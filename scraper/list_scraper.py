# ============================================
# 📋 SCRAPER/LIST_SCRAPER.PY — Listing Scraper
# Scrapes search results and homepage cards.
# To support a new website: duplicate this file,
# adjust CSS selectors, and register in config.py
# ============================================
import requests
from bs4 import BeautifulSoup
from config import BASE_URL, HEADERS
from scraper.helpers import clean


def scrape_list(url: str) -> list[dict]:
    """
    Scrape a listing/search page and return a list of post dicts:
    { title, url, poster, year, extra, formats, slug }
    """
    posts = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(resp.content, 'html.parser')

        for card in soup.find_all('a', class_='movie-card'):
            href = card.get('href', '')
            if not href:
                continue
            full_url = href if href.startswith('http') else BASE_URL + href

            # ── Poster & quality badges ──────────────
            img_div   = card.find('div', class_='movie-card-image')
            poster, formats = '', []
            if img_div:
                img = img_div.find('img')
                if img:
                    poster = img.get('src', '')
                overlay = img_div.find('div', class_='movie-card-overlay')
                if overlay:
                    formats = [
                        clean(f.text)
                        for f in overlay.find_all('span', class_='movie-card-format')
                    ]

            # ── Title, year, extra meta ───────────────
            content = card.find('div', class_='movie-card-content')
            title, year, extra = '', '', ''
            if content:
                t = content.find('h3', class_='movie-card-title')
                if t:
                    title = clean(t.text)
                m = content.find('p', class_='movie-card-meta')
                if m:
                    parts = [p.strip() for p in clean(m.text).split('•')]
                    if parts:
                        year = clean(parts[0])
                    if len(parts) > 1:
                        extra = clean(' • '.join(parts[1:]))

            if title:
                posts.append({
                    'title':   title,
                    'url':     full_url,
                    'poster':  poster,
                    'year':    year,
                    'extra':   extra,
                    'formats': formats,
                    'slug':    full_url.split('/')[-2] if '/' in full_url else '',
                })
    except Exception as e:
        print(f"[list_scraper] {e}")
    return posts
