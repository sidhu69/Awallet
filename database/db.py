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
            wallet INTEGER DEFAULT 0,
            referred_by INTEGER,
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

    # 🔧 migrate old databases
    add_wallet_column()
    add_referred_by_column()


# =========================
# MIGRATIONS
# =========================
def add_wallet_column():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN wallet INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


def add_referred_by_column():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()


# =========================
# USER FUNCTIONS
# =========================
def create_user(
    telegram_id: int,
    name: str,
    upi: str,
    referred_by: int = None
):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # keep wallet + referral if already exists
    cursor.execute("""
        INSERT OR IGNORE INTO users
        (telegram_id, name, upi, wallet, referred_by, created_at)
        VALUES (?, ?, ?, 0, ?, ?)
    """, (telegram_id, name, upi, referred_by, datetime.now().isoformat()))

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
# WALLET FUNCTIONS
# =========================
def get_wallet(telegram_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT wallet FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def update_wallet(telegram_id: int, amount: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET wallet = wallet + ? WHERE telegram_id = ?",
        (amount, telegram_id)
    )

    conn.commit()
    conn.close()


# =========================
# REFERRAL FUNCTIONS
# =========================
def get_referrer(telegram_id: int):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT referred_by FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else None


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
