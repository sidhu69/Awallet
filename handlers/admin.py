from aiogram import Router
from aiogram.types import Message, CallbackQuery
from config import OWNER_ID
from database.db import set_upi

router = Router()


# =========================
# OWNER: CHANGE UPI
# =========================
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


# =========================
# OWNER: APPROVE PAYMENT
# =========================
@router.callback_query(lambda c: c.data.startswith("approve_"))
async def approve_payment(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])

    await call.answer("Approved")
    await call.message.edit_caption("✅ Payment Approved")

    await call.bot.send_message(
        user_id,
        "✅ Your payment has been approved 🎉"
    )


# =========================
# OWNER: DECLINE PAYMENT
# =========================
@router.callback_query(lambda c: c.data.startswith("decline_"))
async def decline_payment(call: CallbackQuery):
    user_id = int(call.data.split("_")[1])

    await call.answer("Declined")
    await call.message.edit_caption("❌ Payment Declined")

    await call.bot.send_message(
        user_id,
        "❌ Your payment was declined. Please contact support."
    )
