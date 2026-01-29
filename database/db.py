import sqlite3
from datetime import datetime

DB_NAME = "database/users.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            upi TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def user_exists(telegram_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    result = cursor.fetchone()
    conn.close()

    return result is not None


def add_user(telegram_id: int, name: str, upi: str):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO users (telegram_id, name, upi, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (telegram_id, name, upi, datetime.utcnow().isoformat())
    )

    conn.commit()
    conn.close()


def get_user(telegram_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT telegram_id, name, upi, created_at FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )

    user = cursor.fetchone()
    conn.close()

    return user
