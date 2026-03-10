# core/chat/stream.py
# stream
import re
import json
import random
from langchain_core.messages import HumanMessage, SystemMessage
from .memory import maybe_summarize

from core.agent.intent_parser import parse_intent
from core.agent.handlers import handle_youth_policy_list, handle_youth_policy_detail, handle_training_list, handle_job_list, handle_job_detail, handle_hiring_info
from core.utils.cache import find_similar_key, load_cache, save_cache, clean_expired_cache
from core.tools.formatters import is_negative


SYSTEM_TOOL_GUARD = """
너는 부산 청년을 돕는 AI 에이전트 자비스다.

[답변 모드]
- TOOL_MODE: 아래 [도구 결과]가 있는 경우. 도구 결과로만 답하고, 없는 사실은 지어내지 마라.
- CHAT_MODE: 도구 결과가 비어있거나, 사용자가 잡담/일반 질문을 한 경우.
  이때는 일반 상식 수준으로 대화해도 되지만,
  정책/기간/금액/URL/모집공고/규정 같은 사실 데이터는 단정하지 말고
  반드시 "※ 내 판단:" 또는 "일반적으로는" 같은 표현으로 표시해라.
  그리고 대답 끝에는 사용자가 정책이나 교육, 직업 정보에 대한 질문을 할 수 있도록 유도하라.

[규칙]
1) [도구 결과]가 있으면 TOOL_MODE.
2) [도구 결과]가 비어있으면 CHAT_MODE.
3) CHAT_MODE에서 추측/추천/경험치처럼 보일 수 있는 말은 문장 앞에 반드시 "※ 내 판단:"을 붙여라.
4) 사용자가 원하면 확인 방법(검색 키워드/공식 출처)을 함께 제시해라.
[주의] 정책 API는 최신 정책(예: 2026년)이 누락될 수 있다. 도구 결과가 최신이 아닐 수 있음을 사용자에게 안내하라.
""".strip()

ALLOW_SIMILAR_CACHE_INTENTS = {
    "job_detail",
    "youth_policy_detail",
}

BOT_ROLE_MESSAGE = (
    "자비스는 부산 청년 지원 안내 챗봇이예요\n"
    "자비스가 잘하는 건 이 3가지!\n"
    "1) 부산 청년정책(주거/취업/교육/대출/지원금 등) 안내\n"
    "2) 국민내일배움카드(고용24) 훈련과정 조회(부산 지역 한정)\n"
    "3) IT/디지털 관련 직업정보(직업 설명/되는 길/전망 등) 안내\n\n"
    "원하는 건 편하게 이렇게 말해줘:\n"
    "- “부산 주거지원 정책 알려줘”\n"
    "- “내일배움카드 파이썬 교육 찾아줘”\n"
    "- “데이터 분석가 직업 상세 알려줘”\n"
)

OUT_OF_SCOPE_MESSAGE = (
    "자비스는 부산 청년정책/내일배움카드 교육/IT 직업정보 안내에 특화돼 있어요!\n"
    "그 범위를 벗어난 내용은 정확도를 보장하기 어려워요!\n\n"
    "예를 들면 이렇게 물어봐주세요:\n"
    "- 부산 청년 주거지원 정책 알려줘\n"
    "- 내일배움카드 데이터분석 과정 있어?\n"
    "- 데이터 분석가 직업 전망 알려줘"
)

def _stream_text(x: str):
    yield x

def _normalize_chat_text(text: str) -> str:
    # 한글/영문/숫자만 남기고 나머지(!,?,.,이모지 등) 제거
    return re.sub(r"[^0-9a-zA-Z가-힣]+", "", (text or "").strip().lower())

def _is_greeting(text: str) -> bool:
    t = _normalize_chat_text(text)
    return t in ["안녕", "안녕하세요", "하이", "hi", "hello", "ㅎㅇ", "헬로", "반가워", "반가워요", "굿모닝", "굿밤", "좋은아침", "좋은밤"]

def _is_thanks(text: str) -> bool:
    t = _normalize_chat_text(text)
    return any(k in t for k in ["고마워", "감사", "땡큐", "thanks", "thankyou", "ㄱㅅ", "고맙"])

def _is_bot_role_question(text: str) -> bool:
    t = (text or "").replace(" ", "")
    patterns = ["너는무슨일", "너무슨일", "넌무슨일", "너뭐하는", "너정체", "역할", "기능", "할수있는거", "무엇을할수"]
    return any(p in t for p in patterns)

def _to_tool_text(x):
    if x is None:
        return ""
    if isinstance(x, str):
        return x
    # dict/list면 진짜 JSON 문자열로
    try:
        return json.dumps(x, ensure_ascii=False, indent=2)
    except Exception:
        return str(x)

