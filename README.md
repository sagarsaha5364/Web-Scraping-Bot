# 🎬 Sseries_Area Bot

Telegram bot to search & download movies/series from 4K HDHub.

**Bot:** [@Sseries_Area](https://t.me/Sseries_Area)

---

## 📁 Project Structure

```
sseries_area_bot/
│
├── main.py                  ← Entry point (run this)
├── bot.py                   ← Telegram client, context store, menus
├── config.py                ← All credentials, URLs & constants
├── requirements.txt
│
├── scraper/
│   ├── helpers.py           ← clean(), check_web(), auto_fetch_all()
│   ├── list_scraper.py      ← Scrapes search/listing pages
│   └── detail_scraper.py    ← Scrapes individual movie/series pages
│
├── handlers/
│   ├── commands.py          ← /start /search /latest /refresh /status
│   ├── callbacks.py         ← All inline button callbacks
│   └── admin.py             ← /admin /ban /broadcast /fsub etc.
│
├── middleware/
│   ├── auth.py              ← Ban check, access gate, user tracking
│   └── fsub.py              ← Force-subscribe channel check
│
└── utils/
    ├── cache.py             ← JSON cache with TTL
    ├── storage.py           ← Users / banned / settings persistence
    ├── image.py             ← Poster image downloader
    ├── formatters.py        ← All message HTML builders
    └── pagination.py        ← Message splitter for long texts
```

---

## 🚀 Setup

```bash
git clone <repo-url>
cd sseries_area_bot
pip install -r requirements.txt
python main.py
```

---

## ✏️ Common edits

| Task | File to edit |
|------|-------------|
| Change bot token / API keys | `config.py` |
| Add a new website source | `config.py` → `SOURCES`, then new file in `scraper/` |
| Change message formatting / branding | `utils/formatters.py` |
| Add a new user command | `handlers/commands.py` |
| Add a new inline button | `handlers/callbacks.py` |
| Add a new admin command | `handlers/admin.py` |
| Change cache duration | `config.py` → `CACHE_TTL_HOURS` |

---

## ➕ Adding a New Website Source

1. Add an entry in `config.py → SOURCES`
2. Duplicate `scraper/list_scraper.py` → e.g. `scraper/list_scraper_site2.py`
3. Adjust CSS selectors for the new site
4. Import and call the new scraper from `handlers/commands.py`

---

## 👑 Admin Commands

| Command | Action |
|---------|--------|
| `/users` | List all users |
| `/ban <id>` | Ban a user |
| `/unban <id>` | Unban a user |
| `/broadcast <msg>` | Send to all users |
| `/clearcache` | Clear scraped cache |
| `/fetchall` | Re-sync all pages |
| `/fsub on\|off` | Toggle force-subscribe |
| `/setfsub @ch1 @ch2` | Set FSub channels |
| `/removefsub` | Remove all FSub channels |
| `/fsubstatus` | Show FSub config |

---

*Branding: @Sseries_Area*
