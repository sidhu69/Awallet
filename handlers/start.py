import asyncio
from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from states.user import UserForm
from utils.check_join import is_user_joined
from keyboards.force_join import join_channel_keyboard
from keyboards.main_menu import main_menu_keyboard
from utils.send_instructions import send_voice_instructions
from database.db import get_user, create_user, get_wallet, save_referral  # save_referral included

router = Router()


# =========================
# /start → CHECK JOIN + REFERRAL
# =========================
@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    joined = await is_user_joined(message.bot, user_id)
    if not joined:
        await message.answer(
            "🚫 To use this bot, please join our channel first 💟.",
            reply_markup=join_channel_keyboard()
        )
        return

    # Parse referral from start command: /start <ref_id>
    parts = message.text.split()
    ref_id = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else None

    user = get_user(user_id)  # Check if user already exists
    if user:
        wallet = get_wallet(user_id)
        await message.answer(
            f"👋 Welcome back!\n"
            f"Your wallet balance is: <b>{wallet}</b> coins\n\n"
            "👇 Select an option below:",
            reply_markup=main_menu_keyboard()
        )
        return

    # New user → save referral if exists
    if ref_id:
        save_referral(user_id, ref_id)

    # Ask confirm to start registration
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

    await call.answer()  # stop loading animation
    await call.message.edit_text("✅ Access granted! Welcome.")

    # 🎧 Send voice instructions
    await send_voice_instructions(call.bot, user_id)

    # ⏱ Wait 30 seconds
    await asyncio.sleep(30)

    # 📝 Ask for name
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

    await state.update_data(name=name)
    await message.answer(f"✅ Thank you, <b>{name}</b>!")

    # ⏱ Wait 2 seconds
    await asyncio.sleep(2)
    await message.answer(
        "💳 Please enter your UPI ID to take withdrawals\n"
        "👉 निकासी के लिए अपना UPI ID दर्ज करें"
    )
    await state.set_state(UserForm.upi)


# =========================
# RECEIVE UPI → MAIN MENU
# =========================
@router.message(UserForm.upi)
async def process_upi(message: types.Message, state: FSMContext):
    upi = message.text.strip()
    if "@" not in upi or len(upi) < 5:
        await message.answer(
            "❌ Invalid UPI ID\n"
            "👉 कृपया सही UPI ID दर्ज करें"
        )
        return

    data = await state.get_data()
    name = data.get("name")
    user_id = message.from_user.id

    # Add new user to DB (referrer already saved in save_referral if applicable)
    create_user(user_id, name, upi)

    # ✅ Registration complete
    await message.answer(
        f"✅ Registration Complete 🎉\n\n"
        f"👤 Name: <b>{name}</b>\n"
        f"💳 UPI: <b>{upi}</b>"
    )

    await state.clear()  # clear FSM

    # 🏠 Show main menu with wallet
    wallet = get_wallet(user_id)
    await message.answer(
        f"👋 <b>Hey there! Welcome to Awallet</b> 💟\n\n"
        "Awallet is always here to help you grow your income.\n"
        f"Your wallet is: <b>{wallet}</b> coins\n"
        "Buy your orders to earn more 💰\n\n"
        "👇 <b>Select an option below:</b>",
        reply_markup=main_menu_keyboard()
    )
