# core/agent/handlers.py

import json
from typing import Optional, Any, List, Dict, Tuple
from core.tools.formatters import format_policy_detail, format_training_detail, format_job_bundle
# 내일배움카드
from core.tools.employment24_training import search_training_it
# 정책
from core.tools.youth_policy import search_youth_policies, get_policy_detail
from core.agent.policy_mapper import find_best_policy_by_name
from core.tools.parsers import parse_zip_codes
# 직업
from core.tools.work24_job_info import get_job_list_cached, get_job_profile_bundle_cached
from core.agent.job_mapper import find_job_codes_by_name


# 청년정책 허용 키워드 (plcyKywdNm)
ALLOWED_POLICY_KEYWORDS = {
    "대출", "보조금", "바우처", "금리혜택", "교육지원",
    "맞춤형상담서비스", "인턴", "벤처", "중소기업",
    "청년가장", "장기미취업청년", "공공임대주택",
    "신용회복", "육아", "출산", "해외진출", "주거지원"
}

DEFAULT_POLICY_KEYWORDS = ["교육지원", "인턴", "주거지원"]

# 훈련과정 검색어 확장(사용자 표현 -> 과정명에 잘 들어가는 키워드)
TRAINING_KEYWORD_EXPAND = {
    "sqld": ["SQLD","SQL", "데이터베이스", "DB"],
    "sql": ["SQL", "데이터베이스", "DB"],
    "데이터분석": ["데이터분석", "빅데이터", "파이썬", "SQL"],
    "데이터 분석": ["데이터분석", "빅데이터", "파이썬", "SQL"],
    "파이썬": ["파이썬", "Python", "데이터"],
    "python": ["Python", "파이썬", "데이터"],
    "자바": ["자바", "Java", "스프링"],
    "java": ["Java", "자바", "스프링"],
    "스프링": ["스프링", "Spring", "자바"],
    "웹": ["웹", "프론트엔드", "React", "JavaScript"],
    "프론트엔드": ["프론트엔드", "React", "JavaScript", "웹"],
    "리액트": ["React", "리액트", "프론트엔드"],
    "자바스크립트": ["JavaScript", "자바스크립트", "프론트엔드"],
    "클라우드": ["클라우드", "AWS", "Azure"],
    "aws": ["AWS", "클라우드"],
    "ai" : ["AI", "파이썬", "빅데이터"]
}

IT_TERMS = [
    "it","아이티","소프트웨어","sw","개발","코딩","프로그래밍",
    "ai","인공지능","클라우드","빅데이터","디지털","ict",
    "웹","앱","앱개발","서버","네트워크"
]

JOB_KEYWORD_EXPAND = {
    "it": ["개발", "소프트웨어", "데이터", "클라우드", "네트워크", "보안", "웹", "앱", "ai"],
    "아이티": ["개발", "소프트웨어", "데이터", "클라우드", "네트워크", "보안", "웹", "앱", "ai"],
    "소프트웨어": ["개발", "백엔드", "프론트엔드", "웹", "앱"],
    "개발": ["웹", "백엔드", "프론트엔드", "앱", "서버"],
    "데이터": ["데이터분석", "빅데이터", "ai", "머신러닝", "sql"],
}

def _normalize_kw(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "")

def _candidate_training_keywords(user_kw: str) -> List[str]:
    """
    사용자 입력 키워드 1개를
    - 정규화해서 매핑 테이블에서 후보 키워드 리스트로 바꿔줌
    - 매핑 없으면 원문 그대로 사용
    """
    if not user_kw:
        return []
    nk = _normalize_kw(user_kw)

    # 매핑이 있으면 그걸 우선 사용
    if nk in TRAINING_KEYWORD_EXPAND:
        return TRAINING_KEYWORD_EXPAND[nk]

    # 없으면 원문 그대로(단, 공백은 제거하지 않은 원문도 한번)
    raw = user_kw.strip()
    return [raw]


