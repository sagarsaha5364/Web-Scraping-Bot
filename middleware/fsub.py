# ============================================
# 🔒 MIDDLEWARE/FSUB.PY — Forced Subscription
# Add/remove channels in /setfsub command.
# ============================================
from telethon import Button
from telethon.tl.functions.channels import GetParticipantRequest
from utils.storage import get_setting


async def check_fsub(bot, event) -> bool:
    """
    Returns True if user has joined all required channels (or FSub is off).
    Sends a join prompt and returns False otherwise.
    """
    if not get_setting('fsub_enabled', False):
        return True

    channels = get_setting('fsub_channels', [])
    if not channels:
        return True

    not_joined = []
    for ch in channels:
        try:
            await bot(GetParticipantRequest(ch, event.sender_id))
        except Exception:
            not_joined.append(ch)

    if not_joined:
        btns = [
            [Button.url(f"📢 Join @{ch}", f"https://t.me/{ch}")]
            for ch in not_joined
        ]
        btns.append([Button.inline("✅ Joined! Try Again", b"fsub_check")])
        await event.respond(
            "<b>⚠️ Please join our channels first!</b>\n"
            "<i>Join below, then click 'Joined!'</i>",
            buttons=btns,
            parse_mode='html',
        )
        return False

    return True
