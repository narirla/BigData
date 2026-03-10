# core/tools/formatters.py
import re
from typing import List, Dict, Any

# core/tools/formatters.py

def _v(x):
    return x if x not in [None, ""] else "-"

def _normalize_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        return [x]
    return []

def _pick(*vals):
    """
    여러 후보 중 첫 번째로 '의미있는 값'을 반환
    """
    for v in vals:
        if v not in [None, "", "-"]:
            return v
    return None

def _get_any(sections: Dict[str, Any], keys: List[str], default=None):
    """
    sections의 여러 dtlGb(dict들)에서 keys 후보를 순서대로 찾아 첫 값 반환.
    예: keys=["jobSum","jobWork","work","doing"] 같은 식으로 확장 가능
    """
    if not isinstance(sections, dict):
        return default
    
    # dtlGb 우선순위: 2(하는일) -> 1(요약) -> 3(교육) -> 4(전망/임금)
    order = ["2", "1", "3", "4", "5", "6", "7"]
    for gb in order:
        sec = sections.get(gb)
        if not isinstance(sec, dict):
            continue
        for k in keys:
            if k in sec and sec.get(k) not in [None, ""]:
                return sec.get(k)

    # 마지막으로 모든 섹션을 다 훑기
    for _, sec in sections.items():
        if not isinstance(sec, dict):
            continue
        for k in keys:
            if k in sec and sec.get(k) not in [None, ""]:
                return sec.get(k)

    return default

def _get_list_any(sections: Dict[str, Any], keys: List[str]) -> List[Any]:
    val = _get_any(sections, keys, default=None)
    return _normalize_list(val)

def _join_names(items, key="majorNm", limit=8):
    items = _normalize_list(items)
    if not items:
        return "-"
    names = []
    for it in items:
        if isinstance(it, dict):
            v = it.get(key)
            if v:
                names.append(str(v))
        elif isinstance(it, str):
            names.append(it)
    if not names:
        return "-"
    if len(names) > limit:
        return ", ".join(names[:limit]) + f" 외 {len(names)-limit}개"
    return ", ".join(names)

def _format_salary(sal):
    if sal in [None, "", "-"]:
        return (
            "공식 평균 임금 데이터는 제공되지 않습니다.\n"
            "대신 아래 사이트에서 채용 공고 기준 연봉을 확인해보세요.\n"
            "- 워크넷 https://www.work.go.kr\n"
            "- 사람인 / 잡코리아 (직무명 검색)"
        )
    return sal

def _format_satisfaction(satis):
    if satis in [None, "", "-"]:
        return (
            "정확한 만족도 통계가 없습니다.\n"
            "일반적으로 이 직종의 만족도는 근무 환경과 워라밸에 따라 차이가 큽니다.\n"
            "직장인 커뮤니티(블라인드, 잡플래닛)의 현직자 리뷰를 참고해 보세요."
        )
    return f"{satis}%"

def _format_prospect(prospect):
    if prospect in [None, "", "-"]:
        return (
            "공식적인 장기 전망 데이터가 확인되지 않습니다.\n"
            "산업 트렌드와 기술 변화에 따라 유동적일 수 있으니,\n"
            "'커리어넷(CareerNet)'의 직업 전망 리포트를 함께 확인하시는 것을 추천드립니다."
        )
    return prospect

def _format_status(status):
    if status in [None, "", "-"]:
        return (
            "현재 고용 현황 상세 데이터가 제공되지 않습니다.\n"
            "부산 지역의 실시간 채용 현황은 '부산일자리정보망'이나\n"
            "'부산워크넷'에서 직접 확인하는 것이 가장 정확합니다."
        )
    return status


NEGATIVE_MARKERS = [
    "직업코드를 찾지 못했습니다",
    "직업코드를 찾을 수",
    "찾지 못",
    "조회 결과가 없습니다",
    "검색된 직업이 없습니다",
    "다른 키워드로 검색해",
]