def _sanitize_policy_keywords(keyword_csv: Optional[str]) -> str:
    """
    LLM이 준 keyword_csv를
    - 허용 키워드만 필터링
    - 전부 제거되면 기본값 적용
    """
    if not keyword_csv:
        return ",".join(DEFAULT_POLICY_KEYWORDS)

    raw = [k.strip() for k in keyword_csv.split(",") if k.strip()]
    filtered = [k for k in raw if k in ALLOWED_POLICY_KEYWORDS]

    if not filtered:
        return ",".join(DEFAULT_POLICY_KEYWORDS)

    # 중복 제거 + 순서 유지
    seen = set()
    unique = []
    for k in filtered:
        if k not in seen:
            unique.append(k)
            seen.add(k)

    return ",".join(unique)

def _is_free_question(text: str) -> bool:
    if not text:
        return False
    t = text.lower().replace(" ", "")
    return any(k in t for k in ["무료", "공짜", "0원", "무상", "전액지원", "본인부담", "자비부담"])

def _is_hiring_question(text: Optional[str]) -> bool:
    if not text:
        return False
    t = text.replace(" ", "")
    return any(k in t for k in ["채용", "구인", "모집", "공고", "일자리", "취업", "연봉협상", "지원하기"])

def _hiring_info_fallback(job_name: Optional[str] = None) -> str:
    # job_name이 있으면 검색 키워드로 활용
    kw = job_name or "직무"
    return (
        "\n\n[채용 정보 안내]\n"
        "현재 이 챗봇은 실시간 채용공고를 직접 조회하는 기능은 아직 없어요.\n"
        "대신 아래 사이트에서 ‘지역=부산’ + 직무 키워드로 검색하면 가장 정확합니다.\n"
        f"- 워크넷: https://www.work.go.kr (검색어 예: 부산 {kw})\n"
        f"- 사람인 / 잡코리아 (검색어 예: 부산 {kw})\n"
        "- 부산일자리정보망: https://www.busan.go.kr/job\n"
    )

def _fallback_keywords(job_name: str) -> List[str]:
    # 아주 간단한 동의어/축약 매핑 (필요하면 계속 추가)
    m = {
        "데이터분석가": ["데이터", "분석", "빅데이터", "데이터 분석"],
        "웹개발자": ["웹", "개발", "프론트엔드", "백엔드"],
        "프론트엔드": ["프론트", "웹", "자바스크립트"],
    }
    key = job_name.replace(" ", "").lower()
    return m.get(key, [])

def _guess_policy_keywords_from_text(text: str) -> str:
    t = (text or "").replace(" ", "")
    if any(k in t for k in ["대출","융자","보증","햇살론","이자","금리"]):
        return "대출,금리혜택,신용회복"
    if any(k in t for k in ["월세","전세","주택","주거","임대"]):
        return "주거지원,공공임대주택,금리혜택"
    if any(k in t for k in ["취업","일자리","인턴","창업","벤처","기업"]):
        return "인턴,벤처,중소기업"
    return "교육지원,인턴,주거지원"

def _is_it_related(it: dict) -> bool:
    text = f"{it.get('plcyNm','')} {it.get('plcyExplnCn','')}".lower()
    # 한글/영문 섞이니까 단순 포함 체크
    return any(term.lower() in text for term in IT_TERMS)

def _policy_region_label(zip_cd_value: Any) -> str:
    codes = parse_zip_codes(zip_cd_value)
    if not codes:
        return "[지역정보 없음]"
    has_busan = any(c.startswith("26") for c in codes)
    only_busan = all(c.startswith("26") for c in codes)

    if only_busan:
        return "[부산 전용]"
    if has_busan:
        return "[전국(부산 포함)]"
    return "[타지역]" # 방어용

