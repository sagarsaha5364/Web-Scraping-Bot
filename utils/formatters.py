# ============================================
# 🎨 UTILS/FORMATTERS.PY — Message Formatters
# All HTML-formatted message builders live here.
# To change display style, edit ONLY this file.
# ============================================
from config import BOT_HANDLE


# ─── Search result one-liner ─────────────────
def fmt_result(post: dict, num: int) -> str:
    t  = post.get('title', '?')
    y  = post.get('year', '')
    ex = post.get('extra', '')
    line = f"<b>{num}. {t}</b>\n"
    parts = []
    if y:  parts.append(f"📅 {y}")
    if ex: parts.append(ex)
    if parts:
        line += "   " + " | ".join(parts) + "\n"
    return line


# ─── Detail page header ──────────────────────
def fmt_header(d: dict) -> str:
    lines = [f"<b>🎬 {d.get('title', '?')}</b>"]
    if d.get('imdb'):
        lines.append(f"⭐ <b>IMDb: {d['imdb']}</b>")
    if d.get('genres'):
        lines.append('  '.join(
            f"#{g.replace(' ', '_').replace('&', '')}" for g in d['genres']
        ))
    lines.append("─" * 30)
    if d.get('overview'):
        lines.append(f"\n<i>{d['overview'][:300]}...</i>")
    meta = []
    for key, icon in [
        ('stars',    '👥'),
        ('last_air', '📅'),
        ('quality',  '🎥'),
        ('audio',    '🔊'),
        ('seasons',  '📺'),
    ]:
        if d.get(key):
            meta.append(f"{icon} <b>{key.title()}:</b> {d[key]}")
    if meta:
        lines.append("\n" + "\n".join(meta))
    return "\n".join(lines)


# ─── Movie download links ─────────────────────
def fmt_movie_downloads(downloads: list) -> str:
    if not downloads:
        return "<i>No downloads available</i>"
    lines = [
        f"<b>📥 DOWNLOADS</b>",
        f"📊 {len(downloads)} files",
        "─" * 30,
    ]
    for i, dl in enumerate(downloads, 1):
        fn = dl.get('filename', '')
        sz = dl.get('size', '')
        au = dl.get('audio', '')
        ql = dl.get('quality', '')
        cd = dl.get('codec', '')
        lines.append(f"\n<b>{i}.</b>")
        if fn:
            lines.append(f"📄 <code>{fn}</code>")
        specs = []
        if ql: specs.append(f"🎥 {ql}")
        if cd: specs.append(f"🔧 {cd}")
        if sz: specs.append(f"💾 {sz}")
        if au: specs.append(f"🔊 {au}")
        if specs:
            lines.append(" | ".join(specs))
        if dl.get('hc'):
            lines.append(f"📥 <a href='{dl['hc']}'>☁️ HubCloud</a>")
        if dl.get('hd'):
            lines.append(f"📥 <a href='{dl['hd']}'>💾 HubDrive</a>")
    lines.append(f"\n\n<i>— {BOT_HANDLE}</i>")
    return "\n".join(lines)


# ─── Season ZIP packs ────────────────────────
def fmt_packs(packs: list, season: str) -> str:
    my = [p for p in packs if p.get('season') == season]
    if not my:
        return f"<i>No ZIP packs for {season}</i>"
    lines = [
        f"<b>📦 ZIP PACKS — {season}</b>",
        f"📊 {len(my)} qualities",
        "─" * 30,
    ]
    for i, p in enumerate(my, 1):
        fn = p.get('filename', '')
        sz = p.get('size', '')
        au = p.get('audio', '')
        ql = p.get('quality', '')
        cd = p.get('codec', '')
        lines.append(f"\n<b>{i}.</b>")
        if fn:
            lines.append(f"📄 <code>{fn}</code>")
        specs = []
        if ql: specs.append(f"🎥 {ql}")
        if cd: specs.append(f"🔧 {cd}")
        if sz: specs.append(f"💾 {sz}")
        if au: specs.append(f"🔊 {au}")
        if specs:
            lines.append(" | ".join(specs))
        if p.get('hc'):
            lines.append(f"📥 <a href='{p['hc']}'>☁️ HubCloud</a>")
        if p.get('hd'):
            lines.append(f"📥 <a href='{p['hd']}'>💾 HubDrive</a>")
    lines.append(f"\n\n<i>— {BOT_HANDLE}</i>")
    return "\n".join(lines)


# ─── Single episode ──────────────────────────
def fmt_one_ep(ep: dict) -> str:
    fn  = ep.get('filename', '')
    num = ep.get('number', '')
    sz  = ep.get('size', '')
    lines = [f"<b>🎬 Episode {num}</b> | 💾 {sz}"]
    if fn:
        lines.append(f"📄 <code>{fn}</code>")
    if ep.get('hc'):
        lines.append(f"📥 <a href='{ep['hc']}'>☁️ HubCloud</a>")
    if ep.get('hd'):
        lines.append(f"📥 <a href='{ep['hd']}'>💾 HubDrive</a>")
    return "\n".join(lines)


# ─── How-to-download guide ───────────────────
HOW_TO = (
    f"<b>📥 How to Download</b>  |  {BOT_HANDLE}\n"
    "━━━━━━━━━━━━━━━━━━━━\n\n"
    "<b>1️⃣</b> Click on <b>☁️ HubCloud</b> or <b>💾 HubDrive</b>\n"
    "<b>2️⃣</b> Wait for page to load (5–10 sec)\n"
    "<b>3️⃣</b> Solve captcha if shown\n"
    "<b>4️⃣</b> Click <b>Download</b> button\n"
    "<b>5️⃣</b> File starts downloading!\n\n"
    "<b>💡 Tips:</b>\n"
    "• HubCloud = Faster speeds\n"
    "• HubDrive = G-Drive links\n"
    "• ZIP = Complete season\n"
    "• Single EPs = Individual files\n\n"
    "<i>⚠️ Use VPN if links don't open!</i>"
)