def is_negative(text: str) -> bool:
    return any(m in text for m in NEGATIVE_MARKERS)


def format_policy_detail(detail: dict) -> str:
    # 연령/소득은 합쳐서 처리
    age_range = f"{_v(detail.get('sprtTrgtMinAge'))} ~ {_v(detail.get('sprtTrgtMaxAge'))}"
    income_range = f"{_v(detail.get('earnMinAmt'))} ~ {_v(detail.get('earnMaxAmt'))}"

    return (
        # 1. 기본 정보
        f"정책명: {_v(detail.get('plcyNm'))}\n"
        f"정책번호: {_v(detail.get('plcyNo'))}\n"
        f"키워드: {_v(detail.get('plcyKywdNm'))}\n\n"

        f"정책설명\n{_v(detail.get('plcyExplnCn'))}\n\n"
        f"정책지원내용\n{_v(detail.get('plcySprtCn'))}\n\n"

        # 2. 신청 정보
        f"신청 정보\n"
        f"- 신청기간: {_v(detail.get('aplyYmd'))}\n"
        f"- 신청 URL: {_v(detail.get('aplyUrlAddr'))}\n"
        f"- 참고 URL: {_v(detail.get('refUrlAddr1'))}\n\n"

        # 3. 신청 / 심사 방법
        f"신청 및 심사 방법\n"
        f"- 신청방법: {_v(detail.get('plcyAplyMthdCn'))}\n"
        f"- 제출서류: {_v(detail.get('sbmsnDcmntCn'))}\n"
        f"- 심사방법: {_v(detail.get('srngMthdCn'))}\n\n"

        # 4. 대상 요건
        f"지원 대상 요건\n"
        f"- 연령: {age_range}\n"
        f"- 소득조건: {income_range}\n"
        f"- 소득기타내용: {_v(detail.get('earnEtcCn'))}\n\n"

        # 5. 지역 / 대상 설명
        f"거주지역: {_v(detail.get('zipCd'))}\n"
        f"참여대상내용\n{_v(detail.get('ptcpPrpTrgtCn'))}"
    )

BUSAN_DISTRICTS = [
    "중구","서구","동구","영도구","부산진구","동래구","남구","북구",
    "해운대구","사하구","금정구","강서구","연제구","수영구","사상구","기장군"
]

def extract_busan_district(address: str) -> str:
    if not address:
        return "-"
    for d in BUSAN_DISTRICTS:
        if d in address:
            return d
    return "부산(구·군 미확인)"

def format_training_detail(detail):
    district = extract_busan_district(detail.get("address"))

    return (
        f"훈련과정명: {detail.get('title')}\n"
        f"훈련기관: {detail.get('subTitle')}\n"
        f"훈련기간: {detail.get('traStartDate')} ~ {detail.get('traEndDate')}\n"
        f"훈련분류: {detail.get('trainTarget')}\n\n"

        f"수강비: {detail.get('courseMan')}\n"
        f"정원: {detail.get('yardMan')}\n\n"

        f"지역: 부산 {district}\n"
        f"주소: {detail.get('address')}\n"
        f"전화번호: {detail.get('telNo')}\n\n"

        f"훈련정보: {detail.get('titleLink')}"
    )


def format_job_detail_basic(job_cd: str, s1: dict) -> str:
    title = _v(s1.get("jobSmclNm") or s1.get("jobMdclNm") or s1.get("jobLrclNm"))
    sal = _v(s1.get("sal"))
    prospect = _v(s1.get("jobProspect"))
    satis = _v(s1.get("jobSatis"))

    return (
        f"직업: {title} (jobCd: {job_cd})\n\n"
        f"요약\n{_v(s1.get('jobSum'))}\n\n"
        f"되는 길\n{_v(s1.get('way'))}\n\n"
        f"임금: {sal}\n"
        f"전망: {prospect}\n"
    )

