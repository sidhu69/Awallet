# handlers/admin_commands.py
from aiogram import Router, types

from config import admins, users
from database import save_db

router = Router()

@router.message(Command("confirm"))
async def cmd_confirm(message: types.Message):
    if message.from_user.id not in admins:
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 2:
        await message.reply("Usage: /confirm <user_id> [optional custom message]")
        return

    try:
        target_uid = int(parts[1])
    except ValueError:
        await message.reply("Invalid user ID format")
        return

    target_str = str(target_uid)
    if target_str not in users:
        await message.reply(f"User {target_uid} not found")
        return

    if not users[target_str]["orders"]:
        await message.reply(f"User {target_uid} has no orders")
        return

    latest_order = users[target_str]["orders"][-1]
    if latest_order["status"] != "proof_uploaded":
        await message.reply(f"Latest order status is '{latest_order['status']}' – not awaiting confirmation")
        return

    amount = latest_order["amount"]
    users[target_str]["balance"] += amount
    latest_order["status"] = "completed"

    custom_msg = parts[2].strip() if len(parts) > 2 else "payment added to your wallet successfully"
    user_message = f"✅ {custom_msg}\nNew balance: ₹{users[target_str]['balance']:.2f}"

    try:
        await bot.send_message(target_uid, user_message)
    except Exception as e:
        await message.reply(f"Order confirmed, but failed to notify user: {str(e)}")
    else:
        await message.reply(
            f"✅ Order confirmed for user {target_uid}\n"
            f"₹{amount:.2f} added\n"
            f"New balance: ₹{users[target_str]['balance']:.2f}"
        )

    save_db()


@router.message(Command("w"))
async def cmd_withdraw(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return

    parts = message.text.split()
    if len(parts) != 3:
        await message.reply("Usage: /w <userid> <amount>")
        return

    try:
        target_uid = int(parts[1])
        amount = float(parts[2])
    except:
        await message.reply("Invalid format. Use: /w <userid> <amount>")
        return

    target_str = str(target_uid)
    if target_str not in users:
        await message.reply(f"User {target_uid} not found")
        return

    current_bal = users[target_str]["balance"]
    if current_bal < amount:
        await message.reply(f"Insufficient balance. Current: ₹{current_bal:.2f}")
        return

    users[target_str]["balance"] -= amount
    save_db()

    try:
        await bot.send_message(
            target_uid,
            f"💸 Withdrawal of ₹{amount:.2f} processed.\n"
            f"New balance: ₹{users[target_str]['balance']:.2f}"
        )
    except:
        pass

    await message.reply(
        f"✅ Withdrawal processed\n"
        f"User: {target_uid}\n"
        f"Amount: ₹{amount:.2f}\n"
        f"New balance: ₹{users[target_str]['balance']:.2f}"
    )


# Other admin commands (editbalance, makeadmin, newupi, deleteupi, cancel) remain unchanged
# Copy them from your old file if needed - they are not changed here