def handle_youth_policy_list(keyword_csv: Optional[str]) -> str :
    kw = _sanitize_policy_keywords(keyword_csv)
    items_only = search_youth_policies(keyword_csv=kw, rtn_type="json", busan_mode="only")
    used_include = False
    items = items_only

    if not items:
        items = search_youth_policies(keyword_csv=kw, rtn_type="json", busan_mode="include")
        used_include = True

    if set(kw.split(",")) == {"교육지원", "인턴", "벤처", "중소기업"}:
        it_items = [x for x in items if _is_it_related(x)]
        # 너무 적으면(예: 0~1개) include 모드로 한 번 더 넓혀보기(전국정책이지만 부산 포함)
        if len(it_items) >= 2:
            items = it_items
        # 없으면 그냥 items

        # if not items:
        #     return "청년정책 목록 조회 결과가 없습니다."
    
    header = ""
    if used_include:
        header = "※ 부산 전용 정책이 부족해 ‘전국 정책 중 부산 신청 가능’ 항목까지 함께 보여드려요.\n\n"

    # formatter 수정에 따라 변경
    lines = []    
    for i, it in enumerate(items, 1):
        label = _policy_region_label(it.get("zipCd"))
        lines.append(f"{i}. {label} [{it.get('plcyNo')}] {it.get('plcyNm')} ({it.get('lclsfNm')}/{it.get('mclsfNm')})")

    items_for_llm = []
    for it in items:
        it2 = dict(it)
        z = (it2.get("zipCd") or "")
        # 너무 길면 앞부분만 남기고 축약
        if isinstance(z, str) and len(z) > 80:
            it2["zipCd"] = z[:80] + "...(truncated)"
        items_for_llm.append(it2)
        
    raw = json.dumps(items_for_llm, ensure_ascii=False, indent=2)
    return header + "\n".join(lines) + "\n\n[RAW_JSON]\n" + raw


def handle_youth_policy_detail(plcy_no: Optional[str], user_input: Optional[str] = None) -> str:
    if plcy_no:
        detail = get_policy_detail(plcy_no, rtn_type="json")
        if not detail:
            return "해당 plcyNo로 조회된 상세 정보가 없습니다. 번호를 다시 확인해주세요"
        return format_policy_detail(detail)

    if not user_input:
        return "상세 조회하려면 정책번호(plcyNo) 또는 정책명이 필요합니다!"
    
    q = user_input.strip()

    kw = _guess_policy_keywords_from_text(q)
    items = []
    for pn in range(1, 4):
        items.extend(search_youth_policies(keyword_csv=kw, page_num=pn, page_size=20, rtn_type="json", busan_mode="only") or [])
    
    if not items:
        for pn in range(1, 4):
            items.extend(search_youth_policies(keyword_csv=kw, page_num=pn, page_size=20, rtn_type="json", busan_mode="include") or [])

    cands = find_best_policy_by_name(q, items, top_k=3)

    if not cands:
        return "정책명을 기준으로 후보를 찾지 못했어요. 정책명(정확히)이나 plcyNo를 알려주면 바로 상세로 보여줄게요!"

    # 후보가 여러 개면 사용자에게 선택 요청(UX 개선)
    if len(cands) >= 2:
        lines = ["비슷한 정책이 여러 개 있어요. 번호(plcyNo)를 골라줘!"]
        for i, it in enumerate(cands, 1):
            lines.append(f"{i}. [{it.get('plcyNo')}] {it.get('plcyNm')} ({it.get('lclsfNm')}/{it.get('mclsfNm')})")
        return "\n".join(lines)

    # 4) 1개면 자동 상세
    picked = cands[0]
    detail = get_policy_detail(picked.get("plcyNo"), rtn_type="json")
    if not detail:
        return "해당 plcyNo로 조회된 상세 정보가 없습니다. 번호를 다시 확인해주세요"
    # 핵심 필드만 뽑기 (없는 필드는 None)
    return format_policy_detail(detail)


