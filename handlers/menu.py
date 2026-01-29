# Line 1
from aiogram import Router, types

# Line 2
from aiogram.filters import Command

# Line 3
from database.db import get_wallet

# Line 4
from keyboards.main_menu import main_menu_keyboard

# Line 5
router = Router()


# =========================
# /menu → SHOW MAIN MENU
# =========================
# Line 11
@router.message(Command("menu"))
async def show_main_menu(message: types.Message):
    # Line 13
    wallet = get_wallet(message.from_user.id)
    
    # Line 15
    await message.answer(
        f"👋 <b>Hey there! Welcome to Awallet 💟</b>\n\n"
        "Awallet is always here to help you grow your income.\n"
        f"Your wallet is: <b>{wallet}</b> coins\n"
        "Buy your orders to earn more 💰\n\n"
        "👇 <b>Select an option below:</b>",
        reply_markup=main_menu_keyboard()
    )
