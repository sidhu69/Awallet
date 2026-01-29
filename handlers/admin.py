from aiogram import Router
from aiogram.types import Message, CallbackQuery
from config import OWNER_ID
from database.db import set_upi, update_wallet, get_referrer, get_wallet

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
        parts = call.data.split("_")
        user_id = int(parts[1])
        amount = int(parts[2])
    except (ValueError, IndexError):
        await call.answer("Invalid data", show_alert=True)
        return

    # ✅ Update user's wallet and check if user exists
    if not update_wallet(user_id, amount):
        await call.answer("❌ Error: User not found in database!", show_alert=True)
        return

    # ✅ Handle referral bonus
    referrer_id = get_referrer(user_id)
    if referrer_id:
        # Bonus calculation: 0.4%
        bonus = amount * 0.004
        if bonus > 0:
            update_wallet(referrer_id, bonus)
            # Notify referrer
            try:
                await call.bot.send_message(
                    referrer_id,
                    f"💸 You received a referral bonus of <b>{bonus:.2f}</b> coins "
                    f"from user <code>{user_id}</code> deposit!"
                )
            except Exception:
                pass # Referrer might have blocked bot

    await call.answer("✅ Payment approved")

    # ✅ Edit admin message safely
    new_text = f"✅ Payment Approved\n👤 User: <code>{user_id}</code>\n💰 Amount: {amount}"
    if call.message.caption:
        await call.message.edit_caption(caption=new_text)
    else:
        await call.message.edit_text(text=new_text)

    # ✅ Notify user
    new_bal = get_wallet(user_id)
    await call.bot.send_message(
        user_id,
        f"✅ Your payment has been approved 🎉\n💰 {amount} coins added to your wallet\n📊 New Balance: <b>{new_bal}</b> coins"
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
        parts = call.data.split("_")
        user_id = int(parts[1])
        amount = int(parts[2])
    except (ValueError, IndexError):
        await call.answer("Invalid data", show_alert=True)
        return

    await call.answer("❌ Payment declined")

    # ✅ Edit admin message safely
    new_text = f"❌ Payment Declined\n👤 User: <code>{user_id}</code>\n💰 Amount: {amount}"
    if call.message.caption:
        await call.message.edit_caption(caption=new_text)
    else:
        await call.message.edit_text(text=new_text)

    # ✅ Notify user
    await call.bot.send_message(
        user_id,
        "❌ Your payment was declined. Please contact support."
    )
