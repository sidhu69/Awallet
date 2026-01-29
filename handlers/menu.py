from aiogram import Router, types
from aiogram.filters import Command  # <-- v3 style
from keyboards.main_menu import main_menu_keyboard
from database.db import get_wallet

router = Router()

# =========================
# /menu → SHOW MAIN MENU
# =========================
@router.message(Command("menu"))  # <-- correct v3 syntax
async def show_main_menu(message: types.Message):
    wallet = get_wallet(message.from_user.id)
    await message.answer(
        f"👋 <b>Hey there! Welcome to Awallet 💟</b>\n\n"
        "Awallet is always here to help you grow your income.\n"
        f"Your wallet is: <b>{wallet}</b> coins\n"
        "Buy your orders to earn more 💰\n\n"
        "👇 <b>Select an option below:</b>",
        reply_markup=main_menu_keyboard()
    )
