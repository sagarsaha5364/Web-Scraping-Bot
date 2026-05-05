# ============================================
# 📄 UTILS/PAGINATION.PY — Message Splitter
# Splits long messages into Telegram-safe pages
# ============================================

MAX_LEN = 3800  # safe below Telegram's 4096 char limit


def split_message(text: str, max_len: int = MAX_LEN) -> list[str]:
    """Split text into pages that fit Telegram's message limit."""
    if len(text) <= max_len:
        return [text]

    pages, current = [], ""
    for line in text.split('\n'):
        if len(current) + len(line) + 1 > max_len:
            pages.append(current.strip())
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        pages.append(current.strip())
    return pages
