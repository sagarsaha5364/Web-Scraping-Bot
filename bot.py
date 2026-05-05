# ============================================
# 🤖 BOT.PY — Telegram Client & Shared State
# ============================================
import os, time
from telethon import TelegramClient, Button
from telethon.sessions import StringSession
from config import API_ID, API_HASH, BOT_TOKEN, ADMIN_ID, SESSION_FILE
from utils.image import download_image_bytes


# ─── Session ─────────────────────────────────
def get_session() -> StringSession:
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            s = f.read().strip()
            if s:
                return StringSession(s)
    return StringSession()


def save_session(session_str: str) -> None:
    with open(SESSION_FILE, 'w') as f:
        f.write(session_str)


# ─── Client ──────────────────────────────────
session = get_session()
bot     = TelegramClient(session, API_ID, API_HASH)


# ─── Context store (per-user navigation state) ──
ctx_store: dict = {}

class Ctx:
    """Holds the current search/navigation state for one user."""
    def __init__(self):
        self.query   = ""
        self.results = []
        self.keys    = []
        self.page    = 1
        self.detail  = None
        self.season  = None
        self.gidx    = 0
        self.epp     = 1
        self.all_eps = []
        self.label   = ""

def ctx(uid: int) -> Ctx:
    if uid not in ctx_store:
        ctx_store[uid] = Ctx()
    return ctx_store[uid]


# ─── Result store (maps short key → full post) ──
result_store:  dict = {}
store_counter: int  = 0

def store_result(post: dict) -> str:
    global store_counter
    store_counter += 1
    key = str(store_counter)
    result_store[key] = post
    return key

def get_stored(key: str) -> dict | None:
    return result_store.get(key)


# ─── Navigation menus ────────────────────────
MAIN = [
    [Button.inline("🔍 Search",          b"ms"), Button.inline("📋 Latest",          b"ml")],
    [Button.inline("🔄 Refresh",         b"mr"), Button.inline("📊 Status",          b"mst")],
    [Button.inline("📥 How to Download", b"howto"), Button.inline("ℹ️ Help",         b"mh")],
]

ADMIN_BTNS = [
    [Button.inline("🔍 Search",          b"ms"), Button.inline("📋 Latest",          b"ml")],
    [Button.inline("🔄 Refresh",         b"mr"), Button.inline("📊 Status",          b"mst")],
    [Button.inline("📥 How to Download", b"howto"), Button.inline("👑 Admin",        b"ma")],
    [Button.inline("ℹ️ Help",            b"mh")],
]

def menu_for(uid: int):
    return ADMIN_BTNS if uid == ADMIN_ID else MAIN


# ─── Poster sender ───────────────────────────
async def send_poster(event, poster_url: str, caption: str = "", buttons=None) -> bool:
    """Download and send a poster image. Returns True on success."""
    if not poster_url or not poster_url.startswith('http'):
        return False
    img_bytes = download_image_bytes(poster_url)
    if not img_bytes:
        return False
    temp_file = f"poster_{int(time.time())}.jpg"
    try:
        with open(temp_file, 'wb') as f:
            f.write(img_bytes)
        await bot.send_file(
            event.chat_id,
            temp_file,
            caption=caption or "",
            buttons=buttons or None,
            parse_mode='html' if caption else None,
        )
        return True
    except Exception as e:
        print(f"[send_poster] {e}")
        return False
    finally:
        try:
            os.remove(temp_file)
        except Exception:
            pass
