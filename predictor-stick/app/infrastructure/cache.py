from cachetools import TTLCache
from app.core.config import settings
from typing import Any, Tuple

# keys: ("channel", channel, version) / ("subject", subject_id, version)
model_cache: TTLCache[Tuple[str, str, str], Any] = TTLCache(
    maxsize=settings.CACHE_MAX_ITEMS, ttl=settings.CACHE_TTL_SECONDS
)

def clear_all():
    model_cache.clear()

def clear_keys(keys: list[tuple[str, str, str]]):
    for k in keys:
        try:
            del model_cache[k]
        except KeyError:
            pass
