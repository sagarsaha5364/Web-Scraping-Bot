# ============================================
# 🗄️ UTILS/CACHE.PY — Cache Management
# Stores scraped data with TTL expiry
# ============================================
import json, os
from datetime import datetime, timedelta, UTC
from config import JSON_FILE, CACHE_TTL_HOURS


def load_cache() -> dict:
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_cache(data: dict) -> None:
    with open(JSON_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def get_cached(url: str):
    """Return cached data if still fresh, else None."""
    data = load_cache()
    if url in data:
        item = data[url]
        cached_at = item.get("cached_at", "")
        if cached_at:
            age = datetime.now(UTC) - datetime.fromisoformat(cached_at)
            if age < timedelta(hours=CACHE_TTL_HOURS):
                return item.get("data")
    return None


def set_cached(url: str, data) -> None:
    all_data = load_cache()
    all_data[url] = {
        "data":      data,
        "cached_at": datetime.now(UTC).isoformat(),
    }
    save_cache(all_data)


def clear_cache() -> None:
    save_cache({})


def cache_size() -> int:
    return len(load_cache())
