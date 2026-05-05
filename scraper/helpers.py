# ============================================
# 🔧 SCRAPER/HELPERS.PY — Scraper Utilities
# Shared helpers used by list & detail scrapers
# ============================================
import re, time
import requests
from config import BASE_URL, HEADERS
from utils.cache import set_cached


def clean(text: str) -> str:
    """Strip and collapse whitespace."""
    return ' '.join((text or '').split()).strip()


def extract_number(text: str) -> str:
    """Pull the episode number out of a badge string like 'Episode-05'."""
    if not text:
        return ''
    text = clean(text)
    for prefix in ['Episode-', 'Episode', 'Episo', 'episode', 'Ep-', 'EP', 'Ep']:
        text = text.replace(prefix, '')
    return ''.join(c for c in text if c.isdigit())


def check_web(url: str = BASE_URL) -> bool:
    """Return True if the site is reachable."""
    try:
        return requests.get(url, headers=HEADERS, timeout=10).status_code == 200
    except Exception:
        return False


def auto_fetch_all(max_pages: int = 10) -> list:
    """
    Crawl the listing pages and return all posts.
    Results are also written to cache automatically.
    """
    # Import here to avoid circular imports
    from scraper.list_scraper import scrape_list

    all_posts = []
    for i in range(1, max_pages + 1):
        url = BASE_URL if i == 1 else f"{BASE_URL}/page/{i}/"
        posts = scrape_list(url)
        if not posts:
            break
        all_posts.extend(posts)
        time.sleep(0.5)

    # Cache every discovered post
    for p in all_posts:
        set_cached(p['url'], {
            'title':  p['title'],
            'url':    p['url'],
            'poster': p.get('poster', ''),
        })

    return all_posts
