# ============================================
# ⚙️ CONFIG.PY — Bot Configuration
# 🎬 Sseries_Area Bot
# ============================================
# To add a new website source, add its BASE_URL
# here and create a matching scraper in scraper/

# ─── Telegram Credentials ───────────────────
API_ID      = 29691930
API_HASH    = "d4fee910d5eac3e9c99889e434ffec77"
BOT_TOKEN   = "6320753534:AAHmrh_Nr5_T1X1IJnjXn9k9RIskH1fXnys"
ADMIN_ID    = 6687248633

# ─── Branding ───────────────────────────────
BOT_NAME    = "Sseries_Area"
BOT_VERSION = "v1.0"
BOT_HANDLE  = "@Sseries_Area"

# ─── Sources (add more websites here) ───────
SOURCES = {
    "4khdhub": {
        "name":     "4K HDHub",
        "base_url": "https://4khdhub.click",
        "enabled":  True,
    },
    # To add another site later:
    # "example": {
    #     "name":     "Example Site",
    #     "base_url": "https://example.com",
    #     "enabled":  True,
    # },
}

# Active source (change key to switch default site)
ACTIVE_SOURCE = "4khdhub"
BASE_URL      = SOURCES[ACTIVE_SOURCE]["base_url"]

# ─── File Paths ──────────────────────────────
JSON_FILE    = "cache.json"
SESSION_FILE = "session_string.txt"
USERS_FILE   = "users.json"
BANNED_FILE  = "banned.json"
SETTINGS_FILE = "settings.json"

# ─── HTTP Headers ────────────────────────────
HEADERS = {
    'User-Agent':      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept':          'text/html,application/xhtml+xml,application/xml;q=0.9',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cache-Control':   'no-cache',
}

# ─── Cache TTL (hours) ───────────────────────
CACHE_TTL_HOURS = 24
