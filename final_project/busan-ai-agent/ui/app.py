# ui/app_nari.py
import os
import re
import pandas as pd
import streamlit as st
from PIL import Image
import streamlit.components.v1 as components
from streamlit_option_menu import option_menu 
import altair as alt
import base64
from typing import List, Dict
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from core.chat.llm import get_llm
from core.chat.stream import get_chat_stream
from ui.components.chat_ui import render_history
from core.tools.work24_job_info import (
    search_job_list,
    get_job_list_cached,
)

img = Image.open("ui/image/favicon.png")

# k = os.getenv("WORK24_AUTH_KEY_JOBINFO")
# print("KEY:", repr(k))
# print("LEN:", None if k is None else len(k))

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(page_title="JOBIT's", page_icon=img, layout="wide")

# 전역 상수(차트 높이)
CHART_H = 360

# Tailwind CSS CDN (스타일은 styles.css에서 전역 적용)
st.markdown(
    "<script src=\"https://cdn.tailwindcss.com\"></script>",
    unsafe_allow_html=True,
)

# 전역 스타일 (별도 파일 로드) - 여러 경로 시도
def _load_styles():
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "styles.css"),
        os.path.join(os.getcwd(), "styles.css"),
        os.path.join(os.getcwd(), "busan-ai-agent", "styles.css"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception:
                return None
    return None

_css_content = _load_styles()
if _css_content:
    st.markdown(f"<style>{_css_content}</style>", unsafe_allow_html=True)
# else: styles.css 없으면 스타일 미적용 (경로 확인 필요)

# 부트스트랩 아이콘 (option_menu 아이콘용)
st.markdown(
    "<link rel=\"stylesheet\" href=\"https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css\">",
    unsafe_allow_html=True,
)
st.markdown("<div id=\"page-top\"></div>", unsafe_allow_html=True)


def img_to_base64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# -----------------------------
# 세션 초기화
# -----------------------------
def init_session():

    #  적성검사 결과(성향, 점수, 키워드)
    if "profile" not in st.session_state:
        st.session_state["profile"] = None

    # 적성검사로부터 생성된 검색 키워드
    if "search_keywords" not in st.session_state:
        st.session_state["search_keywords"] = []

    #  직업 목록 조회 결과(top N)
    if "jobs_top" not in st.session_state:
        st.session_state["jobs_top"] = None

    # 성향 → 직업 키워드 룰(1회 생성 후 재사용)
    if "keyword_rules" not in st.session_state:
        st.session_state["keyword_rules"] = None
    
    # 디버그 원본 저장용 세션 키
    if "job_api_raw" not in st.session_state:
        st.session_state["job_api_raw"] = None
    if "job_api_status" not in st.session_state:
        st.session_state["job_api_status"] = None
    if "job_api_url" not in st.session_state:
        st.session_state["job_api_url"] = None

    # ✅ 성향 점수 표/차트 캐시(깜박임 방지)
    if "trait_scores_df" not in st.session_state:
        st.session_state["trait_scores_df"] = None
    if "trait_scores_chart" not in st.session_state:
        st.session_state["trait_scores_chart"] = None

init_session()

# -----------------------------
# 키워드 룰 생성 함수
# -----------------------------
def build_keyword_rules_from_api(force_refresh: bool = False) -> Dict[str, List[str]]:
    """
    직업정보 API로 키워드를 자동 생성(초안).
    - 각 성향별로 대표 검색어를 정해 직업 목록을 조회
    - 결과의 jobNm / jobClcdNM에서 토큰을 뽑아 상위 키워드로 구성
    """
    trait_query_map = {
        "논리형": "데이터",        # 데이터분석가, 데이터엔지니어
        "직관형": "기획",          # 서비스기획자, IT기획자
        "집중형": "개발",          # 백엔드개발자, 프론트엔드개발자
        "협업형": "프로젝트",      # PM, IT프로젝트관리자
        "내향형": "백엔드",        # 서버개발자, 시스템개발자
        "외향형": "프론트엔드",    # 프론트엔드개발자, UX개발
        "안정형": "시스템",        # 시스템관리자, 인프라엔지니어
        "도전형": "AI",            # AI엔지니어, 머신러닝엔지니어
        "성과형": "클라우드",      # 클라우드엔지니어, DevOps
        "보상형": "보안",          # 정보보안전문가
    }

    rules: Dict[str, List[str]] = {}
    for trait, q in trait_query_map.items():
        try:
            jobs = get_job_list_cached(
                srchType="K",
                keyword=q,
                ttl_seconds=60 * 60 * 24,
                force_refresh=force_refresh,
            )

        except Exception:
            jobs = []  # 키가 없거나 API 실패 시 빈 리스트 처리

        tokens: List[str] = []
        for r in jobs[:50]:
            text = f"{r.get('jobNm','')} {r.get('jobClcdNM', '')}"
            for t in text.replace("/", " ").replace("·", " ").split():
                if len(t) >= 2:
                    tokens.append(t)

        # 중복 제거 + 상위 n개만(초안)
        uniq: List[str] = []
        for t in tokens:
            if t not in uniq:
                uniq.append(t)

        rules[trait] = uniq[:10] if uniq else [q]

    return rules

# 적성 결과 → 검색 키워드 매핑
def keywords_from_result_types(
    result_types: List[str],
    rules: Dict[str, List[str]],
) -> List[str]:
    """
    [역할]
    적성검사 결과 타입(result_types)을 바탕으로
    1) 기본 IT 직종 키워드(IT_JOB_KEYWORDS_BY_TRAIT)
    2) API 기반 자동 생성 키워드(rules)
    를 합쳐 최종 검색 키워드 리스트를 만든다.

    [처리 규칙]
    - 중복 제거(먼저 나온 키워드 우선)
    - 빈값(None/공백) 제거
    - 최대 12개까지만 반환
    """
    kws: List[str] = []

    # 1) 성향별 기본 키워드
    for t in result_types:
        kws.extend(IT_JOB_KEYWORDS_BY_TRAIT.get(t, []))

    # 2) API 기반 키워드 룰
    for t in result_types:
        kws.extend(rules.get(t, []))

    # 3) 중복 제거 + 빈값 제거 + 길이 제한
    out: List[str] = []
    for k in kws:
        k = (k or "").strip()
        if k and k not in out:
            out.append(k)

    return out[:12]


# 직업 검색어 정규화(괄호/특수문자 제거)로 검색 실패(0건) 방지
def normalize_keyword(s: str) -> str:
    s = (s or "").strip()
    # 괄호 내용 제거: "데이터분석가(빅데이터분석가)" -> "데이터분석가"
    s = re.sub(r"\(.*?\)", "", s)
    # 특수기호 정리(필요시 확장 가능)
    s = s.replace("·", " ").replace("/", " ")
    s = re.sub(r"\s+", " ", s).strip()
    return s


# -----------------------------
# IT 직종 키워드 매핑
# (적성 결과 → 고용24 IT 직종 키워드)
# -----------------------------
IT_JOB_KEYWORDS_BY_TRAIT = {
    # 분석·논리 중심
    "논리형": [
        "데이터 시스템 전문가",
        "데이터 설계 및 프로그래머",
        "데이터베이스 운영·관리자",
        "데이터 분석가",
        "빅데이터 분석가",
    ],

    # 아이디어·설계 중심
    "직관형": [
        "컴퓨터시스템 설계 및 분석가",
        "IT 컨설턴트",
        "웹 기획자",
        "IT 감리 전문가",
    ],

    # 혼자 깊게 파는 개발 성향
    "집중형": [
        "시스템 소프트웨어 개발자",
        "시스템 소프트웨어 개발자(프로그래머)",
        "펌웨어 및 임베디드 소프트웨어 프로그래머",
        "응용 소프트웨어 개발자",
        "프로그래머",
    ],

    # 사람·조율·관리 성향
    "협업형": [
        "IT 컨설턴트",
        "컴퓨터시스템 전문가",
        "IT 감리 전문가",
        "프로젝트 관리",
    ],

    # 서버·인프라·운영 선호
    "내향형": [
        "시스템 소프트웨어 개발자",
        "네트워크 시스템 개발자",
        "정보시스템 운영자",
        "네트워크 관리자",
    ],

    # 사용자·서비스 접점 선호
    "외향형": [
        "웹 개발자",
        "웹 개발자(웹 엔지니어·웹 프로그래머)",
        "모바일 애플리케이션 프로그래머",
        "웹 기획자",
        "IT 기술지원 전문가",
    ],

    # 안정·유지·관리 성향
    "안정형": [
        "정보시스템 운영자",
        "네트워크 관리자",
        "웹 운영자",
        "IT 기술지원 전문가",
    ],

    # 신기술·위험 감수 성향
    "도전형": [
        "정보보안 전문가",
        "정보보호 전문가",
        "침해사고 대응 전문가",
        "디지털 포렌식 전문가",
        "AI",
    ],

    # 성과·시장 가치 중시
    "성과형": [
        "클라우드",
        "네트워크 시스템 개발자",
        "정보보안 전문가",
        "데이터 분석가",
    ],

    # 보상·연봉 중시
    "보상형": [
        "IT 컨설턴트",
        "클라우드",
        "보안",
        "데이터",
    ],
}


# -----------------------------
# keyword_rules 1회 생성 보장
# -----------------------------
if st.session_state["keyword_rules"] is None:
    with st.spinner("직업 키워드 룰 생성 중..."):
        st.session_state["keyword_rules"] = build_keyword_rules_from_api(force_refresh=False)


# -----------------------------
# Hero section
# -----------------------------
banner_b64 = img_to_base64("ui/image/jobits.png")
chatbot_icon_b64 = img_to_base64("ui/image/chatbot.png")  # 파일명 맞추기

st.markdown(
    f"""
    <section class="hero" aria-label="JOBIT 소개">
        <div class="hero-inner">
            <div class="hero-visual">
                <img src="data:image/png;base64,{banner_b64}" class="hero-img" alt="JOBIT" />
            </div>
            <div class="hero-content">
                <span class="hero-tagline">
                    너한테 딱 맞는 IT Job-있어! 청년과 IT 일자리를 잇는
                    <span class="hero-title">JOBIT's</span>   
                </span>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Top Menu (세션값 기반 default_index)
# -----------------------------
MENU_OPTIONS = ["적성검사·직업추천", "JOBIT's Chatbot(챗봇)"]

if "main_menu" not in st.session_state:
    st.session_state["main_menu"] = MENU_OPTIONS[0]   # 최초만 적성검사

# 현재 선택값으로 default_index 계산 (rerun에도 유지)
_current = st.session_state.get("main_menu", MENU_OPTIONS[0])
_default_index = MENU_OPTIONS.index(_current) if _current in MENU_OPTIONS else 0

# 탭 메뉴: 배너와 동일한 폭(block-container 전체)으로 표시
menu = option_menu(
    menu_title=None,
    options=MENU_OPTIONS,
    icons=["clipboard-check", "robot"],
    orientation="horizontal",
    key="main_menu",
    default_index=_default_index,
    styles={
        "container": {
            "padding": "8px 12px",
            "background": "linear-gradient(135deg, #1e5bb8 0%, #164a9a 100%)",
            "border": "none",
            "border-radius": "12px",
            "box-shadow": "0 4px 14px 0 rgba(30, 91, 184, 0.3)",
            "justify-content": "center",
        },
        "nav-link": {
            "height": "56px",
            "font-size": "1.1rem",
            "font-weight": "600",
            "padding": "12px 28px",
            "margin": "0 6px",
            "border-radius": "8px",
            "color": "rgba(255,255,255,0.9)",
            "background-color": "transparent",
            "align-items": "center",
            "justify-content": "center",
        },
        "nav-link-selected": {
            "background-color": "rgba(255,255,255,0.2)",
            "color": "#ffffff",
            "border-radius": "8px",
        },
        "icon": {"font-size": "1.2rem"},
    },
)


# -----------------------------
# footer
# -----------------------------
GROUP_ORDER = [
    "청년 정책·지원 정보 사이트",
    "공공 채용정보 사이트",
    "부산 지역 채용정보 사이트",
    "민간 채용정보 사이트",
    "IT 직무 특화 채용 플랫폼",
]

URL_DATA = [
    ("공공 채용정보 사이트", "고용24/워크넷", "https://www.work24.go.kr",
     "고용노동부에서 운영하는 공공 취업·직업 정보 통합 플랫폼"),
    ("부산 지역 채용정보 사이트", "부산일자리정보망", "https://www.busanjob.net/",
     "부산 지역 맞춤 채용 정보와 취업 지원 서비스를 제공하는 공식 포털"),
    ("청년 정책·지원 정보 사이트", "온통청년", "https://www.youthcenter.go.kr/",
     "청년을 위한 정책, 일자리, 주거, 복지 정보를 한곳에 모은 정부 플랫폼"),
    ("청년 정책·지원 정보 사이트", "부산청년플랫폼 청년G대", "https://young.busan.go.kr/",
     "부산 청년 대상 정책, 프로그램, 일자리 정보를 제공하는 지역 특화 플랫폼"),
    ("민간 채용정보 사이트", "사람인", "https://www.saramin.co.kr/",
     "다양한 기업의 채용 공고와 직무·기업 정보를 제공하는 대표 채용 플랫폼"),
    ("민간 채용정보 사이트", "잡코리아", "https://www.jobkorea.co.kr/",
     "신입·경력 채용부터 기업 분석까지 제공하는 종합 취업 포털"),
    ("IT 직무 특화 채용 플랫폼", "원티드", "https://www.wanted.co.kr/",
     "IT·스타트업 중심의 추천 기반 채용 및 커리어 플랫폼"),
    ("IT 직무 특화 채용 플랫폼", "점핏", "https://jumpit.saramin.co.kr/",
     "개발자·IT 직군 특화 채용 정보를 제공하는 전문 플랫폼")
]

def render_reference_footer(tab_id: str):
    st.divider()

    st.caption("관심 있는 직무와 조건에 맞는 채용 정보·청년 정책을 아래 링크 또는 챗봇 안내를 통해 바로 확인해 보세요!")

    with st.expander("🔗 참고 사이트", expanded=False):
        category = st.selectbox(
            "구분 선택",
            ["전체"] + GROUP_ORDER,
            key=f"{tab_id}_footer_category"
        )

        prev_group = None

        for group, name, url, desc in sorted(URL_DATA, key=lambda x: GROUP_ORDER.index(x[0])):
            if category != "전체" and group != category:
                continue
            
            # group이 바뀔 때만 소제목 출력
            if group != prev_group:
                st.markdown(
                    f"<div style='font-weight:600; font-size:1.05rem; margin-top:0.6rem;'>{group}</div>",
                    unsafe_allow_html=True
                )

                prev_group = group

            st.markdown(
                f"- **[{name}]({url})**  \n"
                f"  <span style='color:gray; font-size:0.85rem;'>{desc}</span>",
                unsafe_allow_html=True
            )


# -----------------------------
# 챗봇에 직업 추천 목록 불러오기
# -----------------------------
def render_job_summary_on_chat():
    """
    목적:
    -   적성검사·직업추천에서 조회한 '추천 직업 목록'을
        챗봇 상단에서도 그대로 재사용
    -   키워드는 제외, 직업 목록만 표시
    """
        
    jobs_top = st.session_state.get("jobs_top")

    st.subheader("📌 추천 IT 직업 목록")
    st.caption("해당 직업정보는 적성검사 결과와 연동됩니다. 나에게 맞는 추천 직업에 대해 챗봇에게 물어보세요.")

    # 직업 목록
    if jobs_top:
        view_df = pd.DataFrame(jobs_top)

        cols = [ c for c in ["jobClcdNM", "jobNm"] if c in view_df.columns]
        view_df = view_df[cols].copy()
        view_df.rename(columns={"jobClcdNM": "직종(분류)", "jobNm": "직업명"}, inplace=True)

        st.dataframe(view_df, use_container_width=True, hide_index=True)
    else:
        st.info("직업 목록 조회 결과가 없습니다. (위의 ‘적성검사·직업추천’에서 적성검사를 완료한 뒤, 직업정보 추천까지 받아주세요.)")
# -----------------------------
# 1) 적성검사
# -----------------------------
menu = st.session_state["main_menu"]

if menu ==  "적성검사·직업추천":
    # IT 적성검사·expander 폭 = 위 타이틀·탭과 동일(전체 block-container)
    st.title("📝 IT 적성검사")
    st.caption("검사 완료 후 생성된 키워드로 직업정보 조회 화면과 연결됩니다.")

    # ① 문제 접근 방식 (논리형 ↔ 직관형)
    with st.expander("(Q1~Q4) 문제 접근 방식 ", expanded=True):
        q1 = st.radio("Q1. 새로운 일을 맡으면 먼저?", ["전체 구조와 규칙부터 파악한다", "직접 해보며 감을 잡는다"], index=None)
        q2 = st.radio("Q2. 답을 찾는 방식은?", ["원인·결과를 분석하는 것", "아이디어를 떠올리는 것"], index=None)
        q3 = st.radio("Q3. 설명서를 보면?", ["처음부터 끝까지 읽는다", "필요한 부분만 본다"], index=None)
        q4 = st.radio("Q4. 더 편한 문제 유형은?", ["정답이 하나인 문제", "여러 답이 가능한 문제"], index=None)

    # ② 작업 스타일 (집중형 ↔ 협업형)
    with st.expander("(Q5~Q8) 작업 스타일 ", expanded=False):
        q5 = st.radio("Q5. 일할 때 더 편한 환경은?", ["조용히 혼자", "사람들과 함께"], index=None)
        q6 = st.radio("Q6. 팀 프로젝트에서 주로?", ["맡은 파트를 책임지고 해결", "의견 조율과 분위기 관리"], index=None)
        q7 = st.radio("Q7. 회의가 많아지면?", ["피곤해진다", "오히려 에너지가 난다"], index=None)
        q8 = st.radio("Q8. 더 힘든 상황은?", ["지시 없이 혼자 판단", "계속 소통해야 하는 상황"], index=None)

    # ③ 에너지 방향 (내향형 ↔ 외향형)
    with st.expander("(Q9~Q12) 에너지 방향 ", expanded=False):
        q9 = st.radio("Q9. 쉬는 방법은?", ["집에서 혼자", "사람 만남"], index=None)
        q10 = st.radio("Q10. 발표나 모임 후 느낌은?", ["에너지가 소모된다", "에너지가 충전된다"], index=None)
        q11 = st.radio("Q11. 갑작스러운 모임 제안이 오면?", ["부담스럽다", "기대된다"], index=None)
        q12 = st.radio("Q12. 집중이 잘 되는 장소는?", ["혼자 있는 공간", "사람 있는 공간"], index=None)

    # ④ 위험 선호 (안정형 ↔ 도전형)
    with st.expander("(Q13~Q16) 위험 선호 ", expanded=False):
        q13 = st.radio("Q13. 선택해야 한다면?", ["안정적인 일", "성장 가능성 큰 기회"], index=None)
        q14 = st.radio("Q14. 실패 가능성이 있다면?", ["피하고 싶다", "도전해보고 싶다"], index=None)
        q15 = st.radio("Q15. 새로운 환경은?", ["적응이 느린 편", "금방 적응한다"], index=None)
        q16 = st.radio("Q16. 미래를 생각하면?", ["불안이 크다", "설렘이 크다"], index=None)

    # ⑤ 보상 기준 (성과형 ↔ 보상형)
    with st.expander("(Q17~Q20) 보상 기준", expanded=False):
        q17 = st.radio("Q17. 더 중요한 것은?", ["내가 잘했다는 느낌", "눈에 보이는 보상"], index=None)
        q18 = st.radio("Q18. 야근을 한다면?", ["의미 있는 일이면 가능", "보상이 있어야 가능"], index=None)
        q19 = st.radio("Q19. 성공의 기준은?", ["성취 경험", "연봉·직급"], index=None)
        q20 = st.radio("Q20. 둘 중 하나를 고른다면?", ["재미있지만 연봉이 낮음", "힘들지만 연봉이 높음"], index=None)

    st.markdown('<div class="aptitude-result-actions-marker" data-buttons="save-reset"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        run_test = st.button("검사 결과 저장", use_container_width=True, key="btn_save_result")
    with col2:
        reset_test = st.button("검사 결과 초기화", use_container_width=True, key="btn_reset_result")

    # 초기화
    if reset_test:
        st.session_state["profile"] = None
        st.session_state["search_keywords"] = []
        st.session_state["jobs_top"] = None
        st.session_state["keyword_rules"] = None
        st.session_state["trait_scores_df"] = None
        st.session_state["trait_scores_chart"] = None

        # ✅ 초기화 후 다시 1회 생성 보장
        with st.spinner("직업 키워드 룰 재생성 중..."):
            st.session_state["keyword_rules"] = build_keyword_rules_from_api(force_refresh=False)

        st.success("초기화 완료")

    # 저장
    if run_test:
        st.session_state["trait_scores_chart"] = None
        answers = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10, q11, q12, q13, q14, q15, q16, q17, q18, q19, q20]
        if any(a is None for a in answers):
            st.warning("모든 문항(Q1~Q20)에 답해주세요.")
            st.stop()

        scores = {
            "논리형": 0, "직관형": 0,
            "집중형": 0, "협업형": 0,
            "내향형": 0, "외향형": 0,
            "안정형": 0, "도전형": 0,
                "성과형": 0, "보상형": 0,
        }

        qa_map = [
            (q1, "전체 구조와 규칙부터 파악한다", "논리형", "직관형"),
            (q2, "원인·결과를 분석하는 것", "논리형", "직관형"),
            (q3, "처음부터 끝까지 읽는다", "논리형", "직관형"),
            (q4, "정답이 하나인 문제", "논리형", "직관형"),

            (q5, "조용히 혼자", "집중형", "협업형"),
            (q6, "맡은 파트를 책임지고 해결", "집중형", "협업형"),
            (q7, "피곤해진다", "집중형", "협업형"),
            (q8, "지시 없이 혼자 판단", "집중형", "협업형"),

            (q9, "집에서 혼자", "내향형", "외향형"),
            (q10, "에너지가 소모된다", "내향형", "외향형"),
            (q11, "부담스럽다", "내향형", "외향형"),
            (q12, "혼자 있는 공간", "내향형", "외향형"),

            (q13, "안정적인 일", "안정형", "도전형"),
            (q14, "피하고 싶다", "안정형", "도전형"),
            (q15, "적응이 느린 편", "안정형", "도전형"),
            (q16, "불안이 크다", "안정형", "도전형"),

            (q17, "내가 잘했다는 느낌", "성과형", "보상형"),
            (q18, "의미 있는 일이면 가능", "성과형", "보상형"),
            (q19, "성취 경험", "성과형", "보상형"),
                (q20, "재미있지만 연봉이 낮음", "성과형", "보상형"),
        ]

        for answer, a_text, left_type, right_type in qa_map:
            if answer == a_text:
                scores[left_type] += 1
            else:
                scores[right_type] += 1

        result_types = []
        result_types.append("논리형" if scores["논리형"] >= scores["직관형"] else "직관형")
        result_types.append("집중형" if scores["집중형"] >= scores["협업형"] else "협업형")
        result_types.append("내향형" if scores["내향형"] >= scores["외향형"] else "외향형")
        result_types.append("안정형" if scores["안정형"] >= scores["도전형"] else "도전형")
        result_types.append("성과형" if scores["성과형"] >= scores["보상형"] else "보상형")

        # 생성하지 않고 "있는 룰"을 사용만 함
        KEYWORD_RULES = st.session_state["keyword_rules"]
        keywords = keywords_from_result_types(result_types, KEYWORD_RULES)

        profile = {"types": result_types, "scores": scores, "keywords": keywords}
        st.session_state["profile"] = profile
        st.session_state["search_keywords"] = keywords
        st.success("검사 결과가 저장되었습니다.")

        # 점수 DF/차트는 여기서 1회 생성 후 세션에 저장(깜박임 방지)
        df_scores = pd.DataFrame({
            "성향": list(scores.keys()),
            "점수": list(scores.values()),
        })

        dominant = set(result_types)
        df_scores["우세"] = df_scores["성향"].apply(lambda x: x in dominant)

        chart = (
            alt.Chart(df_scores)
            .mark_bar()
            .encode(
                x=alt.X("성향:N", sort=None, axis=alt.Axis(labelAngle=0, labelPadding=8, labelLimit=120)),
                y=alt.Y("점수:Q"),
                color=alt.condition(
                    alt.datum.우세,
                    alt.value("#FF0000"),
                    alt.value("#90CAF9")
                ),
                tooltip=["성향", "점수"]
            )
            .properties(height=CHART_H, width="container")
            .configure_view(stroke=None)
        )

        st.session_state["trait_scores_df"] = df_scores
        st.session_state["trait_scores_chart"] = chart

    # 저장 여부와 상관없이, profile이 있으면 항상 출력
    profile = st.session_state.get("profile")
    if profile:
        st.caption("본 테스트는 IT 직무 탐색을 위한 간이 검사입니다. 보다 정확한 역량 수준과 적합 직무 판단을 위해서는 고용24-[IT직무 기본역량검사](https://www.work.go.kr/consltJobCarpa/jobPsyExam/aduItCapaDetail.do)와의 병행 활용을 권장합니다.")
        st.subheader("🔎 성향 결과")
        st.info(", ".join(profile["types"]))

        st.subheader("🧩 추천 IT 직업군(검색 키워드)")
        st.info(", ".join(profile["keywords"]))

        st.subheader("📌 성향 점수 상세")

        chart = st.session_state.get("trait_scores_chart")

        # ✅ profile은 있는데 chart 캐시가 비어있으면 1회 재생성
        if chart is None and profile:
            scores = profile["scores"]
            result_types = profile["types"]

            df_scores = pd.DataFrame({
                "성향": list(scores.keys()),
                "점수": list(scores.values()),
            })
            dominant = set(result_types)
            df_scores["우세"] = df_scores["성향"].apply(lambda x: x in dominant)

            chart = (
                alt.Chart(df_scores)
                .mark_bar()
                .encode(
                    x=alt.X(
                        "성향:N",
                        sort=None,
                        axis=alt.Axis(labelAngle=0, labelPadding=8, labelLimit=120)  # (선택) 라벨 겹침 완화
                    ),
                    y=alt.Y("점수:Q"),
                    color=alt.condition(
                        alt.datum.우세,
                        alt.value("#FF0000"),
                        alt.value("#90CAF9")
                    ),
                    tooltip=["성향", "점수"]
                )
                .properties(height=CHART_H, width="container")
                .configure_view(stroke=None)
            )

            st.session_state["trait_scores_df"] = df_scores
            st.session_state["trait_scores_chart"] = chart

        # 렌더링
        if chart is not None:
            st.altair_chart(chart,use_container_width=True)
        else:
            st.info("검사 결과 저장 후 점수 차트가 생성됩니다.")

    # -----------------------------
    # 2) 직업정보 추천(적성검사 연동)
    # -----------------------------
    st.divider()
    st.subheader("💼 IT 직업정보 추천")
    st.caption("해당 직업정보는 첫번째 적성검사 결과와 연동됩니다. 직업 목록 조회를 눌러 상세한 직업명을 확인해 보세요!")

    # ✅ 디버그 모드일 때만 표시
    DEBUG_UI = os.getenv("DEBUG_UI", "0") == "1"

    if DEBUG_UI:
        with st.expander("직업 정보 API 원본 확인(디버그)"):
            raw = st.session_state.get("job_api_raw")
            status = st.session_state.get("job_api_status")
            url = st.session_state.get("job_api_url")

            if not raw:
                st.caption("직업 목록 조회를 실행하면 여기에서 API 원본(XML/Raw)이 표시됩니다.")
            else:
                st.write("HTTP 상태:", status)
                st.write("요청 URL:", url)
                st.code(raw, language="xml")

    profile = st.session_state.get("profile")
    keywords = st.session_state.get("search_keywords", [])

    if not profile or not keywords:
        st.warning("적성검사를 먼저 완료해주세요.")
    else:
        run_search = False
        with st.form("job_search_form"):
            colA, colB = st.columns([2, 1])
            with colA:
                query = st.text_input(
                    "직업 검색어",
                    value=keywords[0],
                    key="job_query"
                )
            with colB:
                top_n = st.number_input(
                    "추천 개수",
                    min_value=5,
                    max_value=30,
                    value=10,
                    step=5,
                    key="job_top_n"
                )

            run_search = st.form_submit_button(
                "직업 목록 조회",
                use_container_width=True
            )

        # 2-1) 목록 조회 버튼 클릭 시: 결과를 세션에 저장
        if run_search:
            with st.spinner("직업 목록 조회 중..."):
                try:
                    raw_query = query
                    norm_query = normalize_keyword(raw_query) # 수정 및 추가: 검색어 정규화 적용

                    try:
                        dbg = search_job_list(
                            srchType="K",
                            keyword=norm_query if norm_query else None,
                            debug=True
                        )

                        st.session_state["job_api_raw"] = (
                            dbg.get("raw") or dbg.get("text") or dbg.get("response") or str(dbg)
                        )

                        st.session_state["job_api_status"] = dbg.get("status")
                        st.session_state["job_api_url"] = dbg.get("url")

                    except Exception as _:
                        # 원본 저장 실패해도 목록 조회는 계속 진행
                        st.session_state["job_api_raw"] = None
                        st.session_state["job_api_status"] = None
                        st.session_state["job_api_url"] = None

                    # 1차: 정규화 키워드로 조회
                    jobs = get_job_list_cached(
                        srchType="K",
                        keyword=norm_query if norm_query else None,
                        ttl_seconds=60 * 60 * 24,
                    )

                    # 2차: 폴백(0건이면 더 넓게)
                    if not jobs and norm_query:
                        fallback = norm_query[:2]
                        jobs = get_job_list_cached(
                            srchType="K",
                            keyword=fallback,
                            ttl_seconds=60*60*24,
                        )

                    if not jobs:
                        st.warning("조회 결과가 없습니다.")
                        st.session_state["jobs_top"] = None
                        st.stop()

                    def calc_score(row: dict, kws: List[str]) -> int:
                        text = f"{row.get('jobNm','')} {row.get('jobClcdNM','')}"
                        return sum(1 for k in kws if k and k in text)

                    for r in jobs:
                        r["match_score"] = calc_score(r, keywords)

                    jobs_sorted = sorted(
                        jobs,
                        key=lambda x: (x.get("match_score", 0), x.get("jobNm", "")),
                        reverse=True,
                    )
                    jobs_top = jobs_sorted[: int(top_n)]

                    # ✅ 세션에 저장(상세 조회용)
                    st.session_state["jobs_top"] = jobs_top

                except Exception as e:
                    st.error(f"직업 목록 조회 실패: {e}")
                    st.session_state["jobs_top"] = None
                    st.stop()

        # 2-2) 세션에 목록이 있으면 항상 렌더링(버튼 rerun 대비)
        jobs_top = st.session_state.get("jobs_top")
        if jobs_top:
            st.success(f"추천 목록 {len(jobs_top)}건")

            view_df = pd.DataFrame(jobs_top)

            cols = [c for c in ["jobClcdNM", "jobNm"] if c in view_df.columns]
            view_df = view_df[cols].copy()

            view_df.rename(columns={"jobClcdNM": "직종(분류)", "jobNm": "직업명"}, inplace=True)
            st.dataframe(view_df, use_container_width=True, hide_index=True,)

        else:
            st.info("직업 목록 조회를 실행하면 추천 목록이 표시됩니다.")

    render_reference_footer("tab1")


# -----------------------------
# 2) 챗봇 (폭 = 타이틀·탭과 동일)
# -----------------------------
elif menu == "JOBIT's Chatbot(챗봇)":
    render_job_summary_on_chat()
    st.divider()
    st.markdown(
        f"""
            <div style="
                display: flex; 
                align-items: center; 
                gap: 12px;
            ">
                <img src="data:image/png;base64,{chatbot_icon_b64}"
                    style="
                        width: 55px; 
                        height: 55px; 
                        flex-shrink: 0;
                        margin-top: 7px;
                ">
                <h1 style="
                    font-size: 44px !important;
                    font-weight: 800 !important;
                    white-space: nowrap !important;
                    line-height: 1.15 !important;
                    display: inline-flex !important;
                ">
                    JOBIT's Chatbot
                </h1>
            </div>
            """,
            unsafe_allow_html=True
    )
    st.caption("JOBIT's에게 부산 청년을 위한 IT 직업 정보, 교육, 정책을 자유롭게 질문해 보세요.")

    # 세션 키 충돌 방지(prefix 적용)
    if "hs_conversation_history" not in st.session_state:
        st.session_state["hs_conversation_history"] = [SystemMessage(content="You are a helpful assistant")]

    if "hs_ui_history" not in st.session_state:
        st.session_state["hs_ui_history"] = []

    if "hs_pending_prompt" not in st.session_state:
        st.session_state["hs_pending_prompt"] = ""

    conversation_history = st.session_state["hs_conversation_history"]
    ui_history = st.session_state["hs_ui_history"]

    llm = get_llm(model="gpt-4o", temperature=0)

    chat_container = render_history(ui_history)

    # pending_prompt 처리
    if st.session_state.get("hs_pending_prompt"):
        prompt = st.session_state["hs_pending_prompt"]
        st.session_state["hs_pending_prompt"] = ""

        ui_history.append(HumanMessage(content=prompt))

        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                stream = get_chat_stream(prompt, conversation_history, llm)
                result = st.write_stream(stream)

        ui_history.append(AIMessage(content=result))
        conversation_history.append(AIMessage(content=result))

    # 채팅 입력 폼
    with st.form("Chatbot_HS", clear_on_submit=True):
        prompt = st.text_input("질문 후 확인 버튼을 눌러주세요")
        chat_submit = st.form_submit_button("확인")

    if chat_submit and prompt:
        ui_history.append(HumanMessage(content=prompt))

        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
            with st.chat_message("assistant"):
                stream = get_chat_stream(prompt, conversation_history, llm)
                result = st.write_stream(stream)

        ui_history.append(AIMessage(content=result))
        conversation_history.append(AIMessage(content=result))

    render_reference_footer("tab2")

# ---------------------------------------
# TOP 버튼
# ---------------------------------------
st.markdown(
    '<a href="#page-top" class="top-btn-float">↑ TOP</a>',
    unsafe_allow_html=True,
)

