import asyncio
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states.user import UserForm
from keyboards.main_menu import main_menu_keyboard, back_button
from utils.send_instructions import send_voice_instructions
from database.db import get_user, create_user, get_wallet

router = Router()


# =========================
# /start → CHECK USER + REFERRAL
# =========================
@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Parse referral from start command (optional)
    parts = message.text.split()
    ref_id = None
    if len(parts) > 1 and parts[1].isdigit():
        ref_id = int(parts[1])
        if ref_id == user_id:
            ref_id = None

    user = get_user(user_id)

    if user:
        wallet = get_wallet(user_id)
        await message.answer(
            f"👋 Welcome back!\n"
            f"Your wallet balance is: <b>{wallet}</b> coins\n\n"
            "👇 Select an option below:",
            reply_markup=main_menu_keyboard()
        )
        return

    # New user flow
    await message.answer(
        "✅ Welcome! Let's get you registered.\n"
        "📝 Please enter your name:\n"
        "👉 कृपया अपना नाम बताएं"
    )
    await state.set_state(UserForm.name)
    if ref_id:
        await state.update_data(referrer_id=ref_id)


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
    await message.answer(f"✅ Thanks, <b>{name}</b>!\n\nNow enter your UPI ID to receive withdrawals:")
    await state.set_state(UserForm.upi)


# =========================
# RECEIVE UPI → COMPLETE REGISTRATION
# =========================
@router.message(UserForm.upi)
async def process_upi(message: types.Message, state: FSMContext):
    upi = message.text.strip()
    if "@" not in upi or len(upi) < 5:
        await message.answer("❌ Invalid UPI ID\n👉 कृपया सही UPI ID दर्ज करें")
        return

    data = await state.get_data()
    name = data.get("name")
    referrer_id = data.get("referrer_id")
    user_id = message.from_user.id

    # Add new user
    create_user(user_id, name, upi)

    await message.answer(
        f"✅ Registration Complete 🎉\n\n"
        f"👤 Name: <b>{name}</b>\n"
        f"💳 UPI: <b>{upi}</b>\n\n"
        "Type /menu to explore the bot and start earning!"
    )

    await state.clear()
