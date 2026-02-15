import sqlite3

class Database:
    def __init__(self, db_name=':memory:'):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        # Create users table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, is_subscribed BOOLEAN)''')
        # Create videos table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS videos (id INTEGER PRIMARY KEY, title TEXT, url TEXT, status TEXT)''')
        # Create subscription_payments table
        self.conn.execute('''CREATE TABLE IF NOT EXISTS subscription_payments (id INTEGER PRIMARY KEY, user_id INTEGER, amount REAL, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))''')
        self.conn.commit()

    def is_user_subscribed(self, user_id):
        cursor = self.conn.execute('''SELECT is_subscribed FROM users WHERE id = ?''', (user_id,))
        return cursor.fetchone()[0] if cursor.fetchone() else None

    def subscribe_user(self, user_id):
        self.conn.execute('''UPDATE users SET is_subscribed = 1 WHERE id = ?''', (user_id,))
        self.conn.commit()

    def save_video(self, title, url):
        self.conn.execute('''INSERT INTO videos (title, url, status) VALUES (?, ?, ?)''', (title, url, 'pending'))
        self.conn.commit()

    def get_all_videos(self):
        cursor = self.conn.execute('''SELECT * FROM videos''')
        return cursor.fetchall()

    def approve_video(self, video_id):
        self.conn.execute('''UPDATE videos SET status = 'approved' WHERE id = ?''', (video_id,))
        self.conn.commit()

    def get_pending_videos(self):
        cursor = self.conn.execute('''SELECT * FROM videos WHERE status = 'pending' ''')
        return cursor.fetchall()

    def update_multiple_balances(self, user_ids, amount):
        self.conn.executemany('''UPDATE users SET balance = balance + ? WHERE id = ?''', [(amount, user_id) for user_id in user_ids])
        self.conn.commit()  

# Example of how to use this class
db = Database()
db.save_video('Example Video','http://example.com/video')  # Save an example video
