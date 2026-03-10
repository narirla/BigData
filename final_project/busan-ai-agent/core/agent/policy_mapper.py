# core/agent/policy_mapper.py

import re
import difflib
from typing import List, Dict, Any, Optional

def _norm(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").lower())

def find_best_policy_by_name(
    query: str,
    items: List[Dict[str, Any]],
    top_k: int = 3,
) -> List[Dict[str, Any]]:
    if not query or not items:
        return []
    q = _norm(query)

    # 1) 완전일치(공백 제거 기준)
    exact = [it for it in items if _norm(it.get("plcyNm", "")) == q]
    if exact:
        return exact[:top_k]

    # 2) 부분포함
    partial = [it for it in items if q in _norm(it.get("plcyNm", ""))]
    if partial:
        return partial[:top_k]

    # 3) 유사도 매칭
    names = [it.get("plcyNm", "") for it in items]
    norm_names = [_norm(n) for n in names]
    # difflib로 제일 가까운 이름 찾기
    best = difflib.get_close_matches(q, norm_names, n=top_k, cutoff=0.6)

    results = []
    for b in best:
        idx = norm_names.index(b)
        results.append(items[idx])
    return results
