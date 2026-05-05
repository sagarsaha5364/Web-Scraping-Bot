# ============================================
# 🚀 MAIN.PY — Entry Point
# Run:  python main.py
# ============================================
import asyncio, os
from bot import bot, session, save_session
from scraper.helpers import check_web, auto_fetch_all
from config import BOT_NAME, BOT_VERSION, BOT_HANDLE

# ── Import all handlers so decorators register ──
import handlers.commands   # noqa: F401
import handlers.callbacks  # noqa: F401
import handlers.admin      # noqa: F401


async def main():
    print("╔══════════════════════════════════════╗")
    print(f"║  🎬 {BOT_NAME} Bot {BOT_VERSION:<22}║")
    print(f"║  {BOT_HANDLE:<38}║")
    print("╚══════════════════════════════════════╝")

    # Clean up stale session files
    for f in os.listdir('.'):
        if f.endswith('.session'):
            os.remove(f)

    await bot.start(bot_token=__import__('config').BOT_TOKEN)
    save_session(session.save())

    me = await bot.get_me()
    print(f"✅ Logged in as @{me.username}")

    # Pre-warm cache
    if check_web():
        posts = auto_fetch_all(5)
        print(f"📥 {len(posts)} posts cached on startup")
    else:
        print("⚠️  Site offline — skipping pre-cache")

    print("🚀 Bot is ready!\n")
    await bot.run_until_disconnected()


if __name__ == '__main__':
    asyncio.run(main())
