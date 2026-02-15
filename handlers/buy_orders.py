from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from config import OWNER_ID
from database.db import (
    subscribe_user,
    is_user_subscribed,
    save_video
)
from keyboards.main_menu import back_button

router = Router()

SUBSCRIPTION_AMOUNT = 50


# =========================
# CLICK SUBSCRIBE
# =========================
@router.callback_query(F.data == "subscribe")
async def subscribe_start(call: CallbackQuery):
    await call.answer()

    await call.message.answer(
        f"💳 <b>Subscription Required</b>\n\n"
        f"Pay ₹{SUBSCRIPTION_AMOUNT} to activate your account.\n\n"
        f"🏦 UPI: <b>ansh@upi</b>\n\n"
        f"📝 Message while paying: <code>SUB_{call.from_user.id}</code>\n\n"
        f"After payment, click Confirm Payment.",
        reply_markup=back_button()
    )


# =========================
# CONFIRM PAYMENT (Manual Approval)
# =========================
@router.callback_query(F.data == "confirm_subscription")
async def confirm_subscription(call: CallbackQuery):
    await call.answer()

    await call.message.bot.send_message(
        OWNER_ID,
        f"🧾 <b>Subscription Request</b>\n\n"
        f"User ID: <code>{call.from_user.id}</code>\n"
        f"Approve using:\n"
        f"/approve {call.from_user.id}"
    )

    await call.message.answer(
        "✅ Your request has been sent to admin.\n"
        "You will be notified after approval."
    )


# =========================
# VIDEO UPLOAD
# =========================
@router.message(F.video)
async def receive_video(message: Message):
    user_id = message.from_user.id

    if not is_user_subscribed(user_id):
        await message.answer("❌ You must subscribe first.")
        return

    file_id = message.video.file_id
    save_video(user_id, file_id)

    await message.bot.send_video(
        OWNER_ID,
        file_id,
        caption=f"📥 New Video\nUser: {user_id}"
    )

    await message.answer(
        "📤 Your video has been received.\n"
        "You’ll be updated once it is posted."
    )
