# ============================================
# 👑 HANDLERS/ADMIN.PY — Admin Commands
# /admin /users /ban /unban /broadcast
# /fsub /setfsub /removefsub /clearcache /fetchall
# ============================================
import asyncio
from telethon import events
from config import ADMIN_ID, BOT_HANDLE
from bot import bot, ADMIN_BTNS
from utils.storage import (
    get_all_users, is_banned, ban_user, unban_user,
    load_banned, count_users, get_setting, set_setting,
)
from utils.cache import clear_cache, cache_size, load_cache, set_cached
from scraper.helpers import check_web, auto_fetch_all


def _is_admin(event) -> bool:
    return event.sender_id == ADMIN_ID


# ─── /admin ──────────────────────────────────
@bot.on(events.NewMessage(pattern='/admin'))
async def admin_cmd(event):
    if not _is_admin(event): return
    await event.respond(
        f"<b>👑 Admin Panel  |  {BOT_HANDLE}</b>\n\n"
        "<b>User management:</b>\n"
        "/users | /ban &lt;id&gt; | /unban &lt;id&gt; | /banned\n\n"
        "<b>Broadcast:</b>\n"
        "/broadcast &lt;message&gt;\n\n"
        "<b>Cache / Data:</b>\n"
        "/clearcache | /fetchall | /stats\n\n"
        "<b>Force-Subscribe:</b>\n"
        "/fsub on|off | /setfsub @ch1 @ch2\n"
        "/removefsub | /fsubstatus",
        buttons=ADMIN_BTNS,
        parse_mode='html',
    )


# ─── /users ──────────────────────────────────
@bot.on(events.NewMessage(pattern='/users'))
async def users_cmd(event):
    if not _is_admin(event): return
    users = get_all_users()
    total = len(users)
    msg   = f"<b>👥 Total Users: {total}</b>\n\n"
    for i, (uid, data) in enumerate(list(users.items())[:20], 1):
        flag = "🚫" if is_banned(uid) else "✅"
        msg += f"{i}. {flag} <b>{data.get('name','?')}</b>"
        if data.get('user'):
            msg += f" @{data['user']}"
        msg += f"\n   ID: <code>{uid}</code>\n"
    if total > 20:
        msg += f"\n<i>+ {total - 20} more…</i>"
    await event.respond(msg, parse_mode='html')


# ─── /ban ────────────────────────────────────
@bot.on(events.NewMessage(pattern='/ban (.+)'))
async def ban_cmd(event):
    if not _is_admin(event): return
    try:
        uid = int(event.pattern_match.group(1))
        ban_user(uid)
        await event.respond(f"<b>✅ Banned:</b> <code>{uid}</code>", parse_mode='html')
    except Exception:
        await event.respond("<b>❌ Invalid ID!</b>", parse_mode='html')


# ─── /unban ──────────────────────────────────
@bot.on(events.NewMessage(pattern='/unban (.+)'))
async def unban_cmd(event):
    if not _is_admin(event): return
    try:
        uid = int(event.pattern_match.group(1))
        unban_user(uid)
        await event.respond(f"<b>✅ Unbanned:</b> <code>{uid}</code>", parse_mode='html')
    except Exception:
        await event.respond("<b>❌ Invalid ID!</b>", parse_mode='html')


# ─── /banned ─────────────────────────────────
@bot.on(events.NewMessage(pattern='/banned'))
async def banned_cmd(event):
    if not _is_admin(event): return
    banned = load_banned()
    msg    = f"<b>🚫 Banned Users: {len(banned)}</b>\n\n"
    for uid in list(banned.keys())[:30]:
        msg += f"<code>{uid}</code>\n"
    await event.respond(msg, parse_mode='html')


