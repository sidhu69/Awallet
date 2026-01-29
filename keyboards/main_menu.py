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
            [InlineKeyboardButton(text="📢 Support Channel", callback_data="support_channel")],
            [InlineKeyboardButton(text="⚙️ Account Settings", callback_data="account_settings")]
        ]
    )
