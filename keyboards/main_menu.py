from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Returns the main menu inline keyboard for the bot.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛒 Buy Orders", callback_data="buy_orders")],
            [InlineKeyboardButton(text="👥 Refer & Earn", callback_data="refer_earn")],
            [InlineKeyboardButton(text="❓ Help", callback_data="help")],
            [InlineKeyboardButton(text="📢 Support Channel", url="https://t.me/theawalletchannel")],
            [InlineKeyboardButton(text="⚙️ Account Settings", callback_data="account_settings")]
        ]
    )

def back_button() -> InlineKeyboardMarkup:
    """
    Returns a keyboard with a single 'Back to Menu' button.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Menu", callback_data="back_to_menu")]
        ]
    )
