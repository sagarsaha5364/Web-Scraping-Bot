# ============================================
# 🖼️ UTILS/IMAGE.PY — Image Download Helper
# ============================================
import requests
from config import HEADERS


def download_image_bytes(url: str) -> bytes | None:
    """Download image from URL, return raw bytes or None on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code == 200 and len(resp.content) > 500:
            return resp.content
    except Exception:
        pass
    return None
