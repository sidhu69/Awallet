import sqlite3
from datetime import datetime

DB_NAME = "awallet.db"


# =========================
# INIT DATABASE
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT,
            upi TEXT,
            created_at TEXT
        )
    """)

    # Settings table (for UPI etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    # Default UPI (if not exists)
    cursor.execute("""
        INSERT OR IGNORE INTO settings (key, value)
        VALUES ('upi', 'default@upi')
    """)

    conn.commit()
    conn.close()


# =========================
# USER FUNCTIONS
# =========================
def create_user(telegram_id: int, name: str, upi: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO users
        (telegram_id, name, upi, created_at)
        VALUES (?, ?, ?, ?)
    """, (telegram_id, name, upi, datetime.now().isoformat()))

    conn.commit()
    conn.close()


def get_user(telegram_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    user = cursor.fetchone()
    conn.close()
    return user


# =========================
# UPI SETTINGS
# =========================
def set_upi(new_upi: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO settings (key, value)
        VALUES ('upi', ?)
    """, (new_upi,))

    conn.commit()
    conn.close()


def get_upi():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT value FROM settings WHERE key = 'upi'"
    )

    row = cursor.fetchone()
    conn.close()

    return row[0] if row else None
