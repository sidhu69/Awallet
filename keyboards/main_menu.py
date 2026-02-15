from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import is_user_subscribed


def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """
    Returns dynamic main menu based on subscription status.
    """

    subscribed = is_user_subscribed(user_id)

    if not subscribed:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Subscribe ₹50", callback_data="subscribe")],
                [InlineKeyboardButton(text="👤 My Profile", callback_data="profile")],
                [InlineKeyboardButton(text="📢 Support Channel", url="https://t.me/theawalletchannel")]
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📤 Send Video", callback_data="send_video")],
            [InlineKeyboardButton(text="📊 My Balance", callback_data="my_balance")],
            [InlineKeyboardButton(text="👤 My Profile", callback_data="profile")],
            [InlineKeyboardButton(text="📢 Support Channel", url="https://t.me/theawalletchannel")]
        ]
    )


def back_button() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
        ]
    )
