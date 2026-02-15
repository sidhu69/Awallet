from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import main_menu_keyboard, back_button
from database.db import get_user

router = Router()


# =========================
# /menu → SHOW MAIN MENU
# =========================
@router.message(Command("menu"))
async def show_main_menu(message: types.Message):
    user_id = message.from_user.id

    await message.answer(
        "👋 Welcome to Awallet\n\n"
        "👇 Select an option below:",
        reply_markup=main_menu_keyboard(user_id)
    )


# =========================
# BACK TO MENU
# =========================
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()

    await call.message.edit_text(
        "👋 Welcome back!\n\n"
        "👇 Select an option below:",
        reply_markup=main_menu_keyboard(call.from_user.id)
    )
    await call.answer()


# =========================
# PROFILE HANDLER
# =========================
@router.callback_query(F.data == "profile")
async def profile_handler(call: types.CallbackQuery):
    user = get_user(call.from_user.id)

    if not user:
        await call.answer("User not found.", show_alert=True)
        return

    user_id, name, upi, balance, is_subscribed = user

    status = "Active" if is_subscribed else "Not Subscribed"

    await call.message.edit_text(
        f"👤 <b>Your Profile</b>\n\n"
        f"🆔 ID: <code>{user_id}</code>\n"
        f"👤 Name: <b>{name}</b>\n"
        f"💳 UPI: <b>{upi}</b>\n"
        f"💰 Balance: ₹<b>{balance}</b>\n"
        f"📌 Subscription: <b>{status}</b>",
        reply_markup=back_button()
    )

    await call.answer()


# =========================
# MY BALANCE
# =========================
@router.callback_query(F.data == "my_balance")
async def balance_handler(call: types.CallbackQuery):
    user = get_user(call.from_user.id)

    if not user:
        await call.answer("User not found.", show_alert=True)
        return

    balance = user[3]

    await call.message.edit_text(
        f"💰 <b>Your Current Balance</b>\n\n"
        f"₹ <b>{balance}</b>",
        reply_markup=back_button()
    )

    await call.answer()
