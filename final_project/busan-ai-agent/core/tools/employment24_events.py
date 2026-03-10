# core/tools/employment24_jobs.py
from typing import Dict, Any, List, Optional
import os, requests
from .parsers import xml_to_dict, safe_get

# 채용행사목록
BASE_URL="https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210L11.do"
BASE_URL_DETAIL="https://www.work24.go.kr/cm/openApi/call/wk/callOpenApiSvcInfo210D11.do"


# 채용행사 목록검색 Tool
def search_employment_events(
        keyword: str,
        start_page: int = 1,
        display: int = 10,
        areaCd: str = '52',
        debug: bool = False
) -> List[Dict[str, Any]]:
    auth_key = os.getenv("WORK24_AUTH_KEY_JOB")
    if not auth_key:
        raise RuntimeError("WORK24_AUTH_KEY is not set")

    # api 입력 필수 정보
    params = {
    "authKey"    : auth_key,
    "callTp"     : "L",
    "returnType" : "XML",
    "startPage"  : start_page,
    "display"    : display,
    "keyword"    : keyword,
    "areaCd"     : areaCd
    }
    
    r = requests.get(BASE_URL, params=params, timeout=15)
    # 디버깅
    if debug:
        return {
            "ok": r.ok,
            "status_code": r.status_code,
            "final_url": r.url,                 # 실제 호출된 URL
            "response_head": r.text[:800],      # 응답 앞부분(에러/빈결과/구조 확인)
        }
    r.raise_for_status()

    data = xml_to_dict(r.text)
    events = safe_get(data, ["empEvList", "empEvent"], default=[])
    # 이벤트가 1개일 경우 dict로 내려오면
    if isinstance(events, dict):
        events = [events]
    
    results = []
    for e in events:
        results.append({
            "area" : e.get("area"),
            "eventNo" : e.get("eventNo"),
            "eventNm" : e.get("eventNm"),
            "eventTerm" : e.get("eventTerm"),
            "startDt" : e.get("startDt")
        })
    print(results)
    return results


# 채용행사 상세검색 Tool
def get_employment_event_detail(
        eventNo: str,
        areaCd: str = '52',
        debug: bool = False
) -> Dict[str, Any]:
    auth_key = os.getenv("WORK24_AUTH_KEY_JOB")
    if not auth_key:
        raise RuntimeError("WORK24_AUTH_KEY is not set")

    # api 입력 필수 정보
    params = {
    "authKey"    : auth_key,
    "callTp"     : "D",
    "returnType" : "XML",
    "eventNo" : eventNo,
    "areaCd"     : areaCd
    }
    
    r = requests.get(BASE_URL_DETAIL, params=params, timeout=15)
    # 디버깅
    if debug:
        return {
            "ok": r.ok,
            "status_code": r.status_code,
            "final_url": r.url,                 # 실제 호출된 URL
            "response_head": r.text[:800],      # 응답 앞부분(에러/빈결과/구조 확인)
        }
    r.raise_for_status()

    data = xml_to_dict(r.text)
    detail = safe_get(data, ["empEventDtl"], default={})
    # 이벤트가 1개일 경우 dict로 내려오면
    if not isinstance(detail, dict) or not detail:
        return {}
    
    results = {
        "eventNm": detail.get("eventNm"),
        "eventTerm": detail.get("eventTerm"),
        "eventPlc": detail.get("eventPlc"),
        "joinCoWantedInfo": detail.get("joinCoWantedInfo"),
        "subMatter": detail.get("subMatter"),
        "inqTelNo": detail.get("inqTelNo"),
        "fax": detail.get("fax"),
        "charger": detail.get("charger"),
        "email": detail.get("email"),
        "visitPath": detail.get("visitPath"),
        }
    # print(results)
    return results