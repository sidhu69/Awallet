from aiogram import Router, types
from aiogram.types import CallbackQuery
from database.db import get_wallet, update_wallet

router = Router()


# =========================
# OWNER APPROVES PAYMENT
# =========================
@router.callback_query(lambda c: c.data.startswith("approve_"))
async def approve_payment(call: CallbackQuery):
    # Format: approve_userid_amount
    _, user_id, amount = call.data.split("_")
    user_id = int(user_id)
    amount = int(amount)

    # Update user's wallet
    update_wallet(user_id, amount)
    new_balance = get_wallet(user_id)

    # Notify the user
    await call.bot.send_message(
        user_id,
        f"✅ Your payment has been approved, your new wallet amount is {new_balance} coins. "
        "Please send /menu to refresh your wallet 🎉"
    )

    # Confirm to owner
    await call.message.edit_text(f"✅ Payment approved for user {user_id}, added {amount} coins.")


# =========================
# OWNER REJECTS PAYMENT
# =========================
@router.callback_query(lambda c: c.data.startswith("reject_"))
async def reject_payment(call: CallbackQuery):
    # Format: reject_userid_amount
    _, user_id, amount = call.data.split("_")
    user_id = int(user_id)
    amount = int(amount)

    # Notify the user
    await call.bot.send_message(
        user_id,
        f"❌ Your payment of {amount} coins was rejected by the owner."
    )

    # Confirm to owner
    await call.message.edit_text(f"❌ Payment rejected for user {user_id}.")
