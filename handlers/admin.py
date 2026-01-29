from aiogram import Router
from aiogram.types import Message, CallbackQuery
from config import OWNER_ID
from database.db import set_upi, update_wallet, get_referrer, update_wallet  # Added get_referrer for referral bonus

router = Router()

# =========================
# OWNER: CHANGE UPI
# Command: /upi yourupi@bank
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

    try:
        _, user_id, amount = call.data.split("_")
        user_id = int(user_id)
        amount = int(amount)
    except ValueError:
        await call.answer("Invalid data", show_alert=True)
        return

    # ✅ Update user's wallet balance
    update_wallet(user_id, amount)

    # ✅ Check for referrer
    referrer_id = get_referrer(user_id)
    if referrer_id:
        bonus = round(amount * 0.004)  # 0.4% referral bonus
        if bonus > 0:
            update_wallet(referrer_id, bonus)
            # Notify referrer
            await call.bot.send_message(
                referrer_id,
                f"💸 You received a referral bonus of <b>{bonus}</b> coins "
                f"from user <code>{user_id}</code> deposit!"
            )

    await call.answer("Payment approved")

    # ✅ Edit admin message safely
    if call.message.caption:
        await call.message.edit_caption(
            f"✅ Payment Approved\n💰 Amount: {amount}"
        )
    else:
        await call.message.edit_text(
            f"✅ Payment Approved\n💰 Amount: {amount}"
        )

    # ✅ Notify user
    await call.bot.send_message(
        user_id,
        f"✅ Your payment has been approved 🎉\n💰 {amount} coins added to your wallet"
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

    try:
        _, user_id, amount = call.data.split("_")
        user_id = int(user_id)
        amount = int(amount)
    except ValueError:
        await call.answer("Invalid data", show_alert=True)
        return

    await call.answer("Payment declined")

    # ✅ Edit admin message safely
    if call.message.caption:
        await call.message.edit_caption(
            f"❌ Payment Declined\n💰 Amount: {amount}"
        )
    else:
        await call.message.edit_text(
            f"❌ Payment Declined\n💰 Amount: {amount}"
        )

    # ✅ Notify user
    await call.bot.send_message(
        user_id,
        "❌ Your payment was declined. Please contact support."
    )
