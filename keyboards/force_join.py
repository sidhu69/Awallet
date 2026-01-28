from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNEL_ID


def join_channel_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Join Channel",
                url=f"https://t.me/{CHANNEL_ID.replace('@', '')}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔄 Confirm",
                callback_data="confirm_join"
            )
        ]
    ])
    return keyboard
