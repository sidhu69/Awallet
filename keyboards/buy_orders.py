from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def cancel_order_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel Order", callback_data="cancel_order")]
        ]
    )
