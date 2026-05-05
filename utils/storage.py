# ============================================
# 💾 UTILS/STORAGE.PY — JSON File Operations
# Users • Banned • Settings persistence
# ============================================
import json, os
from datetime import datetime, UTC
from config import USERS_FILE, BANNED_FILE, SETTINGS_FILE


# ─── Generic helpers ─────────────────────────
def load_json_file(file: str) -> dict:
    try:
        if os.path.exists(file):
            with open(file, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_json_file(file: str, data: dict) -> None:
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)


# ─── Users ───────────────────────────────────
def load_users() -> dict:
    return load_json_file(USERS_FILE)

def save_users(data: dict) -> None:
    save_json_file(USERS_FILE, data)

def save_user(uid: int, data: dict) -> None:
    users = load_users()
    users[str(uid)] = data
    save_users(users)

def get_all_users() -> dict:
    return load_users()

def count_users() -> int:
    return len(load_users())


# ─── Banned ──────────────────────────────────
def load_banned() -> dict:
    return load_json_file(BANNED_FILE)

def save_banned(data: dict) -> None:
    save_json_file(BANNED_FILE, data)

def is_banned(uid: int) -> bool:
    return str(uid) in load_banned()

def ban_user(uid: int) -> None:
    banned = load_banned()
    banned[str(uid)] = {"banned_at": datetime.now(UTC).isoformat()}
    save_banned(banned)

def unban_user(uid: int) -> None:
    banned = load_banned()
    banned.pop(str(uid), None)
    save_banned(banned)


# ─── Settings ────────────────────────────────
def load_settings() -> dict:
    return load_json_file(SETTINGS_FILE)

def save_settings(data: dict) -> None:
    save_json_file(SETTINGS_FILE, data)

def get_setting(key: str, default=None):
    return load_settings().get(key, default)

def set_setting(key: str, value) -> None:
    settings = load_settings()
    settings[key] = value
    save_settings(settings)
