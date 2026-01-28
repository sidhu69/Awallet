from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from utils.check_join import is_user_joined
from keyboards.force_join import join_channel_keyboard

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

    await message.answer("✅ Welcome! You have access to the bot.")


@router.callback_query(lambda c: c.data == "confirm_join")
async def confirm_join_handler(call: CallbackQuery):
    bot = call.bot
    user_id = call.from_user.id

    joined = await is_user_joined(bot, user_id)

    if joined:
        await call.message.edit_text("✅ Access granted! Welcome.")
    else:
        await call.answer(
            "❌ You haven't joined the channel yet😒.",
            show_alert=True
        )
