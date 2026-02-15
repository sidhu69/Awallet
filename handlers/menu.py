from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states.user import UserForm
from database.db import get_wallet, is_user_subscribed, subscribe_user, save_video
from keyboards.main_menu import main_menu_keyboard

from config import OWNER_ID

router = Router()


# =========================
# /menu → MAIN MENU
# =========================
@router.message(Command("menu"))
async def show_main_menu(message: types.Message):
    user_id = message.from_user.id
    wallet = get_wallet(user_id)

    await message.answer(
        f"👋 <b>Hey there! Welcome to Awallet 💟</b>\n\n"
        f"Your wallet: <b>{wallet}</b> coins\n"
        "👇 Select an option below:",
        reply_markup=main_menu_keyboard(user_id)
    )


# =========================
# SUBSCRIBE BUTTON → PAYMENT FLOW
# =========================
@router.callback_query(lambda c: c.data == "subscribe")
async def subscribe_handler(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    if is_user_subscribed(user_id):
        await call.answer("✅ You are already subscribed!", show_alert=True)
        return

    await call.message.edit_text(
        "💳 To post a video, first pay the subscription amount.\n\n"
        "1️⃣ Send payment.\n"
        "2️⃣ Send a screenshot of the payment."
    )
    await state.set_state(UserForm.screenshot)
    await call.answer()


# =========================
# RECEIVE PAYMENT SCREENSHOT
# =========================
@router.message(UserForm.screenshot, lambda m: m.content_type in ['photo', 'document'])
async def receive_screenshot(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    # Forward screenshot to admin
    await message.forward(chat_id=OWNER_ID)

    await message.answer(
        "✅ Screenshot received. Admin will confirm your payment soon."
    )
    await state.clear()


# =========================
# POST VIDEO BUTTON
# =========================
@router.callback_query(lambda c: c.data == "post_video")
async def post_video_handler(call: types.CallbackQuery, state: FSMContext):
    user_id = call.from_user.id

    if not is_user_subscribed(user_id):
        await call.answer("❌ You must subscribe first!", show_alert=True)
        return

    await call.message.edit_text("🎬 Send your video to post:")
    await state.set_state(UserForm.video)
    await call.answer()


# =========================
# RECEIVE VIDEO
# =========================
@router.message(UserForm.video, lambda m: m.content_type == 'video')
async def receive_video(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    file_id = message.video.file_id

    save_video(user_id, file_id)

    await message.answer(
        "✅ Video received! It will be approved by admin shortly."
    )
    await state.clear()
