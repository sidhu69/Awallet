from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from utils.check_join import is_user_joined
from keyboards.force_join import join_channel_keyboard
from utils.send_instructions import send_voice_instructions

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message):
    bot = message.bot
    user_id = message.from_user.id

    joined = await is_user_joined(bot, user_id)

    if not joined:
        await message.answer(
            "🚫 To use this bot, please join our channel first💟.",
            reply_markup=join_channel_keyboard()
        )
        return

    # Access granted
    await message.answer("✅ Access granted! Welcome.")
    
    # Forward the voice from your channel
    await send_voice_instructions(bot, user_id)


@router.callback_query(lambda c: c.data == "confirm_join")
async def confirm_join_handler(call: CallbackQuery):
    bot = call.bot
    user_id = call.from_user.id

    joined = await is_user_joined(bot, user_id)

    if joined:
        # Stop button glowing
        await call.answer()

        # Update message
        await call.message.edit_text("✅ Access granted! Welcome.")

        # Forward the voice from your channel
        await send_voice_instructions(bot, user_id)

    else:
        # Show alert that user hasn't joined
        await call.answer(
            "❌ You haven't joined the channel yet😒.",
            show_alert=True
        )
