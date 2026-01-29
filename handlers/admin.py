from aiogram import Router
from aiogram.types import Message
from config import OWNER_ID
from database.db import set_upi

router = Router()

@router.message(lambda m: m.text.startswith("/upi"))
async def change_upi(message: Message):
    if message.from_user.id != OWNER_ID:
        return

    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /upi yourupi@bank")
        return

    set_upi(parts[1])
    await message.answer(f"✅ UPI updated to: {parts[1]}")
