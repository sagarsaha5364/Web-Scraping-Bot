# ============================================
# 💬 HANDLERS/COMMANDS.PY — User Commands
# /start /search /latest /refresh /status /help
# ============================================
from telethon import events, Button
from config import ADMIN_ID, BASE_URL, BOT_NAME, BOT_VERSION, BOT_HANDLE
from bot import bot, ctx, menu_for, store_result, send_poster
from middleware.auth import check_access, track
from utils.cache import get_cached, set_cached, cache_size, load_cache
from utils.formatters import fmt_result, fmt_header, fmt_movie_downloads, HOW_TO
from utils.pagination import split_message
from scraper.list_scraper import scrape_list
from scraper.detail_scraper import scrape_detail
from scraper.helpers import check_web, auto_fetch_all


# ─── /start ──────────────────────────────────
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    if not await check_access(bot, event): return
    await track(bot, event)
    await event.respond(
        f"<b>🎬 {BOT_NAME} {BOT_VERSION}</b>  |  {BOT_HANDLE}\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>👋 Welcome, {event.sender.first_name}!</b>\n\n"
        "✨ Movies → Direct Downloads\n"
        "📺 Series → Seasons → Episodes\n"
        "🖼️ Poster + Clickable Links\n"
        "📦 ZIP + Single EPs\n\n"
        "/search | /latest | /refresh | /status\n"
        "/howtodownload\n\n"
        "<i>💡 Send any title to search!</i>",
        buttons=menu_for(event.sender_id),
        parse_mode='html',
    )


# ─── /howtodownload ───────────────────────────
@bot.on(events.NewMessage(pattern='/howtodownload'))
async def howto_cmd(event):
    await event.respond(HOW_TO, parse_mode='html')


# ─── /help ───────────────────────────────────
@bot.on(events.NewMessage(pattern='/help'))
async def help_cmd(event):
    if not await check_access(bot, event): return
    await track(bot, event)
    await event.respond(
        "<b>📚 Help</b>\n\n"
        "/search /latest /refresh /status\n"
        "/howtodownload",
        buttons=menu_for(event.sender_id),
        parse_mode='html',
    )


# ─── /search ─────────────────────────────────
@bot.on(events.NewMessage(pattern='/search(?: (.+))?'))
async def search_cmd(event):
    if not await check_access(bot, event): return
    await track(bot, event)
    q = event.pattern_match.group(1)
    if q:
        await do_search(event, q)
    else:
        await event.respond(
            "<b>🔍 Send a title to search:</b>",
            buttons=[[Button.inline("❌ Cancel", b"mn")]],
            parse_mode='html',
        )


# ─── /latest ─────────────────────────────────
@bot.on(events.NewMessage(pattern='/latest'))
async def latest_cmd(event):
    if not await check_access(bot, event): return
    await track(bot, event)
    await show_latest(event)


# ─── /refresh ────────────────────────────────
@bot.on(events.NewMessage(pattern='/refresh'))
async def refresh_cmd(event):
    if not await check_access(bot, event): return
    await track(bot, event)
    await do_refresh(event)


# ─── /status ─────────────────────────────────
@bot.on(events.NewMessage(pattern='/status'))
async def status_cmd(event):
    if not await check_access(bot, event): return
    await track(bot, event)
    from utils.storage import count_users, get_setting
    web    = check_web()
    users  = count_users()
    cached = cache_size()
    fsub   = get_setting('fsub_enabled', False)
    await event.respond(
        f"<b>📊 Status  |  {BOT_HANDLE}</b>\n\n"
        f"🌐 {'✅ Online' if web else '❌ Offline'}\n"
        f"📦 Cached: {cached}\n"
        f"👥 Users: {users}\n"
        f"🔒 FSub: {'✅ On' if fsub else '❌ Off'}\n"
        f"⚡ Running",
        buttons=menu_for(event.sender_id),
        parse_mode='html',
    )


# ─── Plain-text search ────────────────────────
@bot.on(events.NewMessage(func=lambda e: not e.text.startswith('/') and e.text and e.text.strip()))
async def text_search(event):
    if not await check_access(bot, event): return
    await track(bot, event)
    await do_search(event, event.text.strip())


# ─── Search logic ─────────────────────────────
async def do_search(event, q: str):
    c = ctx(event.sender_id)
    c.query, c.page = q, 1

    st = await event.respond(f"<i>🔍 Searching: {q}…</i>", parse_mode='html')

    if check_web():
        results = scrape_list(f"{BASE_URL}/?s={q.replace(' ', '+')}")
        if not results:
            # Fall back to homepage partial match
            results = [
                p for p in scrape_list(BASE_URL)
                if q.lower() in p.get('title', '').lower()
            ]
        for r in results:
            if not get_cached(r['url']):
                set_cached(r['url'], {'title': r['title'], 'url': r['url'], 'poster': r.get('poster', '')})
    else:
        results = [
            item.get('data', item)
            for item in load_cache().values()
            if q.lower() in item.get('data', item).get('title', '').lower()
        ]

    if not results:
        await st.delete()
        await event.respond(
            f"<b>❌ No results for:</b> {q}",
            buttons=menu_for(event.sender_id),
            parse_mode='html',
        )
        return

    c.keys    = [store_result(r) for r in results]
    c.results = results
    await _send_results_page(event, st, c, 1)


async def show_latest(event):
    st = await event.respond("<i>📋 Fetching latest…</i>", parse_mode='html')
    if check_web():
        results = scrape_list(BASE_URL)
        for r in results:
            set_cached(r['url'], {'title': r['title'], 'url': r['url'], 'poster': r.get('poster', '')})
    else:
        results = [item.get('data', item) for item in load_cache().values()][:20]

    if not results:
        await st.delete()
        await event.respond("<b>❌ No posts found!</b>", buttons=menu_for(event.sender_id), parse_mode='html')
        return

    c = ctx(event.sender_id)
    c.results, c.query, c.page = results, "Latest", 1
    c.keys = [store_result(r) for r in results]
    await _send_results_page(event, st, c, 1)


async def do_refresh(event):
    if not check_web():
        await event.respond("<b>⚠️ Site is offline!</b>", buttons=menu_for(event.sender_id), parse_mode='html')
        return
    st    = await event.respond("<i>🔄 Syncing…</i>", parse_mode='html')
    posts = auto_fetch_all(5)
    await st.delete()
    await event.respond(
        f"<b>✅ {len(posts)} posts cached!</b>",
        buttons=menu_for(event.sender_id),
        parse_mode='html',
    )


# ─── Shared result-page builder ──────────────
async def _send_results_page(event, st_msg, c, pg_num: int):
    results = c.results
    total   = max(1, (len(results) + 9) // 10)
    start   = (pg_num - 1) * 10
    pg      = results[start:start + 10]

    lines = [
        f"🔍 <b>{c.query}</b>",
        f"📄 {pg_num}/{total}  |  {len(results)} results",
        "─" * 30, "",
    ]
    for i, r in enumerate(pg, start + 1):
        lines.append(fmt_result(r, i))

    btns = [
        [Button.inline(f"📥 {i}. {r.get('title','?')[:30]}", f"dt_{c.keys[i-1]}")]
        for i, r in enumerate(pg, start + 1)
    ]
    if pg_num > 1:    btns.insert(0, [Button.inline("⬅️ Prev", f"pg_{pg_num-1}")])
    if pg_num < total:btns.insert(0, [Button.inline("Next ➡️", f"pg_{pg_num+1}")])
    btns.append([Button.inline("🔙 Menu", b"mn")])

    await st_msg.delete()
    await event.respond("\n".join(lines), buttons=btns, parse_mode='html')
