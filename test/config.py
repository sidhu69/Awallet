# config.py - All constants & globals
OWNER_ID = 8032922682
BOT_TOKEN = "8392213332:AAE8vq4X1GbmuOmmX6Hdix7CUwTvAtb3iQ0"
SUPPORT_USERNAME = "@theawalletsupportbot"
CHANNEL_USERNAME = "@awalletchannel"

DB_FILE = "awallet_users.json"

# Globals (loaded/saved in database.py)
welcome_media = None          # {"file_id": str, "type": "voice"|"audio"}
auto_qr_enabled = False
auto_qr_file_id = None

users = {}
admins = {OWNER_ID}
