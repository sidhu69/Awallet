import asyncio
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states.user import UserForm
from database.db import get_user, create_user, get_wallet, subscribe_user, is_user_subscribed, save_video

from keyboards.main_menu import join_channel_keyboard

router = Router()


# =========================
# /start → NEW USER FLOW
# =========================
@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    user = get_user(user_id)

    # If user exists → show /menu hint
    if user:
        await message.answer(
            f"👋 Welcome back!\n"
            f"Your wallet balance: <b>{get_wallet(user_id)}</b> coins\n\n"
            "Type /menu to explore options."
        )
        return

    # New user → ask for name
    await message.answer(
        "✅ Welcome! Please enter your name:\n"
        "👉 कृपया अपना नाम बताएं"
    )
    await state.set_state(UserForm.name)


# =========================
# RECEIVE NAME
# =========================
@router.message(UserForm.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("❌ Please enter a valid name")
        return

    await state.update_data(name=name)
    await message.answer(f"✅ Thank you, <b>{name}</b>!\n\nNow enter your UPI ID:")
    await state.set_state(UserForm.upi)


# =========================
# RECEIVE UPI
# =========================
@router.message(UserForm.upi)
async def process_upi(message: types.Message, state: FSMContext):
    upi = message.text.strip()
    if "@" not in upi or len(upi) < 5:
        await message.answer("❌ Invalid UPI ID\n👉 कृपया सही UPI ID दर्ज करें")
        return

    data = await state.get_data()
    name = data.get("name")
    user_id = message.from_user.id

    # Create user in DB
    create_user(user_id, name, upi)

    await message.answer(
        f"✅ Registration Complete 🎉\n\n"
        f"👤 Name: <b>{name}</b>\n"
        f"💳 UPI: <b>{upi}</b>\n\n"
        "👉 Type /menu to explore options"
    )
    await state.clear()
