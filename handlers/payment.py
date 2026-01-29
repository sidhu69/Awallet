from aiogram import Router, types
from database.db import get_wallet, update_wallet

router = Router()


# =========================
# ADMIN CONFIRMS PAYMENT
# =========================
@router.message(commands=["confirm_payment"])  # Owner uses this
async def confirm_payment(message: types.Message):
    # Format: /confirm_payment <user_id> <amount>
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Usage: /confirm_payment <user_id> <amount>")
        return

    try:
        user_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer("❌ Invalid user_id or amount")
        return

    # ✅ Update wallet
    update_wallet(user_id, amount)
    new_balance = get_wallet(user_id)

    # Notify user
    try:
        await message.bot.send_message(
            user_id,
            f"✅ Your payment has been approved, your new wallet amount is {new_balance} coins. "
            "Please send /menu to refresh your wallet 🎉"
        )
    except Exception as e:
        await message.answer(f"⚠ Could not notify user: {e}")

    # Confirm to admin
    await message.answer(f"💰 Payment of {amount} coins added to user {user_id}. New balance: {new_balance}")
