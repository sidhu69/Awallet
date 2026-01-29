from aiogram import Router
from aiogram.types import Message, CallbackQuery
from config import OWNER_ID
from database.db import set_upi, update_wallet

router = Router()


# =========================
# OWNER: CHANGE UPI
# =========================
@router.message(lambda m: m.text and m.text.startswith("/upi"))
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
# callback_data: approve_<user_id>_<amount>
# =========================
@router.callback_query(lambda c: c.data.startswith("approve_"))
async def approve_payment(call: CallbackQuery):
    if call.from_user.id != OWNER_ID:
        await call.answer("Not authorized", show_alert=True)
        return

    _, user_id, amount = call.data.split("_")
    user_id = int(user_id)
    amount = int(amount)

    # ✅ update wallet
    update_wallet(user_id, amount)

    await call.answer("Payment approved")
    await call.message.edit_caption(
        f"✅ Payment Approved\n💰 Amount: {amount}"
    )

    await call.bot.send_message(
        user_id,
        f"✅ Your payment has been approved 🎉\n"
        f"💰 {amount} coins added to your wallet"
    )


# =========================
# OWNER: DECLINE PAYMENT
# callback_data: decline_<user_id>_<amount>
# =========================
@router.callback_query(lambda c: c.data.startswith("decline_"))
async def decline_payment(call: CallbackQuery):
    if call.from_user.id != OWNER_ID:
        await call.answer("Not authorized", show_alert=True)
        return

    _, user_id, amount = call.data.split("_")
    user_id = int(user_id)

    await call.answer("Payment declined")
    await call.message.edit_caption("❌ Payment Declined")

    await call.bot.send_message(
        user_id,
        "❌ Your payment was declined. Please contact support."
    )
