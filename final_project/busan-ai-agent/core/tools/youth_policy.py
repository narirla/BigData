# core/tools/youth_policy.py

from typing import Dict, Any, List, Optional
import os, requests
from .parsers import xml_to_dict, safe_get
from core.agent.router import is_busan_only, includes_busan

YOUTH_BASE_URL_LIST="https://www.youthcenter.go.kr/go/ythip/getPlcy"

# Non-public(모듈안에서만 작동)
def _normalize_list(x):
    if x is None:
        return []
    if isinstance(x, list):
        return x
    if isinstance(x, dict):
        return [x]
    return []

def search_youth_policies(
        keyword_csv: Optional[str] = None,          # 취업,교육,주거
        lclsfNm_csv: Optional[str] = None,          # 일자리,주거
        mclsfNm_csv: Optional[str] = None,          # 취업,창업
        page_num: int = 1,
        page_size: int = 10,
        zip_cd: str = "26000",                      # 부산광역시
        rtn_type: str = "json",                     # json 추천 (안되면 xml로)
        debug: bool = False,
        busan_mode: str = "only"
) -> List[Dict[str, Any]] | Dict[str, Any]:         # 리스트, 딕셔너리 모두 받음
    api_key=os.getenv("YOUTH_POLICY_OPENAPI_KEY")
    if not api_key:
        raise RuntimeError("YOUTH_POLICY_OPENAPI_KEY is not set")
    
    params = {
        "apiKeyNm": api_key,
        "pageNum": page_num,
        "pageSize": page_size,
        "pageType": "1",        # 목록
        "zipCd": zip_cd,
        "rtnType": rtn_type,    # json or xml
    }
    if keyword_csv:
        params["plcyKywdNm"] = keyword_csv
    if lclsfNm_csv:
        params["lclsfNm"] = lclsfNm_csv
    if mclsfNm_csv:
        params["mclsfNm"] = mclsfNm_csv
    
    r = requests.get(YOUTH_BASE_URL_LIST, params=params, timeout=20)

    if debug:
        return {
            "ok": r.ok,
            "status_code": r.status_code,
            "final_url": r.url,
            "response_head": r.text[:800],
        }
    
    r.raise_for_status()

    # json 시도
    if rtn_type.lower() == "json":
        try:
            payload = r.json()
            items = (
                payload.get("youthPolicyList")
                or payload.get("result", {}).get("youthPolicyList")
                or payload.get("data", {}).get("youthPolicyList")
            )
            items = _normalize_list(items)
        except Exception:
            items = []
    else:
        items = []
    
    # json 실패하면 XML 파싱
    if not items :
        data = xml_to_dict(r.text)
        items = safe_get(data, ["youthPolicyList"], default=[])
        items = _normalize_list(items)

    results: List[Dict[str, Any]] = []
    for it in items :
        results.append({
            "plcyNo": it.get("plcyNo"),
            "plcyNm": it.get("plcyNm"),
            "lclsfNm": it.get("lclsfNm"),
            "mclsfNm": it.get("mclsfNm"),
            "plcyKywdNm": it.get("plcyKywdNm"),
            "plcyExplnCn": (it.get("plcyExplnCn") or "")[:200],
            "sprtTrgtMinAge": it.get("sprtTrgtMinAge"),
            "sprtTrgtMaxAge": it.get("sprtTrgtMaxAge"),
            "aplyUrlAddr": it.get("aplyUrlAddr"),
            "rgtrInstCdNm": it.get("rgtrInstCdNm"),
            "zipCd": it.get("zipCd")
        })

    if busan_mode == "only":
        results = [r for r in results if is_busan_only(r.get("zipCd"))]
    else:  # "include"
        results = [r for r in results if includes_busan(r.get("zipCd"))]
    return results

def get_policy_detail(
    plcy_no: str,
    zip_cd: str = "26000",
    rtn_type: str = "json",
    debug: bool = False,   
) -> Dict[str, Any] | Dict[str, Any] :
    api_key = os.getenv("YOUTH_POLICY_OPENAPI_KEY")
    if not api_key:
        raise RuntimeError("YOUTH_POLICY_OPENAPI_KEY is not set")
    
    params = {
        "apiKeyNm": api_key,
        "pageType": "2",    # 상세
        "plcyNo": plcy_no,
        "zipCd": zip_cd,
        "rtnType": rtn_type,
    }

    r = requests.get(YOUTH_BASE_URL_LIST, params=params, timeout=20)

    if debug:
        return {
            "ok": r.ok,
            "status_code": r.status_code,
            "final_url": r.url,
            "response_head": r.text[:800],
        }

    r.raise_for_status()

    # JSON 우선
    if rtn_type.lower() == "json":
        try:
            payload = r.json()
            detail = (
                payload.get("youthPolicyList")
                or payload.get("result", {}).get("youthPolicyList")
                or payload.get("data", {}).get("youthPolicyList")
            )
            if isinstance(detail, list) and detail:
                detail = detail[0]
            if isinstance(detail, dict) and detail:
                return detail
        except Exception:
            pass

    # XML fallback
    try:
        data = xml_to_dict(r.text)
        detail = safe_get(data, ["youthPolicyList"], default={})
        if isinstance(detail, list) and detail:
            detail = detail[0]
    except Exception as e:
        print(f"[XML Parsing Error] {e}")
        return {}
    
    if detail and not includes_busan(detail.get("zipCd")):
        return {}
    return detail
