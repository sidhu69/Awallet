import asyncio
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states.user import UserForm
from utils.check_join import is_user_joined
from keyboards.force_join import join_channel_keyboard
from keyboards.main_menu import main_menu_keyboard
from database.db import get_user, create_user

router = Router()


# =========================
# /start → CHECK JOIN
# =========================
@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    joined = await is_user_joined(message.bot, user_id)
    if not joined:
        await message.answer(
            "🚫 To use this bot, please join our channel first.",
            reply_markup=join_channel_keyboard()
        )
        return

    user = get_user(user_id)

    if user:
        await message.answer(
            "👋 Welcome back!\n\n"
            "👇 Select an option below:",
            reply_markup=main_menu_keyboard()
        )
        return

    await message.answer(
        "✅ Access granted!\n\n"
        "📝 Please enter your name:"
    )
    await state.set_state(UserForm.name)


# =========================
# RECEIVE NAME
# =========================
@router.message(UserForm.name)
async def process_name(message: types.Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ Please enter a valid name.")
        return

    await state.update_data(name=name)

    await message.answer(
        "💳 Please enter your UPI ID:"
    )

    await state.set_state(UserForm.upi)


# =========================
# RECEIVE UPI → COMPLETE REGISTRATION
# =========================
@router.message(UserForm.upi)
async def process_upi(message: types.Message, state: FSMContext):
    upi = message.text.strip()

    if "@" not in upi or len(upi) < 5:
        await message.answer("❌ Invalid UPI ID. Please try again.")
        return

    data = await state.get_data()
    name = data.get("name")
    user_id = message.from_user.id

    create_user(user_id, name, upi)

    await message.answer(
        f"✅ Registration Complete!\n\n"
        f"👤 Name: <b>{name}</b>\n"
        f"💳 UPI: <b>{upi}</b>"
    )

    await state.clear()

    await message.answer(
        "👇 Choose an option below:",
        reply_markup=main_menu_keyboard()
    )
