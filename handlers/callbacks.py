# ============================================
# 🎛️ HANDLERS/CALLBACKS.PY — Inline Buttons
# All CallbackQuery handlers live here.
# ============================================
from telethon import events, Button
from config import ADMIN_ID, BASE_URL, BOT_HANDLE
from bot import bot, ctx, menu_for, get_stored, send_poster
from middleware.fsub import check_fsub
from utils.cache import get_cached, set_cached
from utils.formatters import fmt_result, fmt_header, fmt_movie_downloads, fmt_packs, fmt_one_ep, HOW_TO
from utils.pagination import split_message
from scraper.detail_scraper import scrape_detail
from scraper.helpers import check_web
from handlers.commands import do_refresh, show_latest, _send_results_page


# ─── FSub re-check ───────────────────────────
@bot.on(events.CallbackQuery(pattern=b"fsub_check"))
async def fsub_check(event):
    if await check_fsub(bot, event):
        await event.edit("<b>✅ Verified! You're good.</b>", buttons=menu_for(event.sender_id), parse_mode='html')
    else:
        await event.answer("❌ Not joined yet!")


# ─── How-to ──────────────────────────────────
@bot.on(events.CallbackQuery(pattern=b"howto"))
async def howto_btn(event):
    await event.answer("📥")
    await event.respond(HOW_TO, parse_mode='html')


