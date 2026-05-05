# ============================================
# 🔍 SCRAPER/DETAIL_SCRAPER.PY — Detail Page
# Scrapes a single movie/series page.
# To support a new website: duplicate this file,
# update selectors, and call from handlers.
# ============================================
import re, time
import requests
from bs4 import BeautifulSoup
from config import HEADERS
from scraper.helpers import clean, extract_number


def scrape_detail(url: str) -> dict | None:
    """
    Fetch and parse a detail page.
    Returns a structured dict or None on failure.
    """
    d = {
        'title': '', 'poster': '', 'imdb': '',
        'genres': [], 'overview': '',
        'stars': '', 'last_air': '', 'quality': '', 'audio': '', 'seasons': '',
        'packs': [], 'episodes': [], 'movie_downloads': [],
        'is_movie': False,
    }
    try:
        # Cache-bust the URL
        sep = '&' if '?' in url else '?'
        url += f"{sep}_={int(time.time())}"

        resp = requests.get(url, headers=HEADERS, timeout=30)
        soup = BeautifulSoup(resp.content, 'html.parser')

        # ── Title ────────────────────────────────────
        t = soup.find('h1', class_='page-title')
        if t:
            d['title'] = clean(t.text)

        # ── IMDb score ───────────────────────────────
        imdb = soup.find('span', class_='imdb-score')
        if imdb:
            d['imdb'] = clean(imdb.text)

        # ── Poster ───────────────────────────────────
        poster_div = soup.find('div', class_='poster-image')
        if poster_div:
            img = poster_div.find('img')
            if img:
                d['poster'] = img.get('src', '')

        # ── Overview ─────────────────────────────────
        ov = soup.find('p', class_='mt-4')
        if ov:
            d['overview'] = clean(ov.text)[:500]

        # ── Genres ───────────────────────────────────
        for badge in soup.find_all('span', class_='badge-outline'):
            a = badge.find('a')
            if a:
                d['genres'].append(clean(a.text))

        # ── Metadata items ───────────────────────────
        for item in soup.find_all('div', class_='metadata-item'):
            lbl = item.find('span', class_='metadata-label')
            val = item.find('span', class_='metadata-value')
            if lbl and val:
                k = clean(lbl.text).rstrip(':').lower()
                v = clean(val.text)
                if 'star'   in k: d['stars']    = v
                elif 'air'  in k: d['last_air'] = v
                elif 'print'in k: d['quality']  = v
                elif 'audio'in k: d['audio']    = v
                elif 'season'in k:d['seasons']  = v

        # ── Detect movie vs series ───────────────────
        series_tabs = soup.find('div', class_='series-tabs')
        has_packs   = soup.find('div', id='complete-pack')
        has_eps     = soup.find('div', id='episodes')

        if not series_tabs and not has_packs and not has_eps:
            d['is_movie'] = True
            _parse_movie_downloads(soup, d)
            return d

        # ── Series: ZIP packs ────────────────────────
        if has_packs:
            _parse_packs(has_packs, d)

        # ── Series: individual episodes ──────────────
        if has_eps:
            _parse_episodes(has_eps, d)

    except Exception as e:
        print(f"[detail_scraper] {e}")
        return None

    return d


# ─── Private helpers ─────────────────────────

def _parse_movie_downloads(soup, d: dict) -> None:
    for item in soup.find_all('div', class_='download-item'):
        dl = {}
        hdr = item.find('div', class_='download-header')
        if hdr:
            flex = hdr.find('div', class_='flex-1')
            if flex:
                code = flex.find('code')
                if code:
                    for b in code.find_all('span', class_='badge'):
                        txt, st = clean(b.text), b.get('style', '')
                        if '#ea580c' in st: dl['size']  = txt
                        elif '#0d9488' in st: dl['audio'] = txt
        cnt = item.find('div', id=lambda x: x and x.startswith('content-file'))
        if cnt:
            ft = cnt.find('div', class_='file-title')
            if ft: dl['filename'] = clean(ft.text)
            for b in cnt.find_all('span', class_='badge'):
                txt, st = clean(b.text), b.get('style', '')
                if '#1e40af' in st: dl['quality'] = txt
                elif '#7e22ce' in st: dl['codec']  = txt
            for link in cnt.find_all('a', class_='btn'):
                lt   = clean(link.get_text().replace('\xa0', ' '))
                href = link.get('href', '')
                if href:
                    if 'hubcloud' in lt.lower(): dl['hc'] = href
                    elif 'hubdrive' in lt.lower(): dl['hd'] = href
        if dl and dl.get('filename'):
            d['movie_downloads'].append(dl)


