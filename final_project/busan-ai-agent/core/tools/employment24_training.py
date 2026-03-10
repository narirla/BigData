# core/tools/employment24_training.py
from typing import Dict, Any, List, Optional
import os, requests
from .parsers import xml_to_dict, safe_get

BASE_URL = "https://www.work24.go.kr/cm/openApi/call/hr/callOpenApiSvcInfo310L01.do"

def search_training_it(
        srchTraArea1: str = "26",
        page_num: int = 1,
        page_size: int = 30,
        keyword: Optional[str] = None,
        srchNcs1: str='20',
        crseTracseSe: Optional[str] = None,
        debug: bool = False
) -> List[Dict[str, Any]]:
    auth_key = os.getenv("WORK24_AUTH_KEY_TRAINING")
    if not auth_key:
        raise RuntimeError("WORK24_AUTH_KEY_TRAINING is not set")
    
    params = {
        "authKey": auth_key,
        "returnType": "JSON",
        "outType": "2",
        "pageNum": str(page_num),
        "pageSize": str(page_size),
        "srchTraArea1": srchTraArea1,
        "srchNcs1" : srchNcs1
    }
    # if srchNcs1:
    #     params["srchNcs1"] = srchNcs1
    if crseTracseSe:
        params["crseTracseSe"] = crseTracseSe
    if keyword:
        params["srchTraProcessNm"] = keyword

    r = requests.get(BASE_URL, params=params, timeout=15)
    # 디버깅용
    if debug:
        return {
            "ok": r.ok,
            "status_code": r.status_code,
            "final_url": r.url,                 # 실제 호출된 URL
            "response_head": r.text[:800],      # 응답 앞부분(에러/빈결과/구조 확인)
        }
    r.raise_for_status()

    # JSON 실패하면 XML
    items = []
    try :
        payload = r.json()

        if isinstance(payload.get("srchList"), list):
            items = payload["srchList"]
        elif isinstance(payload.get("HRDNet", {}).get("srchList"), list):
            items = payload["HRDNet"]["srchList"]
        else :
            items = payload.get("HRDNet", {}).get("srchList", {}).get("scn_list", [])

    except Exception:
        data = xml_to_dict(r.text)
        items = safe_get(data, ["HRDNet", "srchList", "scn_list"], default=[])
    if isinstance(items, dict):
        items = [items]
    
    return items