def handle_training_list(training_keyword: Optional[str]) -> str:
    if _is_free_question(training_keyword):
        return (
            "‘무료 과정’은 내일배움카드 과정에서 보통 이렇게 이해하면 돼요:\n"
            "1) 수강비(훈련비)는 표시되지만, 실제 본인부담금은 카드 유형/취업상태/우대조건에 따라 달라요.\n"
            "2) 그래서 완전 무료(본인부담 0원)인지 여부는 과정 상세 페이지에서 ‘본인부담금/자비부담’ 항목으로 확인해야 정확해요.\n\n"
            "원하는 분야 키워드(예: 파이썬/SQL/웹/자바)를 말해주면 부산 과정 목록을 찾아드릴게요!"
        )

    if not training_keyword or not training_keyword.strip():
        return (
            "내일배움카드 훈련과정을 찾아드릴게요!\n"
            "원하는 IT 분야 키워드만 하나 던져주세요\n"
            "예: 파이썬 / SQLD / 데이터분석 / 웹 / 자바 / 클라우드"
        )

    user_kw = training_keyword.strip()
    nk = _normalize_kw(user_kw)
    is_sqld = nk == "sqld"
    candidates = _candidate_training_keywords(user_kw)

    # 후보 키워드로 순차 검색(최대 3개 정도면 충분)
    all_items: List[Dict[str, Any]] = []
    tried = []
    for kw in candidates[:3]:
        tried.append(kw)
        items = search_training_it(keyword=kw, debug=False) or []
        if isinstance(items, dict):
            items = [items]
        all_items.extend(items)
    

    # 중복 제거(훈련과정명 + 시작일 + 기관명 조합 기준)
    uniq = []
    seen = set()
    for it in all_items:
        key = (
            (it.get("title") or "").strip(),
            (it.get("traStartDate") or "").strip(),
            (it.get("subTitle") or "").strip(),
        )
        if key in seen:
            continue
        seen.add(key)
        uniq.append(it)

    if not uniq:
        return (
            f"'{user_kw}'로는 부산 훈련과정을 확인할 수 없어요\n"
            f"제가 시도한 키워드: {', '.join(tried)}\n"
            "다른 표현으로 다시 말해볼래?\n"
            "예: SQL / 데이터베이스 / 파이썬 / 빅데이터 / 웹 / 자바"
        )

    # 너무 많으면 상위 15개만
    lines = []
    for it in uniq[:15]:
        lines.append(format_training_detail(it))

    lines.append("\n원하시는 과정이 있으면 과정명(또는 링크)을 말해주시면 더 자세히 같이 볼게요!")

    if is_sqld:
        lines.insert(0,
            "참고: ‘SQLD’ 자체를 제목에 포함한 시험 대비 과정은 조회 결과가 없을 수 있어요.\n"
            "아래는 SQL/DB 기초~실무 과정으로 SQLD 준비에 도움이 될 수 있는 과정들이에요."
        )
    return "\n\n".join(lines)


