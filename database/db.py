import sqlite3
from datetime import datetime

DB_NAME = "awallet.db"


# =========================
# INIT DATABASE
# =========================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Users table with wallet
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT,
            upi TEXT,
            wallet INTEGER DEFAULT 0,
            created_at TEXT,
            referrer_id INTEGER
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
def create_user(telegram_id: int, name: str, upi: str, referrer_id: int = None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Preserve existing wallet if user already exists
    cursor.execute("""
        INSERT OR REPLACE INTO users
        (telegram_id, name, upi, wallet, created_at, referrer_id)
        VALUES (?, ?, ?, COALESCE((SELECT wallet FROM users WHERE telegram_id = ?), 0), ?, ?)
    """, (telegram_id, name, upi, telegram_id, datetime.now().isoformat(), referrer_id))

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

    cursor.execute("SELECT wallet FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0


def update_wallet(telegram_id: int, amount: float):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET wallet = wallet + ? WHERE telegram_id = ?",
        (amount, telegram_id)
    )

    conn.commit()
    conn.close()


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


# =========================
# REFERRAL FUNCTIONS
# =========================
def save_referral(user_id: int, referrer_id: int):
    """
    Save referrer for a new user.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET referrer_id = ? WHERE telegram_id = ?",
        (referrer_id, user_id)
    )

    conn.commit()
    conn.close()


def get_referrer(user_id: int):
    """
    Returns the referrer_id of a user.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT referrer_id FROM users WHERE telegram_id = ?",
        (user_id,)
    )

    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def add_referral_bonus(user_id: int, deposit_amount: float, percentage: float = 0.4):
    """
    Add referral bonus to the referrer wallet based on user's deposit.
    Default: 0.4% of deposit.
    """
    referrer_id = get_referrer(user_id)
    if not referrer_id:
        return  # No referrer

    bonus = deposit_amount * (percentage / 100)
    update_wallet(referrer_id, bonus)
    return bonus
