import asyncio
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states.user import UserForm
from utils.check_join import is_user_joined
from keyboards.force_join import join_channel_keyboard
from keyboards.main_menu import main_menu_keyboard
from utils.send_instructions import send_voice_instructions
from database.db import get_user, create_user, get_wallet, save_referral

router = Router()


# =========================
# /start → CHECK JOIN + REFERRAL
# =========================
@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Parse referral from start command: /start <ref_id>
    parts = message.text.split()
    ref_id = None
    if len(parts) > 1 and parts[1].isdigit():
        ref_id = int(parts[1])
        # Don't refer yourself
        if ref_id == user_id:
            ref_id = None

    user = get_user(user_id)
    
    # If new user and has ref_id, we need to make sure it's stored
    # We'll handle storage during create_user, but we can cache it in state
    if not user and ref_id:
        await state.update_data(referrer_id=ref_id)

    joined = await is_user_joined(message.bot, user_id)
    if not joined:
        await message.answer(
            "🚫 To use this bot, please join our channel first 💟.",
            reply_markup=join_channel_keyboard()
        )
        return

    if user:
        wallet = get_wallet(user_id)
        await message.answer(
            f"👋 Welcome back!\n"
            f"Your wallet balance is: <b>{wallet}</b> coins\n\n"
            "👇 Select an option below:",
            reply_markup=main_menu_keyboard()
        )
        return

    # New user who has joined
    await message.answer(
        "✅ You already have access.\n"
        "Click <b>Confirm</b> below to continue 👇",
        reply_markup=join_channel_keyboard()
    )


# =========================
# CONFIRM BUTTON → FLOW
# =========================
@router.callback_query(lambda c: c.data == "confirm_join")
async def confirm_join_handler(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    joined = await is_user_joined(call.bot, user_id)
    if not joined:
    await call.answer(
            "❌ You haven't joined the channel yet 😒.",
            show_alert=True
        )
        return

    await call.answer()
    
    # Check if user already registered during the sleep/wait
    if get_user(user_id):
        await call.message.edit_text("✅ Welcome back!")
        wallet = get_wallet(user_id)
        await call.message.answer(
            f"Your wallet balance is: <b>{wallet}</b> coins",
            reply_markup=main_menu_keyboard()
        )
        return

    await call.message.edit_text("✅ Access granted! Welcome.")

    # 🎧 Send voice instructions
    await send_voice_instructions(call.bot, user_id)

    # ⏱ Wait 10 seconds (reduced from 30 for better UX)
    await asyncio.sleep(10)

    await call.message.answer(
        "📝 Please enter your name\n"
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
