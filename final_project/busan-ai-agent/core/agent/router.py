# core/agent/router.py
import re
from typing import Any
from core.tools.parsers import parse_zip_codes

# any() : 리스트, 튜플 처럼 반복 가능한(iterable) 객체에
# 단 하나라도 참(True)이 있으면 참을 반환(키워드 확인)

def needs_employment_event_tool(user_input:str) -> bool:
    keywords = ["채용행사", "채용", "취업행사", "박람회", "설명회",
                "일자리", "채용 라운지", "자세히", "상세", "행사정보", "행사"]
    if any(k in user_input for k in keywords):
        return True
    
    if re.search(r"\b\d{4,}\b", user_input):
        return True

    return False

# 부산권 26XXX 걸러내기
def is_busan_policy(zip_value:Any)->bool:
    codes = parse_zip_codes(zip_value)
    return any(c.startswith("26") for c in codes)

def is_busan_only(zip_value: Any) -> bool:
    codes = parse_zip_codes(zip_value)
    if not codes:
        return False
    return all(c.startswith("26") for c in codes)

def includes_busan(zip_value: Any) -> bool:
    codes = parse_zip_codes(zip_value)
    return any(c.startswith("26") for c in codes)