def _strip_raw_json_block(text: str) -> str:
    """
    handle_youth_policy_list()가 붙이는 [RAW_JSON] 블록은
    캐시 저장 시 제외(파일/토큰/용량 절약)
    """
    if not isinstance(text, str) or not text:
        return text
    marker = "\n\n[RAW_JSON]\n"
    if marker in text:
        return text.split(marker, 1)[0]
    return text

def _is_small_talk(text: str) -> bool:
    t = (text or "").strip()
    # 너무 빡세게 말고, 자주 나오는 것만
    return t in ["ㅋㅋ", "ㅋㅋㅋ", "ㅎㅎ", "??", "?", "ㅇㅇ", "ㅇㅋ", "ㄱㅅ", "고마워", "헉", "아", "오키"]

def _is_high_risk(text: str) -> bool:
    """
    의료/법률/투자/자해 등 '섣불리 대답하면 위험'한 범주만 최소 하드가드.
    """
    t = (text or "").replace(" ", "")
    keywords = [
        "자살","자해","죽고싶","우울","공황","불안장애",
        "진단","처방","약","부작용","병원",
        "소송","고소","변호사","법률",
        "코인","주식","투자","레버리지","대출상품추천"
    ]
    return any(k in t for k in keywords)


def get_chat_stream(user_input: str, conversation_history, llm):
    # 디버깅용
    print(f"[USER] {user_input}")
    print(f"[GREET] {_is_greeting(user_input)} | [THANKS] {_is_thanks(user_input)}")

    if _is_greeting(user_input):
        return _stream_text(
            "안녕하세요! 무엇을 도와드릴까요?\n"
            "자비스는 부산 청년정책/내일배움카드 교육/IT 직업정보 안내에 특화돼 있어요!\n"
            "원하는 주제로 편하게 물어봐주세요:\n"
            "- 부산 청년 주거지원 정책 알려줘\n"
            "- 내일배움카드 데이터분석 과정 있어?\n"
            "- 데이터 분석가 직업 전망 알려줘"
        )
    if _is_thanks(user_input):
        return _stream_text("천만에요! 또 궁금한 거 있으면 물어보세요!")   

    if random.random() < 0.05:
        clean_expired_cache(ttl_seconds=86400 * 1)

    maybe_summarize(conversation_history, llm)

    if _is_bot_role_question(user_input):
        return _stream_text(BOT_ROLE_MESSAGE)

    intent_result = parse_intent(user_input, llm)

    print(f"[INTENT] {intent_result.intent} | slots={intent_result.model_dump()}")

    # 범위 밖(=chit_chat) 질문 처리:
    if intent_result.intent == "chit_chat":
        # 1) 고위험만 하드가드
        if _is_high_risk(user_input):
            return _stream_text(
                "이 주제는 내가 섣불리 단정해서 말하면 위험해요…\n"
                "전문 기관/전문가 상담을 추천할게요."
            )

        # 2) 그 외는 CHAT_MODE로 자연스럽게 응답 (도구 결과 없음)
        conversation_history.append(HumanMessage(content=user_input))
        messages = list(conversation_history)

        # 도구 결과를 비워서 CHAT_MODE 유도
        messages.append(SystemMessage(content=f"{SYSTEM_TOOL_GUARD}\n\n[도구 결과]\n"))
        if _is_small_talk(user_input):
            messages.append(SystemMessage(content="CHAT_MODE에서 1~2문장으로 짧고 가볍게 답해라."))
        return llm.stream(messages)

    
    if intent_result.intent == "youth_policy_list":
        if _looks_like_policy_name(user_input) and _wants_detail(user_input):
            intent_result.intent = "youth_policy_detail"
            intent_result.policy_name = user_input.strip()
            intent_result.keyword_csv = None

    m = re.search(r"\b\d{10,25}\b", user_input.replace(" ", ""))
    if m:
        plcy = m.group(0)
        # 정책번호가 들어오면 무조건 상세조회로 보냄
        intent_result.intent = "youth_policy_detail"
        intent_result.plcy_no = plcy

    user_text = user_input.strip()

    # 통합 캐시키 생성(우선순위: job_cd -> plcy_no -> keyword)
    param = (intent_result.job_cd
            or intent_result.plcy_no
            or intent_result.policy_name
            or intent_result.job_keyword
            or intent_result.job_name
            or intent_result.training_keyword
            or intent_result.keyword_csv
            or "general")

    if any(w in user_text for w in ["뭐야", "설명", "알려줘", "자세히", "정보"]) and intent_result.intent == "job_list":
        # 직업명 느낌이면 detail로 강제
        if intent_result.job_keyword and len(intent_result.job_keyword) <= 10:
            intent_result.intent = "job_detail"
            intent_result.job_name = intent_result.job_keyword
            intent_result.job_keyword = None
    
    # override 반영 재계산
    param = (intent_result.job_cd
            or intent_result.plcy_no
            or intent_result.policy_name
            or intent_result.job_keyword
            or intent_result.job_name
            or intent_result.training_keyword
            or intent_result.keyword_csv
            or "general")

    # 공백 제거 및 소문자
    raw_key = f"{intent_result.intent}_{param}".replace(" ", "").strip().lower()

    tool_context = None

    # 먼저 같은 키 조회
    cached = load_cache(raw_key)
    if cached:
        tool_context = cached.get("payload")
        if isinstance(tool_context, str):
            tool_context = _strip_raw_json_block(tool_context)
        print(f"[Cache Hit] exact: {raw_key}")

    # detail intent에 한해서만 유사도 캐시 체크
    if not tool_context and intent_result.intent in ALLOW_SIMILAR_CACHE_INTENTS :
        # prefix 전달
        intent_prefix = f"{intent_result.intent}_"
        similar_key = find_similar_key(raw_key, prefix=intent_prefix, threshold=0.9)

        if similar_key:
            cached2 = load_cache(similar_key)
            if cached2:
                tool_context = cached2.get("payload")

                if isinstance(tool_context, str):
                    tool_context = _strip_raw_json_block(tool_context)
                print(f"[Cache Hit] similar: {similar_key}")

    # use_similarity = intent_result.intent in ALLOW_SIMILAR_CACHE_INTENTS
    # similar_key = None

    # if use_similarity:
    #     similar_key = find_similar_key(
    #         raw_key,
    #         prefix=intent_prefix,
    #         threshold=0.9   # detail은 더 빡세게
    #     )
    # if similar_key :
    #     cached_data = load_cache(similar_key)

    #     if cached_data :
    #         tool_context = cached_data.get("payload")
    #         print(f"[Cache Hit!] 유사 키 발견: {similar_key}")           
    #         # 캐시 데이터가 문자열이 아닐 때 문자열로 변환
    #         if isinstance(tool_context, list):
    #             tool_context = str(tool_context)

    # 캐시 없으면 API 호출
    if not tool_context :
        try :
            print(f"[API Call] '{raw_key}' 신규 요청 발생")
            if intent_result.intent == "job_list":
                result_text, _ = handle_job_list(intent_result.job_keyword)
                tool_context = result_text

            elif intent_result.intent == "job_detail":
                tool_context = handle_job_detail(intent_result.job_cd, intent_result.job_name, user_input=user_input)

            elif intent_result.intent == "youth_policy_list":
                tool_context = handle_youth_policy_list(intent_result.keyword_csv)

            elif intent_result.intent == "youth_policy_detail":
                tool_context = handle_youth_policy_detail(intent_result.plcy_no, user_input=user_input)

            elif intent_result.intent == "hiring_info":
                tool_context = handle_hiring_info(getattr(intent_result, "hiring_keyword", None) or intent_result.job_keyword)

            elif intent_result.intent == "training_list":
                tool_context = handle_training_list(intent_result.training_keyword)

                if any(k in user_input.replace(" ", "") for k in ["교육","훈련","강의","과정","국비","내일배움카드"]):
                    pol = handle_youth_policy_list("교육지원")
                    tool_context = tool_context + "\n\n---\n\n[같이 보면 좋은 청년정책(교육지원)]\n" + pol

            # 새로 가져온 데이터 저장(raw_key로 저장)
            if tool_context and intent_result.intent != "chit_chat":
                cache_payload = tool_context

                cache_payload = _to_tool_text(cache_payload)
                cache_payload = _strip_raw_json_block(cache_payload)

                if intent_result.intent in ["youth_policy_list", "youth_policy_detail"]:
                    save_cache(raw_key, cache_payload)
                else:
                    if not is_negative(cache_payload):
                        save_cache(raw_key, cache_payload)
                    else:
                        print(f"[Skip Cache] 유효하지 않은 결과로 판단되어 캐싱을 건너뜁니다: {raw_key}")
        except Exception as e :
            tool_context = f"죄송합니다. 데이터를 가져오는 중 오류가 발생했습니다 : {str(e)}"

    conversation_history.append(HumanMessage(content=user_input))

    # tool_context를 history에 저장 X 이번 요청에서만 messages 구성(token 초과 방어)
    messages = list(conversation_history)

    tool_context = _to_tool_text(tool_context)

    if tool_context:
        messages.append(SystemMessage(content=f"{SYSTEM_TOOL_GUARD}\n\n[도구 결과]\n{tool_context}"))

    return llm.stream(messages)

    
def _looks_like_policy_name(text: str) -> bool:
    t = (text or "").replace(" ", "")
    return any(k in t for k in [
        "대출","지원금","보조금","사업","보증","바우처","계좌",
        "주거","월세","임대","공공임대","주택","공공교육",
        "교육지원"   # ← 정책 키워드로 명확한 것만 유지
    ])
    
def _wants_detail(user_text: str) -> bool:
    t = (user_text or "").replace(" ", "")
    return any(k in t for k in ["자세히","상세","알려줘","정보","어떻게","신청"])


