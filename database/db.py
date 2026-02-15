import sqlite3

class Database:
    def __init__(self, db_name='awallet.db'):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            upi TEXT,
            balance INTEGER DEFAULT 0,
            is_subscribed BOOLEAN DEFAULT 0
        )
        """)

        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS videos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            file_id TEXT,
            status TEXT DEFAULT 'pending',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)

        self.conn.commit()

    # ---------- USER METHODS ----------

    def create_user(self, user_id, name, upi):
        self.conn.execute("""
        INSERT OR IGNORE INTO users (id, name, upi)
        VALUES (?, ?, ?)
        """, (user_id, name, upi))
        self.conn.commit()

    def subscribe_user(self, user_id):
        self.conn.execute("""
        UPDATE users SET is_subscribed = 1 WHERE id = ?
        """, (user_id,))
        self.conn.commit()

    def add_balance(self, user_id, amount):
        self.conn.execute("""
        UPDATE users SET balance = balance + ? WHERE id = ?
        """, (amount, user_id))
        self.conn.commit()

    def get_user(self, user_id):
        cursor = self.conn.execute("""
        SELECT * FROM users WHERE id = ?
        """, (user_id,))
        return cursor.fetchone()

    # ---------- VIDEO METHODS ----------

    def save_video(self, user_id, file_id):
        self.conn.execute("""
        INSERT INTO videos (user_id, file_id)
        VALUES (?, ?)
        """, (user_id, file_id))
        self.conn.commit()

    def get_pending_videos(self):
        cursor = self.conn.execute("""
        SELECT * FROM videos WHERE status = 'pending'
        """)
        return cursor.fetchall()

    def approve_video(self, video_id):
        self.conn.execute("""
        UPDATE videos SET status = 'approved' WHERE id = ?
        """, (video_id,))
        self.conn.commit()
