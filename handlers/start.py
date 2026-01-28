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


@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    bot = message.bot
    user_id = message.from_user.id

    joined = await is_user_joined(bot, user_id)

    if not joined:
        await message.answer(
            "🚫 To use this bot, please join our channel first 💟.",
            reply_markup=join_channel_keyboard()
        )
        return

    # Access granted
    await message.answer("✅ Access granted! Welcome.")

    # Send voice instructions
    await send_voice_instructions(bot, user_id)

    # ⏱ wait 30 seconds
    await asyncio.sleep(30)

    # Ask for name (EN + HI)
    await message.answer(
        "📝 Please enter your name\n"
        "👉 कृपया अपना नाम बताएं"
    )

    # Set FSM state
    await state.set_state(UserForm.name)


@router.callback_query(lambda c: c.data == "confirm_join")
async def confirm_join_handler(call: CallbackQuery, state: FSMContext):
    bot = call.bot
    user_id = call.from_user.id

    joined = await is_user_joined(bot, user_id)

    if joined:
        await call.answer()  # stop button loading

        await call.message.edit_text("✅ Access granted! Welcome.")

        await send_voice_instructions(bot, user_id)

        # ⏱ wait 30 seconds
        await asyncio.sleep(30)

        await call.message.answer(
            "📝 Please enter your name\n"
            "👉 कृपया अपना नाम बताएं"
        )

        await state.set_state(UserForm.name)

    else:
        await call.answer(
            "❌ You haven't joined the channel yet 😒.",
            show_alert=True
        )


# ✅ HANDLE NAME INPUT
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