# ─── /broadcast ──────────────────────────────
@bot.on(events.NewMessage(pattern='/broadcast (.+)'))
async def broadcast_cmd(event):
    if not _is_admin(event): return
    msg_text = event.pattern_match.group(1)
    users    = get_all_users()
    ok = fail = 0
    st = await event.respond("<i>📢 Sending broadcast…</i>", parse_mode='html')
    for uid in users:
        if is_banned(uid):
            continue
        try:
            await bot.send_message(
                int(uid),
                f"<b>📢 {BOT_HANDLE} Broadcast</b>\n\n{msg_text}",
                parse_mode='html',
            )
            ok += 1
            await asyncio.sleep(0.3)
        except Exception:
            fail += 1
    await st.edit(f"<b>✅ Done!</b>  ✅ {ok} sent  ❌ {fail} failed", parse_mode='html')


# ─── /clearcache ─────────────────────────────
@bot.on(events.NewMessage(pattern='/clearcache'))
async def clearcache_cmd(event):
    if not _is_admin(event): return
    clear_cache()
    await event.respond("<b>✅ Cache cleared!</b>", parse_mode='html')


# ─── /fetchall ───────────────────────────────
@bot.on(events.NewMessage(pattern='/fetchall'))
async def fetchall_cmd(event):
    if not _is_admin(event): return
    st    = await event.respond("<i>🔄 Syncing all pages…</i>", parse_mode='html')
    posts = auto_fetch_all(10)
    await st.edit(f"<b>✅ {len(posts)} posts synced!</b>", parse_mode='html')


# ─── /stats ──────────────────────────────────
@bot.on(events.NewMessage(pattern='/stats'))
async def stats_cmd(event):
    if not _is_admin(event): return
    web    = check_web()
    users  = count_users()
    cached = cache_size()
    fsub   = get_setting('fsub_enabled', False)
    await event.respond(
        f"<b>📊 Bot Stats  |  {BOT_HANDLE}</b>\n\n"
        f"🌐 Site: {'✅ Online' if web else '❌ Offline'}\n"
        f"📦 Cached pages: {cached}\n"
        f"👥 Total users: {users}\n"
        f"🔒 FSub: {'✅ On' if fsub else '❌ Off'}\n"
        f"⚡ Status: Running",
        parse_mode='html',
    )


# ─── /fsub on|off ────────────────────────────
@bot.on(events.NewMessage(pattern='/fsub on'))
async def fsub_on(event):
    if not _is_admin(event): return
    set_setting('fsub_enabled', True)
    await event.respond("<b>✅ Force-Subscribe: ON</b>", parse_mode='html')

@bot.on(events.NewMessage(pattern='/fsub off'))
async def fsub_off(event):
    if not _is_admin(event): return
    set_setting('fsub_enabled', False)
    await event.respond("<b>❌ Force-Subscribe: OFF</b>", parse_mode='html')


# ─── /setfsub ────────────────────────────────
@bot.on(events.NewMessage(pattern='/setfsub (.+)'))
async def setfsub_cmd(event):
    if not _is_admin(event): return
    channels = [ch.strip().replace('@', '') for ch in event.pattern_match.group(1).split()]
    set_setting('fsub_channels', channels)
    set_setting('fsub_enabled', True)
    await event.respond(
        "<b>✅ FSub channels set:</b>\n" + "\n".join(f"📢 @{ch}" for ch in channels),
        parse_mode='html',
    )


# ─── /removefsub ─────────────────────────────
@bot.on(events.NewMessage(pattern='/removefsub'))
async def removefsub_cmd(event):
    if not _is_admin(event): return
    set_setting('fsub_channels', [])
    set_setting('fsub_enabled', False)
    await event.respond("<b>✅ All FSub channels removed!</b>", parse_mode='html')


# ─── /fsubstatus ─────────────────────────────
@bot.on(events.NewMessage(pattern='/fsubstatus'))
async def fsubstatus_cmd(event):
    if not _is_admin(event): return
    enabled  = get_setting('fsub_enabled', False)
    channels = get_setting('fsub_channels', [])
    msg = f"<b>🔒 FSub: {'✅ ON' if enabled else '❌ OFF'}</b>\n\n"
    for ch in channels:
        msg += f"📢 @{ch}\n"
    if not channels:
        msg += "<i>No channels set.</i>"
    await event.respond(msg, parse_mode='html')
