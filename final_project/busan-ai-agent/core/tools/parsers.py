# core/tools/parsers.py
from typing import Any, Dict, List, Optional
import re
import xmltodict

def xml_to_dict(xml_text: str) -> Dict[str, Any]:
    return xmltodict.parse(xml_text)

def safe_get(d: Dict[str, Any], path: List[str], default=None):
    cur = d
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur

# zipCd를 리스트로 파싱하여 5자리 숫자로 뽑기(부산지역코드 구분 전처리)
def parse_zip_codes(zip_value: Any) -> List[str]:
    if not zip_value:
        return []
    s = str(zip_value)
    return re.findall(r"\b\d{5}\b", s)


