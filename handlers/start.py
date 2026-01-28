from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from utils.check_join import is_user_joined
from keyboards.force_join import join_channel_keyboard
from utils.send_instructions import send_voice_instructions

router = Router()


@router.callback_query(lambda c: c.data == "confirm_join")
async def confirm_join_handler(call: CallbackQuery):
    bot = call.bot
    user_id = call.from_user.id

    # Re-check if user has joined the channel
    joined = await is_user_joined(bot, user_id)

    if joined:
        # Access granted → update message
        await call.message.edit_text("✅ Access granted! Welcome.")

        # Forward the instruction voice note
        await send_voice_instructions(bot, user_id)

        # Answer the callback so the glowing stops
        await call.answer()  # <- THIS LINE FIXES THE BUTTON HANG

    else:
        # User still hasn't joined → alert
        await call.answer(
            "❌ You haven't joined the channel yet😒.",
            show_alert=True
        
        )