# ─── Result pagination ───────────────────────
@bot.on(events.CallbackQuery(pattern=b"pg_(\\d+)"))
async def pg(event):
    pg_num = int(event.data.decode().split('_')[1])
    c = ctx(event.sender_id)
    c.page = pg_num
    results = c.results
    total   = max(1, (len(results) + 9) // 10)
    start   = (pg_num - 1) * 10
    pg_r    = results[start:start + 10]

    lines = [
        f"🔍 <b>{c.query}</b>",
        f"📄 {pg_num}/{total}  |  {len(results)} results",
        "─" * 30, "",
    ]
    for i, r in enumerate(pg_r, start + 1):
        lines.append(fmt_result(r, i))

    btns = [
        [Button.inline(f"📥 {i}. {r.get('title','?')[:30]}", f"dt_{c.keys[i-1]}")]
        for i, r in enumerate(pg_r, start + 1)
    ]
    if pg_num > 1:     btns.insert(0, [Button.inline("⬅️ Prev", f"pg_{pg_num-1}")])
    if pg_num < total: btns.insert(0, [Button.inline("Next ➡️", f"pg_{pg_num+1}")])
    btns.append([Button.inline("🔙 Menu", b"mn")])
    await event.edit("\n".join(lines), buttons=btns, parse_mode='html')


# ─── Detail page ─────────────────────────────
@bot.on(events.CallbackQuery(pattern=b"dt_(.+)"))
async def dt(event):
    key  = event.data.decode().replace('dt_', '')
    post = get_stored(key)
    if not post:
        await event.answer("❌ Expired")
        return

    url    = post.get('url', f"{BASE_URL}/{post.get('slug', '')}/")
    await event.answer("⏳")
    st     = await event.respond("<i>⏳ Fetching details…</i>", parse_mode='html')
    detail = scrape_detail(url) if check_web() else get_cached(url)
    if detail and check_web():
        set_cached(url, detail)
    if not detail:
        detail = get_cached(url)
    if not detail:
        await st.delete()
        await event.respond("<b>⚠️ Not available right now.</b>", buttons=menu_for(event.sender_id), parse_mode='html')
        return

    c = ctx(event.sender_id)
    c.detail = detail
    poster   = detail.get('poster', '')
    hdr      = fmt_header(detail)

    # ── Movie ────────────────────────────────
    if detail.get('is_movie'):
        dl_text   = fmt_movie_downloads(detail.get('movie_downloads', []))
        full_text = hdr + "\n\n" + dl_text
        await st.delete()
        short = f"<b>🎬 {detail.get('title','?')}</b>"
        if detail.get('imdb'):
            short += f"\n⭐ IMDb: {detail['imdb']}"
        await send_poster(event, poster, short)
        pages = split_message(full_text)
        if len(pages) > 1:
            await event.respond(
                f"📄 Page 1/{len(pages)}\n{'─'*30}\n\n{pages[0]}",
                buttons=[[Button.inline("Next ➡️", b"pgx_2")]] + menu_for(event.sender_id),
                parse_mode='html',
            )
        else:
            await event.respond(full_text, buttons=menu_for(event.sender_id), parse_mode='html')
        return

    # ── Series: season selector ──────────────
    packs    = detail.get('packs', [])
    episodes = detail.get('episodes', [])
    seasons  = sorted(set(
        [p.get('season') for p in packs    if p.get('season')] +
        [g.get('season') for g in episodes if g.get('season')]
    )) or ['S01']

    caption = hdr + "\n\n<b>📺 Select a Season:</b>"
    btns    = []
    for s in seasons:
        pc = len([p for p in packs    if p.get('season') == s])
        ec = len([g for g in episodes if g.get('season') == s])
        btns.append([Button.inline(f"📺 {s}  ┃  📦{pc}  📝{ec}", f"sn_{s}")])
    btns.append([Button.inline("🔙 Back", b"bk"), Button.inline("📋 Menu", b"mn")])

    await st.delete()
    if not await send_poster(event, poster, caption, btns):
        await event.respond(caption, buttons=btns, parse_mode='html')


# ─── Season menu ─────────────────────────────
@bot.on(events.CallbackQuery(pattern=b"sn_(.+)"))
async def sn(event):
    season = event.data.decode().replace('sn_', '')
    c      = ctx(event.sender_id)
    c.season = season
    detail = c.detail
    if not detail:
        await event.edit("<b>❌ Session expired!</b>", buttons=menu_for(event.sender_id), parse_mode='html')
        return

    packs      = [p for p in detail.get('packs',    []) if p.get('season') == season]
    eps        = [g for g in detail.get('episodes', []) if g.get('season') == season]
    total_eps  = sum(len(g['episodes']) for g in eps)
    lines = [
        f"<b>🎬 {detail.get('title','?')}  —  {season}</b>",
        "─" * 30, "",
        f"📦 <b>ZIP packs:</b> {len(packs)}",
        f"📝 <b>Single EPs:</b> {len(eps)} quality groups ({total_eps} eps)",
        "",
        "<b>👇 Choose:</b>",
    ]
    btns = []
    if packs: btns.append([Button.inline(f"📦 ZIP / Season Packs  ({len(packs)})",           f"pk_{season}")])
    if eps:   btns.append([Button.inline(f"📝 Single Episodes  ({len(eps)} quality groups)", f"ql_{season}")])
    btns.append([Button.inline("🔙 Seasons", b"bs"), Button.inline("📋 Menu", b"mn")])
    await event.edit("\n".join(lines), buttons=btns, parse_mode='html')


# ─── Quality group selector ───────────────────
@bot.on(events.CallbackQuery(pattern=b"ql_(.+)"))
async def ql(event):
    season = event.data.decode().replace('ql_', '')
    c      = ctx(event.sender_id)
    detail = c.detail
    if not detail:
        await event.edit("<b>❌</b>", buttons=menu_for(event.sender_id), parse_mode='html')
        return

    eps       = [g for g in detail.get('episodes', []) if g.get('season') == season]
    total_eps = sum(len(g['episodes']) for g in eps)
    lines = [
        f"<b>📝 {season}  —  Quality Groups</b>",
        f"📊 {len(eps)} groups  |  {total_eps} eps total",
        "─" * 30, "",
        "<b>Select a quality group:</b>",
    ]
    btns = []
    for i, g in enumerate(eps):
        label    = g.get('label', '')[:45]
        ep_count = len(g['episodes'])
        audio    = g.get('audio', '')
        txt      = f"🎥 {label}  ({ep_count} eps)"
        if audio: txt += f"  🔊{audio}"
        btns.append([Button.inline(txt[:55], f"ep_{season}_{i}_1")])
    btns.append([Button.inline(f"🔙 {season}", f"sn_{season}"), Button.inline("📋 Menu", b"mn")])
    await event.edit("\n".join(lines), buttons=btns, parse_mode='html')


# ─── Episode list (paginated) ─────────────────
@bot.on(events.CallbackQuery(pattern=b"ep_(.+)_(\\d+)_(\\d+)"))
async def ep_list(event):
    parts  = event.data.decode().split('_')
    season = parts[1]
    idx    = int(parts[2])
    page   = int(parts[3])
    c      = ctx(event.sender_id)
    c.season = season; c.gidx = idx; c.epp = page
    detail = c.detail
    if not detail:
        await event.edit("<b>❌</b>", buttons=menu_for(event.sender_id), parse_mode='html')
        return

    eps   = [g for g in detail.get('episodes', []) if g.get('season') == season]
    if idx >= len(eps):
        await event.answer("Group not found!")
        return

    group    = eps[idx]
    c.all_eps = group['episodes']
    c.label   = group.get('label', '')
    all_eps   = group['episodes']
    per_page  = 15
    total_pg  = max(1, (len(all_eps) + per_page - 1) // per_page)
    start     = (page - 1) * per_page
    page_eps  = all_eps[start:start + per_page]

    lines = [
        f"<b>📝 {season}  —  {group.get('label','')[:50]}</b>",
        f"📊 {group.get('count','')}  |  🔊 {group.get('audio','N/A')}",
        f"📄 Page {page}/{total_pg}  |  {len(all_eps)} eps total",
        "─" * 30, "",
        "<b>Tap an episode to get its link:</b>",
    ]
    btns, row = [], []
    for i, ep in enumerate(page_eps):
        num = ep.get('number', '')
        num = num.zfill(2) if num and num.isdigit() else '??'
        row.append(Button.inline(f"{season}E{num}", f"dl_{season}_{idx}_{start+i}"))
        if len(row) == 4:
            btns.append(row); row = []
    if row: btns.append(row)

    if page > 1:      btns.append([Button.inline("⬅️ Prev", f"ep_{season}_{idx}_{page-1}")])
    if page < total_pg: btns.append([Button.inline("Next ➡️", f"ep_{season}_{idx}_{page+1}")])
    btns.append([Button.inline(f"📋 View all links ({len(all_eps)} eps)", f"va_{season}_{idx}_1")])
    btns.append([Button.inline("🔙 Qualities", f"ql_{season}"), Button.inline("📋 Menu", b"mn")])
    await event.edit("\n".join(lines), buttons=btns, parse_mode='html')


# ─── Single episode download ──────────────────
@bot.on(events.CallbackQuery(pattern=b"dl_(.+)_(\\d+)_(\\d+)"))
async def dl_ep(event):
    parts  = event.data.decode().split('_')
    season = parts[1]
    gidx   = int(parts[2])
    epidx  = int(parts[3])
    c      = ctx(event.sender_id)
    detail = c.detail
    if not detail:
        await event.answer("❌"); return

    eps = [g for g in detail.get('episodes', []) if g.get('season') == season]
    if gidx >= len(eps):
        await event.answer("!"); return

    group = eps[gidx]
    ep    = group['episodes'][epidx]
    num   = ep.get('number', '??')
    num   = num.zfill(2) if num.isdigit() else num

    msg = (
        f"<b>📥 {season}E{num}</b>\n"
        f"<b>Quality:</b> {group.get('label','')}\n"
        f"<b>Audio:</b> {group.get('audio','N/A')}\n"
        f"<b>Source:</b> {BOT_HANDLE}\n"
        "─" * 30 + "\n\n" +
        fmt_one_ep(ep)
    )
    btns = []
    if ep.get('hc'): btns.append([Button.url("☁️ HubCloud", ep['hc'])])
    if ep.get('hd'): btns.append([Button.url("💾 HubDrive",  ep['hd'])])
    btns.append([Button.inline(f"🔙 {season}", f"ep_{season}_{gidx}_{c.epp}"), Button.inline("📋 Menu", b"mn")])
    await event.edit(msg, buttons=btns, parse_mode='html')


# ─── View-all episodes (text list) ───────────
@bot.on(events.CallbackQuery(pattern=b"va_(.+)_(\\d+)_(\\d+)"))
async def va(event):
    parts  = event.data.decode().split('_')
    season = parts[1]
    gidx   = int(parts[2])
    page   = int(parts[3])
    c      = ctx(event.sender_id)
    detail = c.detail
    if not detail:
        await event.edit("<b>❌</b>", buttons=menu_for(event.sender_id), parse_mode='html')
        return

    eps = [g for g in detail.get('episodes', []) if g.get('season') == season]
    if gidx >= len(eps):
        await event.answer("!"); return

    group     = eps[gidx]
    all_eps   = group['episodes']
    per_page  = 8
    total_pg  = max(1, (len(all_eps) + per_page - 1) // per_page)
    start     = (page - 1) * per_page
    page_eps  = all_eps[start:start + per_page]

    lines = [
        f"<b>📋 {season}  —  {group.get('label','')[:50]}</b>",
        f"🔊 {group.get('audio','N/A')}  |  📄 {page}/{total_pg}  |  {len(all_eps)} eps",
        "─" * 30,
    ]
    for ep in page_eps:
        lines.append(f"\n{fmt_one_ep(ep)}")
        lines.append("─" * 20)

    btns = []
    if page > 1:       btns.append([Button.inline("⬅️ Prev", f"va_{season}_{gidx}_{page-1}")])
    if page < total_pg:btns.append([Button.inline("Next ➡️", f"va_{season}_{gidx}_{page+1}")])
    btns.append([Button.inline("🔙 Episodes", f"ep_{season}_{gidx}_1"), Button.inline("📋 Menu", b"mn")])

    full = "\n".join(lines)
    if len(full) > 4000:
        chunks = [full[i:i+3800] for i in range(0, len(full), 3800)]
        await event.edit(chunks[0], buttons=btns, parse_mode='html')
        for chunk in chunks[1:]:
            await event.respond(chunk, parse_mode='html')
    else:
        await event.edit(full, buttons=btns, parse_mode='html')


# ─── Back to season list ──────────────────────
@bot.on(events.CallbackQuery(pattern=b"bs$"))
async def bs(event):
    c = ctx(event.sender_id)
    detail = c.detail
    if not detail:
        await event.edit("<b>❌</b>", buttons=menu_for(event.sender_id), parse_mode='html')
        return
    packs    = detail.get('packs', [])
    episodes = detail.get('episodes', [])
    seasons  = sorted(set(
        [p.get('season') for p in packs    if p.get('season')] +
        [g.get('season') for g in episodes if g.get('season')]
    )) or ['S01']
    caption = fmt_header(detail) + "\n\n<b>📺 Select a Season:</b>"
    btns    = []
    for s in seasons:
        pc = len([p for p in packs    if p.get('season') == s])
        ec = len([g for g in episodes if g.get('season') == s])
        btns.append([Button.inline(f"📺 {s}  ┃  📦{pc}  📝{ec}", f"sn_{s}")])
    btns.append([Button.inline("🔙 Back", b"bk"), Button.inline("📋 Menu", b"mn")])
    await event.edit(caption, buttons=btns, parse_mode='html')


# ─── ZIP packs ───────────────────────────────
@bot.on(events.CallbackQuery(pattern=b"pk_(.+)"))
async def pk(event):
    season = event.data.decode().replace('pk_', '')
    c      = ctx(event.sender_id)
    detail = c.detail
    if not detail:
        await event.edit("<b>❌</b>", buttons=menu_for(event.sender_id), parse_mode='html')
        return
    msg  = fmt_packs(detail.get('packs', []), season)
    btns = [[Button.inline(f"🔙 {season}", f"sn_{season}"), Button.inline("📋 Menu", b"mn")]]
    if len(msg) > 4000:
        chunks = [msg[i:i+3800] for i in range(0, len(msg), 3800)]
        await event.edit(chunks[0], buttons=btns, parse_mode='html')
        for chunk in chunks[1:]:
            await event.respond(chunk, parse_mode='html')
    else:
        await event.edit(msg, buttons=btns, parse_mode='html')


# ─── Back to search results ───────────────────
@bot.on(events.CallbackQuery(pattern=b"bk$"))
async def bk(event):
    c = ctx(event.sender_id)
    if c.results:
        pg_num  = c.page
        results = c.results
        total   = max(1, (len(results) + 9) // 10)
        start   = (pg_num - 1) * 10
        pg_r    = results[start:start + 10]
        lines   = [f"🔍 <b>{c.query}</b>", f"📄 {pg_num}/{total}", "─" * 30, ""]
        for i, x in enumerate(pg_r, start + 1):
            lines.append(fmt_result(x, i))
        btns = [
            [Button.inline(f"📥 {i}. {x.get('title','?')[:30]}", f"dt_{c.keys[i-1]}")]
            for i, x in enumerate(pg_r, start + 1)
        ]
        if pg_num > 1:    btns.insert(0, [Button.inline("⬅️", f"pg_{pg_num-1}")])
        if pg_num < total:btns.insert(0, [Button.inline("➡️", f"pg_{pg_num+1}")])
        btns.append([Button.inline("🔙 Menu", b"mn")])
        await event.edit("\n".join(lines), buttons=btns, parse_mode='html')
    else:
        await event.edit("<b>📌 Main Menu</b>", buttons=menu_for(event.sender_id), parse_mode='html')


# ─── Menu / utility buttons ──────────────────
@bot.on(events.CallbackQuery(pattern=b"mn$"))
async def mn(event):
    await event.edit("<b>📌 Main Menu</b>", buttons=menu_for(event.sender_id), parse_mode='html')

@bot.on(events.CallbackQuery(pattern=b"ms$"))
async def ms(event):
    await event.edit(
        "<b>🔍 Send a title to search:</b>",
        buttons=[[Button.inline("❌ Cancel", b"mn")]],
        parse_mode='html',
    )

@bot.on(events.CallbackQuery(pattern=b"ml$"))
async def ml(event):
    await event.answer("⏳")
    await show_latest(event)

@bot.on(events.CallbackQuery(pattern=b"mr$"))
async def mr(event):
    await event.answer("⏳")
    await do_refresh(event)

@bot.on(events.CallbackQuery(pattern=b"mst$"))
async def mst(event):
    from handlers.commands import status_cmd
    await status_cmd(event)

@bot.on(events.CallbackQuery(pattern=b"mh$"))
async def mh(event):
    await event.edit(
        "<b>📚 Help  |  @Sseries_Area</b>\n\n"
        "/search /latest /refresh /status\n"
        "/howtodownload",
        buttons=menu_for(event.sender_id),
        parse_mode='html',
    )

@bot.on(events.CallbackQuery(pattern=b"ma$"))
async def ma(event):
    if event.sender_id != ADMIN_ID:
        await event.answer("❌ Admins only!")
        return
    from bot import ADMIN_BTNS
    await event.edit(
        "<b>👑 Admin Panel</b>\n\n"
        "/users /ban /unban /broadcast\n"
        "/fsub on|off /setfsub /removefsub",
        buttons=ADMIN_BTNS,
        parse_mode='html',
    )
