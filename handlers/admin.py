from aiogram import Router
from aiogram.types import Message, CallbackQuery
from config import OWNER_ID
from keyboards.main_menu import main_menu_keyboard
from database.db import (
    set_upi,
    set_user_subscribed,
    update_wallet,
    get_referrer,
)

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
# OWNER: APPROVE SUBSCRIPTION
# callback_data: approve_sub_<user_id>
# =========================
@router.callback_query(lambda c: c.data.startswith("approve_sub_"))
async def approve_subscription(call: CallbackQuery):
    if call.from_user.id != OWNER_ID:
        await call.answer("Not authorized", show_alert=True)
        return

    try:
        user_id = int(call.data.split("_")[2])
    except (ValueError, IndexError):
        await call.answer("Invalid data", show_alert=True)
        return

    # ✅ Mark user as subscribed
    set_user_subscribed(user_id)

    # ✅ Referral fixed bonus (₹5 example)
    referrer_id = get_referrer(user_id)
    if referrer_id:
        bonus = 5
        update_wallet(referrer_id, bonus)

        try:
            await call.bot.send_message(
                referrer_id,
                f"💸 You received ₹{bonus} referral bonus from user <code>{user_id}</code> subscription!"
            )
        except Exception:
            pass

    await call.answer("✅ Subscription approved")

    # ✅ Update admin message
    new_text = (
        f"✅ Subscription Approved\n"
        f"👤 User: <code>{user_id}</code>\n"
        f"💳 Amount: ₹50"
    )

    if call.message.caption:
        await call.message.edit_caption(caption=new_text)
    else:
        await call.message.edit_text(text=new_text)

    # ✅ Notify user
    await call.bot.send_message(
        user_id,
        "✅ Your ₹50 subscription has been approved.\n\n"
        "You can now submit your video for review.",
        reply_markup=main_menu_keyboard(user_id)
    )


# =========================
# OWNER: DECLINE SUBSCRIPTION
# callback_data: decline_sub_<user_id>
# =========================
@router.callback_query(lambda c: c.data.startswith("decline_sub_"))
async def decline_subscription(call: CallbackQuery):
    if call.from_user.id != OWNER_ID:
        await call.answer("Not authorized", show_alert=True)
        return

    try:
        user_id = int(call.data.split("_")[2])
    except (ValueError, IndexError):
        await call.answer("Invalid data", show_alert=True)
        return

    await call.answer("❌ Subscription declined")

    new_text = (
        f"❌ Subscription Declined\n"
        f"👤 User: <code>{user_id}</code>\n"
        f"💳 Amount: ₹50"
    )

    if call.message.caption:
        await call.message.edit_caption(caption=new_text)
    else:
        await call.message.edit_text(text=new_text)

    await call.bot.send_message(
        user_id,
        "❌ Your subscription payment was declined.\nPlease contact support."
    )
