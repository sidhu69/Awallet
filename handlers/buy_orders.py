import random
import asyncio
from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states.order import BuyOrder
from keyboards.buy_orders import cancel_order_kb
from keyboards.main_menu import back_button
from config import OWNER_ID
from database.db import get_upi

router = Router()


# =========================
# STEP 1 → CLICK BUY ORDERS
# =========================
@router.callback_query(lambda c: c.data == "buy_orders")
async def buy_orders_start(call: CallbackQuery, state: FSMContext):
    await call.answer()

    await call.message.answer(
        "🛒 Enter order amount (350 – 30000)\n\n"
        "👉 Please write amount you want to buy",
        reply_markup=cancel_order_kb()
    )
    await state.set_state(BuyOrder.amount)


# =========================
# STEP 2 → RECEIVE AMOUNT
# =========================
@router.message(BuyOrder.amount)
async def receive_amount(message: Message, state: FSMContext):
    # 🔒 CRITICAL FIX
    if not message.text:
        await message.answer("❌ Please send numbers only", reply_markup=back_button())
        return

    if not message.text.isdigit():
        await message.answer("❌ Enter valid number", reply_markup=back_button())
        return

    amount = int(message.text)

    if amount <= 0 or amount > 30000:
        await message.answer("❌ Amount must be between 1 and 30000", reply_markup=back_button())
        return

    await state.update_data(amount=amount)

    await message.answer("⏳ Please wait, creating your order...")

    await asyncio.sleep(random.randint(3, 6))

    await message.answer(
        f"💳 <b>Payment Details</b>\n\n"
        f"🔢 Amount: <b>{amount}</b>\n"
        f"🏦 UPI: <b>{get_upi()}</b>\n\n"
        "📸 After payment, send screenshot here",
        reply_markup=back_button()
    )

    await state.set_state(BuyOrder.screenshot)


# =========================
# STEP 3 → RECEIVE SCREENSHOT
# =========================
@router.message(BuyOrder.screenshot)
async def receive_screenshot(message: Message, state: FSMContext):
    if not message.photo:
        await message.answer("❌ Please send payment screenshot only", reply_markup=back_button())
        return

    data = await state.get_data()
    amount = data["amount"]

    await message.answer("⏳ Please wait while we confirm your payment...")

    await message.bot.send_photo(
        chat_id=OWNER_ID,
        photo=message.photo[-1].file_id,
        caption=(
            f"🧾 <b>New Payment Request</b>\n\n"
            f"👤 User ID: <code>{message.from_user.id}</code>\n"
            f"💰 Amount: <b>{amount}</b>"
        ),
        reply_markup=__import__("keyboards.admin").admin.approve_decline_kb(
            message.from_user.id,
            amount
        )
    )

    await message.answer("✅ Request sent to admin!", reply_markup=back_button())
    await state.clear()
