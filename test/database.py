# database.py - Save/load logic
import json
import logging
from pathlib import Path

from config import DB_FILE, users, admins, welcome_media, auto_qr_enabled, auto_qr_file_id

DB_PATH = Path(DB_FILE)

def save_db():
    try:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "users": users,
                "admins": list(admins),
                "welcome_media": welcome_media,
                "auto_qr_enabled": auto_qr_enabled,
                "auto_qr_file_id": auto_qr_file_id
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"save_db failed: {e}")

def load_db():
    global users, admins, welcome_media, auto_qr_enabled, auto_qr_file_id
    if not DB_PATH.is_file():
        return
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            users = data.get("users", {})
            admins = set(data.get("admins", [OWNER_ID]))
            welcome_media = data.get("welcome_media")
            auto_qr_enabled = data.get("auto_qr_enabled", False)
            auto_qr_file_id = data.get("auto_qr_file_id")
    except Exception as e:
        logging.error(f"load_db failed: {e}")
