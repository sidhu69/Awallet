from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
import asyncio
from aiogram.fsm.context import FSMContext

from states.user import UserForm
from utils.check_join import is_user_joined
from keyboards.force_join import join_channel_keyboard
from utils.send_instructions import send_voice_instructions

router = Router()


# /start → ONLY CHECK JOIN STATUS
@router.message(CommandStart())
async def start_handler(message: Message):
    bot = message.bot
    user_id = message.from_user.id

    joined = await is_user_joined(bot, user_id)

    if not joined:
        await message.answer(
            "🚫 To use this bot, please join our channel first 💟.",
            reply_markup=join_channel_keyboard()
        )
        return

    await message.answer(
        "✅ You already have access.\n"
        "Click <b>Confirm</b> below to continue 👇",
        reply_markup=join_channel_keyboard()
    )


# CONFIRM BUTTON → MAIN FLOW
@router.callback_query(lambda c: c.data == "confirm_join")
async def confirm_join_handler(call: CallbackQuery, state: FSMContext):
    bot = call.bot
    user_id = call.from_user.id

    joined = await is_user_joined(bot, user_id)

    if not joined:
        await call.answer(
            "❌ You haven't joined the channel yet 😒.",
            show_alert=True
        )
        return

    await call.answer()  # stop button loading

    await call.message.edit_text("✅ Access granted! Welcome.")

    # Send voice
    await send_voice_instructions(bot, user_id)

    # Wait 30 sec
    await asyncio.sleep(30)

    # Ask name once
    await call.message.answer(
        "📝 Please enter your name\n"
        "👉 कृपया अपना नाम बताएं"
    )

    await state.set_state(UserForm.name)


# RECEIVE NAME
@router.message(UserForm.name)
async def process_name(message: Message, state: FSMContext):
    name = message.text.strip()

    if len(name) < 2:
        await message.answer("❌ Please enter a valid name")
        return

    await state.update_data(name=name)

    await message.answer(
        f"✅ Thank you, <b>{name}</b>!\n"
        "You are successfully registered 🎉"
    )

    await state.clear()
