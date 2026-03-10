# core/utils/cache.py
from __future__ import annotations

import json
import os
import time
import difflib
from pathlib import Path
from typing import Any, Callable, Optional


# 캐시 저장 폴더 (core/data/cache)
DEFAULT_CACHE_DIR = Path(__file__).resolve().parents[1] / "data" / "cache"
CACHE_DIR = Path(os.getenv("CACHE_DIR", str(DEFAULT_CACHE_DIR)))

def _ensure_cache_dir() -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _safe_key(key: str) -> str:
    """
    파일명 안전하게 변환 (공백/슬래시/특수문자 최소 처리)
    """
    return "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in key).strip("_")


def cache_path(key: str) -> Path:
    _ensure_cache_dir()
    return CACHE_DIR / f"{_safe_key(key)}.json"


def load_cache(key: str) -> Optional[dict]:
    """
    캐시 파일이 있으면 dict 로드, 없으면 None
    """
    path = cache_path(key)
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # 깨진 캐시 파일이면 무시
        return None


def save_cache(key: str, payload: Any) -> None:
    """
    payload는 JSON으로 직렬화 가능한 값이어야 함.
    """
    path = cache_path(key)
    data = {
        "_cached_at": int(time.time()),
        "payload": payload,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_expired(cache_obj: dict, ttl_seconds: int) -> bool:
    """
    ttl_seconds가 0이면 항상 만료로 간주(항상 새로 fetch)
    """
    if ttl_seconds <= 0:
        return True
    cached_at = cache_obj.get("_cached_at")
    if not isinstance(cached_at, int):
        return True
    return (time.time() - cached_at) > ttl_seconds


def get_or_fetch(
    key: str,
    fetch_fn: Callable[[], Any],
    ttl_seconds: int = 86400,
    force_refresh: bool = False,
) -> Any:
    """
    캐시 우선 사용:
    - 캐시 존재 + TTL 안 지남 => 캐시 payload 반환
    - 아니면 fetch_fn() 실행 후 저장하고 payload 반환

    force_refresh=True면 무조건 fetch 후 저장.
    """
    if not force_refresh:
        cached = load_cache(key)
        if cached and not is_expired(cached, ttl_seconds):
            return cached.get("payload")

    payload = fetch_fn()
    save_cache(key, payload)
    return payload


def clear_cache(key: str) -> bool:
    """
    특정 캐시 파일 삭제. 삭제 성공하면 True.
    """
    path = cache_path(key)
    if path.exists():
        path.unlink()
        return True
    return False

# 캐시 파일 유사도 기반 검색(difflib 이용)
def find_similar_key(query_key: str, prefix: str = "", threshold: float = 0.8) -> Optional[str]:
    """
    저장된 캐시 파일 목록 중 'prefix'로 시작하면서 query_key와 유사한 키를 반환합니다.
    - threshold: 0.0 ~ 1.0 (1.0에 가까울수록 엄격하게 일치해야 함)
    """
    # 캐시 디렉토리가 없으면 만들기
    _ensure_cache_dir()

    q = _safe_key(query_key)
    pfx = _safe_key(prefix)

    # 의도(prefix)로 시작하는 파일만 필터링해 캐시 안 .json 파일 이름 가져오기
    cache_files = [p.stem for p in CACHE_DIR.glob(f"{pfx}*.json")]

    if not cache_files:
        return None
    
    # 가장 유사한 키 목록 뽑기(n=1 : 한개만)
    matches = difflib.get_close_matches(q, cache_files, n=1, cutoff=threshold)

    return matches[0] if matches else None

# 캐시 클리닝
def clean_expired_cache(ttl_seconds: int = 86400 * 7) -> int:
    """
    clean_expired_cache의 Docstring
    지정된 ttl_seconds(기본 7일)보다 오래된 캐시 파일을 찾아 삭제합니다.
    - 반환값: 삭제된 파일의 개수
    """

    _ensure_cache_dir()
    deleted_count = 0
    now = time.time()

    # .json 파일 순회
    for cache_file in CACHE_DIR.glob("*.json"):
        try :
            with cache_file.open("r", encoding="utf-8") as f :
                data = json.load(f)
            
            cached_at = data.get("_cached_at", 0)

            if (now - cached_at > ttl_seconds):
                cache_file.unlink() # 파일 삭제
                deleted_count += 1
        except (json.JSONDecoderError, PermissionError, KeyError):
            # 깨진 파일, 읽기 권한 없는 파일 삭제 처리
            cache_file.unlink()
            deleted_count += 1

    if deleted_count > 0 :
        print(f"[Cache Cleanup] {deleted_count}개의 만료된 캐시 파일이 삭제되었습니다.")
    
    return deleted_count

