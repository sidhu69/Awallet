from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def approve_decline_kb(user_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_data=f"approve_{user_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Decline",
                    callback_data=f"decline_{user_id}"
                )
            ]
        ]
    )
