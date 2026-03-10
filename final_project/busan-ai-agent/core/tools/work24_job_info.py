# core/tools/work24_job_info.py
from __future__ import annotations

from typing import Any, Dict, List, Optional, Union
import os
import requests

from core.utils.cache import get_or_fetch
from core.tools.parsers import xml_to_dict, safe_get


# 직업정보 목록(키워드/조건 검색)
BASE_URL_LIST = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo212L01.do"
# 직업정보 상세(dtlGb로 섹션 선택)
BASE_URL_DETAIL = "https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo212D01.do"


def _get_auth_key() -> str:
    auth_key = os.getenv("WORK24_AUTH_KEY_JOBINFO")
    if not auth_key:
        raise RuntimeError("WORK24_AUTH_KEY_JOBINFO is not set")
    return auth_key


def _normalize_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        return [x]
    return []


# -----------------------------
# 1) 직업정보 API
# -----------------------------
def search_job_list(
    srchType: str = "K",
    keyword: Optional[str] = None,
    avgSal: Optional[str] = None,
    prospect: Optional[str] = None,
    returnType: str = "XML",  # 문서상 XML 고정
    debug: bool = False,
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    직업 정보 조회
    - srchType: K(키워드), C(조건: 연봉/전망)
    - keyword: srchType=K일 때만 사용
    - avgSal/prospect: srchType=C일 때만 사용
    """
    auth_key = _get_auth_key()

    params = {
        "authKey": auth_key,
        "returnType": returnType,
        "target": "JOBCD",
        "srchType": srchType,
    }

    if srchType == "K":
        if keyword:
            params["keyword"] = keyword
    elif srchType == "C":
        if avgSal:
            params["avgSal"] = avgSal
        if prospect:
            params["prospect"] = prospect

    r = requests.get(BASE_URL_LIST, params=params, timeout=20)

    if debug:
        return {
            "ok": r.ok,
            "status_code": r.status_code,
            "final_url": r.url,
            "response_head": r.text[:800],
        }

    r.raise_for_status()

    data = xml_to_dict(r.text)

    # XML 구조: <jobsList><total>...</total><jobList>...</jobList></jobsList>
    jobs_list = safe_get(data, ["jobsList"], default={})
    total = safe_get(jobs_list, ["total"], default=None)
    items = safe_get(jobs_list, ["jobList"], default=[])
    items = _normalize_list(items)

    results: List[Dict[str, Any]] = []
    for it in items:
        results.append(
            {
                "jobClcd": it.get("jobClcd"),
                "jobClcdNM": it.get("jobClcdNM"),
                "jobCd": it.get("jobCd"),
                "jobNm": it.get("jobNm"),
            }
        )

    # total을 같이 쓰고 싶으면 handler에서 쓰기 편하게 dict로 감싸도 되는데,
    # 지금은 단순 리스트 반환으로 통일
    return results


def get_job_list_cached(
    srchType: str = "K",
    keyword: Optional[str] = None,
    avgSal: Optional[str] = None,
    prospect: Optional[str] = None,
    ttl_seconds: int = 60 * 60 * 24,  # 24시간
    force_refresh: bool = False,
) -> List[Dict[str, Any]]:
    """
    목록 캐시 버전
    - 키워드/조건 조합마다 캐시 키가 달라야 함
    """
    key = f"work24_job_list_srchType={srchType}_kw={keyword}_avgSal={avgSal}_prospect={prospect}"

    return get_or_fetch(
        key=key,
        ttl_seconds=ttl_seconds,
        force_refresh=force_refresh,
        fetch_fn=lambda: search_job_list(
            srchType=srchType,
            keyword=keyword,
            avgSal=avgSal,
            prospect=prospect,
            debug=False,
        ),
    )


# -----------------------------
# 2) 직업 상세 API
# -----------------------------

def _pick_first_dict(x):
    if isinstance(x, dict):
        return x
    if isinstance(x, list) and x:
        return x[0] if isinstance(x[0], dict) else None
    return None

def _find_first_dict_by_keys(data: dict, keys: list[str]) -> dict:
    """
    data(파싱된 xmltodict 결과)에서
    keys 후보를 순서대로 찾아서 dict 하나를 반환.
    """
    for k in keys:
        node = safe_get(data, [k], default=None)
        node = _pick_first_dict(node)
        if node:
            return node

        # 가끔 한 단계 더 들어갈 수도 있으니 후보로도 체크
        node2 = safe_get(data, ["jobDtl", k], default=None)
        node2 = _pick_first_dict(node2)
        if node2:
            return node2
    return {}


def get_job_detail(
    jobCd: str,
    dtlGb: str,
    jobGb: str = "1",
    returnType: str = "XML",
    debug: bool = False,
) -> Union[Dict[str, Any], Dict[str, Any]]:
    """
    직업 상세 조회
    - dtlGb:
      1 요약, 2 하는 일, 3 교육/자격/훈련, 4 임금/만족도/전망,
      5 능력/지식/환경, 6 성격/흥미/가치관, 7 업무활동
    """
    auth_key = _get_auth_key()

    params = {
        "authKey": auth_key,
        "returnType": returnType,
        "target": "JOBDTL",
        "jobGb": jobGb,
        "jobCd": jobCd,
        "dtlGb": dtlGb,
    }

    r = requests.get(BASE_URL_DETAIL, params=params, timeout=20)

    if debug:
        return {
            "ok": r.ok,
            "status_code": r.status_code,
            "final_url": r.url,
            "response_head": r.text[:1200],
        }

    r.raise_for_status()

    data = xml_to_dict(r.text)

    # 문서 예시는 <jobSum> 아래에 많은 필드가 있음.
    # 실제 응답 루트가 다를 수 있어서 넉넉하게 탐색:

    candidates = [
        "jobSum", "jobWork", "jobEdu", "jobStat", "jobAbility", "jobDtl",
        "jobInfo", "result", "data"
    ]
    # - jobSum이 dict면 그대로
    # - list면 첫 번째

    node = _find_first_dict_by_keys(data, candidates)
    if not node:
        return {}
    
    # job_sum = safe_get(data, ["jobSum"], default=None)

    # 어떤 응답은 최상위가 아니라 한 단계 더 들어갈 수도 있어서 후보를 몇 개 더 본다
    # if not job_sum:
    #     job_sum = safe_get(data, ["jobDtl", "jobSum"], default=None)
    # if isinstance(job_sum, list) and job_sum:
    #     job_sum = job_sum[0]

    # if not isinstance(job_sum, dict):
    #     return {}

    # 관련전공/자격증/관련직업은 list/dict 섞여올 수 있음
    rel_majors = _normalize_list(node.get("relMajorList"))
    rel_certs = _normalize_list(node.get("relCertList"))
    rel_jobs = _normalize_list(node.get("relJobList"))

    # 깔끔하게 정규화해서 반환
    normalized = dict(node)
    if rel_majors:
        normalized["relMajorList"] = rel_majors
    if rel_certs:
        normalized["relCertList"] = rel_certs
    if rel_jobs:
        normalized["relJobList"] = rel_jobs

    return normalized


def get_job_detail_cached(
    jobCd: str,
    dtlGb: str,
    ttl_seconds: int = 60 * 60 * 24 * 7,  # 7일
    force_refresh: bool = False,
) -> Dict[str, Any]:
    """
    상세 캐시 버전
    - 직업코드 + dtlGb 조합마다 캐시
    """
    key = f"work24_job_detail_jobCd={jobCd}_dtlGb={dtlGb}"

    return get_or_fetch(
        key=key,
        ttl_seconds=ttl_seconds,
        force_refresh=force_refresh,
        fetch_fn=lambda: get_job_detail(jobCd=jobCd, dtlGb=dtlGb, debug=False),
    )


# 추천 직업 상세 묶음 조회

def get_job_profile_bundle_cached(
    jobCd: str,
    dtlGbs: List[str] = ["1", "2", "3", "4"],
) -> Dict[str, Any]:
    """
    한 직업(jobCd)에 대해 필요한 dtlGb 섹션을 묶어서 반환.
    반환:
    {
      "jobCd": "...",
      "sections": {
         "1": {...},
         "2": {...},
         ...
      }
    }
    """

    if "1" not in dtlGbs:
        dtlGbs = ["1"] + dtlGbs

    sections = {}
    for gb in dtlGbs:
        sections[gb] = get_job_detail_cached(jobCd=jobCd, dtlGb=gb)
    # 보험
    if all(isinstance(v, dict) and not v for v in sections.values()):
        sections["1"] = get_job_detail_cached(jobCd=jobCd, dtlGb="1", force_refresh=True)

    return {"jobCd": jobCd, "sections": sections}
