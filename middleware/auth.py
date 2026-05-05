# ============================================
# 🛡️ MIDDLEWARE/AUTH.PY — Auth & User Tracking
# ============================================
from datetime import datetime, UTC
from utils.storage import save_user, is_banned
from middleware.fsub import check_fsub


async def track(bot, event) -> None:
    """Save/update user info on every interaction."""
    try:
        u = event.sender
        save_user(u.id, {
            'id':   u.id,
            'name': u.first_name or '',
            'user': u.username or '',
            'last': datetime.now(UTC).isoformat(),
        })
    except Exception:
        pass


async def check_banned(event) -> bool:
    """Return True (and notify) if user is banned."""
    if is_banned(event.sender_id):
        await event.respond("<b>🚫 You are banned!</b>", parse_mode='html')
        return True
    return False


async def check_access(bot, event) -> bool:
    """Full access gate: banned check + FSub check."""
    if await check_banned(event):
        return False
    if not await check_fsub(bot, event):
        return False
    return True