def handle_job_list(job_keyword: Optional[str]) -> Tuple[str, List[Dict[str, Any]]]:
    user_kw = (job_keyword or "개발").strip()
    nk = user_kw.replace(" ", "").lower()

    # 1) IT 같은 포괄 키워드는 확장 검색
    expanded = JOB_KEYWORD_EXPAND.get(nk, [user_kw])

    merged: List[Dict[str, Any]] = []
    seen = set()

    for kw in expanded[:6]:  # 너무 많이 때리면 느려짐. 5~6개면 충분
        items = get_job_list_cached(keyword=kw)
        if not items:
            continue
        for it in items:
            job_cd = it.get("jobCd")
            if not job_cd or job_cd in seen:
                continue
            seen.add(job_cd)
            merged.append(it)

    if not merged:
        # 2) 그래도 없으면 단어 쪼개서 재시도(웹 개발자 -> 웹/개발자)
        parts = [p for p in user_kw.replace("/", " ").split() if len(p) >= 1]
        for p in parts:
            items = get_job_list_cached(keyword=p)
            for it in items or []:
                job_cd = it.get("jobCd")
                if not job_cd or job_cd in seen:
                    continue
                seen.add(job_cd)
                merged.append(it)

    if not merged:
        return f"'{user_kw}'로 검색된 직업이 없습니다.", []

    top = merged[:12]  # IT면 좀 더 보여주는게 UX 좋음
    lines = []

    if nk in JOB_KEYWORD_EXPAND:
        used = ", ".join(expanded[:6])
        lines.append(f"'{user_kw}'는 범위가 넓어서 관련 키워드로 확장해 찾아봤어요: {used}\n")

    for i, it in enumerate(top, 1):
        lines.append(f"{i}. [{it.get('jobCd')}] {it.get('jobNm')} ({it.get('jobClcdNM')})")
    lines.append("\n원하는 번호/직업코드(jobCd)를 말하면 상세를 보여드리겠습니다!")
    return "\n".join(lines), top

def handle_job_detail(job_cd: Optional[str], job_name: Optional[str], user_input:Optional[str]=None) -> str:
    if not job_cd and not job_name:
        return "직업 상세를 보려면 jobCd 또는 직업명을 알려주세요! 예: '웹개발자 상세'"

    # jobCd가 없으면 이름으로 후보 찾기
    if not job_cd and job_name:
        meta = get_job_list_cached(keyword=job_name)  # 가장 간단: 이름으로 한 번 검색
        candidates = find_job_codes_by_name(job_name, meta, top_k=1)
        # 실패할 경우
        if not candidates:
            parts = [p for p in job_name.replace("/", " ").split() if len(p) >= 2]
            for p in parts:
                meta2 = get_job_list_cached(keyword=p)
                candidates = find_job_codes_by_name(job_name, meta2, top_k=1)
                if candidates:
                    break
        # 다시 실패할 경우 fallback 키워드로 검색
        if not candidates:
            for fk in _fallback_keywords(job_name):
                meta3 = get_job_list_cached(keyword=fk)
                candidates = find_job_codes_by_name(job_name, meta3, top_k=1)
                if candidates:
                    break
        # 그래도 실패했다면
        if not candidates:
            return f"'{job_name}'에 해당하는 직업코드를 찾지 못했습니다. 다른 키워드로 검색해보는건 어떨까요?"
        job_cd = candidates[0].get("jobCd")

    bundle = get_job_profile_bundle_cached(jobCd=job_cd, dtlGbs=["1", "2", "3", "4"])
    sections = bundle.get("sections", {})

    job_cd_safe = job_cd or "-"

    result = format_job_bundle(job_cd_safe, sections)

    if _is_hiring_question(user_input):
        result += _hiring_info_fallback(job_name=job_name)

    return result

def handle_hiring_info(hiring_keyword: Optional[str]) -> str:
    kw = (hiring_keyword or "IT").strip()
    return (
        f"[IT 채용정보 찾는 곳]\n"
        f"실시간 공고를 직접 조회하진 못하지만, 아래에서 '부산 + {kw}'로 검색하면 정확해요!\n\n"
        f"1) 부산일자리정보망: https://www.busan.go.kr/job\n"
        f"2) 고용24/워크넷: https://www.work.go.kr\n"
        f"3) 사람인 / 잡코리아: (검색어 예: 부산 {kw})\n"
        f"4) 개발자 특화(원티드/점핏): (검색어 예: 부산 {kw})\n\n"
        f"[검색 꿀팁]\n"
        f"- 키워드 조합 추천: 부산 + (백엔드/프론트/데이터/AI) + (Python/Java/SQL/React)\n"
        f"- 예: '부산 데이터 분석 SQL', '부산 백엔드 Python', '부산 AI MLOps'\n"
    )