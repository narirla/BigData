# core/agent/job_mapper.py

from typing import Any, Dict, List, Optional, Union

def find_job_codes_by_name(
    job_name: str,
    jobs_meta: List[Dict[str, Any]],
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    job_name(사용자 입력/추천 결과)로 목록(jobs_meta)에서 후보를 찾아 반환.
    - 1차: 완전일치
    - 2차: 포함 매칭(부분일치)
    반환 예: [{"jobCd": "...", "jobNm": "...", "jobClcd": "...", "jobClcdNM": "..."}]
    """
    if not job_name:
        return []

    q = job_name.strip()

    exact = [j for j in jobs_meta if (j.get("jobNm") or "").strip() == q]
    if exact:
        return exact[:top_k]

    partial = [j for j in jobs_meta if q in ((j.get("jobNm") or "").strip())]
    if partial:
        return partial[:top_k]

    # 느슨한 매칭: 공백 제거 후 비교(예: "데이터 분석가" vs "데이터분석가")
    q2 = q.replace(" ", "")
    loose = [
        j for j in jobs_meta
        if q2 and q2 in ((j.get("jobNm") or "").replace(" ", ""))
    ]
    return loose[:top_k]