def _join_cert_names(items, limit=8):
    # relCertList는 {"certNm": "..."} 형태가 흔함
    return _join_names(items, key="certNm", limit=limit)

def _join_rel_jobs(items, limit=8):
    # relJobList는 {"jobNm": "..."} 형태가 흔함
    return _join_names(items, key="jobNm", limit=limit)

def format_job_bundle(job_cd: str, sections: dict) -> str:
    # sections가 {"1":{...}} 형태가 아니라 dtlGb_1 단일 dict로 들어오는 경우 방어
    if isinstance(sections, dict) and "jobSum" in sections and not any(k in sections for k in ["1","2","3","4","5","6","7"]):
        sections = {"1": sections}
    """
    dtlGb가 들쭉날쭉/1번 몰빵이어도 깨지지 않는 안전 출력
    """

    title = _pick(
        _get_any(sections, ["jobSmclNm"]),
        _get_any(sections, ["jobMdclNm"]),
        _get_any(sections, ["jobLrclNm"]),
    ) or "-"

    # 직업 타이틀 후보
    job_sum = _get_any(sections, ["jobSum", "summary", "sum"], default="-")
    way = _get_any(sections, ["way", "path", "road"], default="-")

    # 요약/되는길/하는길
    majors = _get_list_any(sections, ["relMajorList", "majorList"])
    certs = _get_list_any(sections, ["relCertList", "certList"])
    rel_jobs = _get_list_any(sections, ["relJobList", "jobList"])

    # 관련 전공/자격증/관련 직업
    major_text = _join_names(majors, key="majorNm")
    cert_text = _join_names(certs, key="certNm")
    rel_jobs_text = _join_names(rel_jobs, key="jobNm")

    # 임금/만족도/전망/현황 (전부 1번 몰빵 가능)
    sal = _get_any(sections, ["sal", "avgSal", "salary"], default="-")
    satis = _get_any(sections, ["jobSatis", "satis"], default="-")
    prospect = _get_any(sections, ["jobProspect", "prospect"], default="-")
    status = _get_any(sections, ["jobStatus", "status"], default="-")

    # 추가 정보(있으면 보여주기)
    abil = _get_any(sections, ["jobAbil", "abil"], default=None)
    know = _get_any(sections, ["knowldg", "knowledge"], default=None)
    env = _get_any(sections, ["jobEnv", "env"], default=None)
    chr_ = _get_any(sections, ["jobChr", "character"], default=None)
    intr = _get_any(sections, ["jobIntrst", "interest"], default=None)
    vals = _get_any(sections, ["jobVals", "values"], default=None)

    extra_lines = []
    if abil not in [None, "", "-"]:
        extra_lines.append(f"필요 능력\n{abil}")
    if know not in [None, "", "-"]:
        extra_lines.append(f"필요 지식\n{know}")
    if env not in [None, "", "-"]:
        extra_lines.append(f"업무 환경\n{env}")
    if chr_ not in [None, "", "-"]:
        extra_lines.append(f"성격/특성\n{chr_}")
    if intr not in [None, "", "-"]:
        extra_lines.append(f"흥미\n{intr}")
    if vals not in [None, "", "-"]:
        extra_lines.append(f"가치관\n{vals}")

    extra_block = "\n\n".join(extra_lines)
    if extra_block:
        extra_block = "\n\n---\n\n" + extra_block

    return (
        f"직업: {title}\n"
        f"jobCd: {job_cd}\n\n"
        f"요약\n{_v(job_sum)}\n\n"
        f"되는 길\n{_v(way)}\n\n"
        f"관련 전공: {major_text}\n"
        f"관련 자격증: {cert_text}\n\n"
        f"임금: {_format_salary(sal)}\n"
        f"만족도: {_format_satisfaction(satis)}\n"
        f"전망: {_format_prospect(prospect)}\n"
        f"현황: {_format_status(status)}\n\n"
        f"관련 직업: {rel_jobs_text}"
        f"{extra_block}"
    )