def _parse_packs(has_packs, d: dict) -> None:
    for item in has_packs.find_all('div', class_='download-item'):
        p = {}
        hdr = item.find('div', class_='download-header')
        if hdr:
            sn = hdr.find('div', class_='episode-number')
            if sn: p['season'] = clean(sn.text)
            flex = hdr.find('div', class_='flex-1')
            if flex:
                title_text = ""
                for child in flex.children:
                    if isinstance(child, str):
                        t = clean(child)
                        if t and len(t) > 5:
                            title_text = t
                            break
                    elif child.name == 'br':
                        break
                if not title_text:
                    continue
                p['title'] = title_text
                code = flex.find('code')
                if code:
                    for b in code.find_all('span', class_='badge'):
                        txt, st = clean(b.text), b.get('style', '')
                        if '#ea580c' in st: p['size']   = txt
                        elif '#0d9488' in st: p['audio'] = txt
                        elif '#15803d' in st: p['source']= txt
        cnt = item.find('div', id=lambda x: x and x.startswith('content-file'))
        if cnt:
            ft = cnt.find('div', class_='file-title')
            if ft: p['filename'] = clean(ft.text)
            for b in cnt.find_all('span', class_='badge'):
                txt, st = clean(b.text), b.get('style', '')
                if '#1e40af' in st: p['quality'] = txt
                elif '#7e22ce' in st: p['codec']  = txt
            for link in cnt.find_all('a', class_='btn'):
                lt   = clean(link.get_text().replace('\xa0', ' '))
                href = link.get('href', '')
                if href:
                    if 'hubcloud' in lt.lower(): p['hc'] = href
                    elif 'hubdrive' in lt.lower(): p['hd'] = href
        if p and (p.get('filename') or p.get('hc') or p.get('hd')):
            if not p.get('audio'):
                p['audio'] = d.get('audio', 'N/A')
            d['packs'].append(p)


def _parse_episodes(has_eps, d: dict) -> None:
    for grp in has_eps.find_all('div', class_='episode-item'):
        g = {'episodes': []}
        hdr = grp.find('div', class_='episode-header')
        if hdr:
            sn = hdr.find('div', class_='episode-number')
            if sn: g['season'] = clean(sn.text)
            info = hdr.find('div', class_='episode-info')
            if info:
                h3 = info.find('h3', class_='episode-title')
                if h3: g['label'] = clean(h3.text)
                for b in info.find_all('span', class_='badge'):
                    txt = clean(b.text)
                    if 'Episode' in txt: g['count'] = txt

        cnt = grp.find('div', id=lambda x: x and x.startswith('content-'))
        if cnt:
            for ep_item in cnt.find_all('div', class_='episode-download-item'):
                e = {}
                ft = ep_item.find('div', class_='episode-file-title')
                if ft: e['filename'] = clean(ft.text)
                inf = ep_item.find('div', class_='episode-file-info')
                if inf:
                    nb = inf.find('span', class_='badge-psa')
                    if nb: e['number'] = extract_number(clean(nb.text))
                    sb = inf.find('span', class_='badge-size')
                    if sb: e['size'] = clean(sb.text)
                if not e.get('number'):
                    fn = e.get('filename', '')
                    m = re.search(r'[SE](\d{2,3})', fn, re.IGNORECASE)
                    if m: e['number'] = m.group(1)
                for link in ep_item.find_all('a', class_='btn-sm'):
                    lt   = clean(link.get_text().replace('\xa0', ' '))
                    href = link.get('href', '')
                    if href:
                        if 'hubcloud' in lt.lower(): e['hc'] = href
                        elif 'hubdrive' in lt.lower(): e['hd'] = href
                if e:
                    g['episodes'].append(e)

        if g['episodes']:
            audio_set = set()
            for ep in g['episodes']:
                fn = ep.get('filename', '')
                for lang in ['Hindi', 'English', 'Chinese', 'Tamil', 'Telugu']:
                    if lang.lower() in fn.lower():
                        audio_set.add(lang)
            if not audio_set:
                for lang in ['Hindi', 'English', 'Chinese']:
                    if lang.lower() in d.get('audio', '').lower():
                        audio_set.add(lang)
            g['audio'] = ', '.join(sorted(audio_set)) if audio_set else d.get('audio', 'N/A')
            d['episodes'].append(g)
