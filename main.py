# awallet_bot.py
# Fixed: FSM context & data consistency in /send → TXID → proof flow using StorageKey

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────

OWNER_ID = 8032922682
BOT_TOKEN = "8471574197:AAHpzznbJ_4bCgzeJD4AjFTr8iJF8X0JC7A"           # ← CHANGE THIS
SUPPORT_USERNAME = "@theawalletsupportbot"

DB_FILE = Path("awallet_users.json")

# Global welcome media info
welcome_media: Optional[dict] = None        # {"file_id": str, "type": "voice"|"audio"}

# ────────────────────────────────────────────────
# DATA
# ────────────────────────────────────────────────

users: Dict[str, Dict[str, Any]] = {}
admins: set[int] = {OWNER_ID}

# ────────────────────────────────────────────────
# STATES
# ────────────────────────────────────────────────

class Registration(StatesGroup):
    waiting_for_name        = State()
    waiting_for_upi         = State()
    waiting_for_upi_confirm = State()


class BuyOrder(StatesGroup):
    waiting_for_amount   = State()
    waiting_for_txid     = State()
    waiting_for_proof    = State()


# ────────────────────────────────────────────────
# PERSISTENCE
# ────────────────────────────────────────────────

def save_db():
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "users": users,
                "admins": list(admins),
                "welcome_media": welcome_media
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logging.error(f"save_db failed: {e}")


def load_db():
    global users, admins, welcome_media
    if not DB_FILE.is_file():
        return
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            users = data.get("users", {})
            admins = set(data.get("admins", [OWNER_ID]))
            welcome_media = data.get("welcome_media")
    except Exception as e:
        logging.error(f"load_db failed: {e}")


# ────────────────────────────────────────────────
# BOT SETUP
# ────────────────────────────────────────────────

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💡 Help",     callback_data="help"),
            InlineKeyboardButton(text="👛 Wallet",    callback_data="wallet"),
        ],
        [
            InlineKeyboardButton(text="🛒 Buy Order", callback_data="buy"),
            InlineKeyboardButton(text="🎧 Support",   callback_data="support"),
        ],
    ])


# ────────────────────────────────────────────────
# Set welcome voice/audio
# ────────────────────────────────────────────────

@router.message(Command("setvn"))
async def cmd_setvn(message: types.Message):
    if message.from_user.id != OWNER_ID:
        await message.reply("Only the bot owner can use this command.")
        return

    replied = message.reply_to_message
    if not replied:
        await message.reply("Reply to a voice message or audio file with /setvn")
        return

    file_id = None
    media_type = None

    if replied.voice:
        file_id = replied.voice.file_id
        media_type = "voice"
    elif replied.audio:
        file_id = replied.audio.file_id
        media_type = "audio"

    if not file_id or not media_type:
        await message.reply("Please reply to a **voice message** or **audio file** (mp3, m4a, ogg, etc.)")
        return

    global welcome_media
    welcome_media = {"file_id": file_id, "type": media_type}
    save_db()

    await message.reply(
        f"✅ Welcome media set!\n"
        f"Type: {media_type}\nFile ID: {file_id}"
    )


# ────────────────────────────────────────────────
# START + REGISTRATION
# ────────────────────────────────────────────────

@router.message(CommandStart(deep_link=False))
async def cmd_start(message: types.Message, state: FSMContext):
    uid_str = str(message.from_user.id)

    if uid_str in users:
        name = users[uid_str].get("name", "User")
        await message.answer(f"Welcome back, {name} 👋", reply_markup=get_main_menu())
        return

    await message.answer(
        "Welcome to Awallet 🌟\n\n"
        "Earn attractive daily returns using our AI-powered system.\n\n"
        "To get started, please enter your full name 👇"
    )

    await state.set_state(Registration.waiting_for_name)
    await state.update_data(reg_user_id=message.from_user.id)


@router.message(Registration.waiting_for_name)
async def reg_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get("reg_user_id") != message.from_user.id:
        await message.answer("Session issue detected. Please use /start again.")
        await state.clear()
        return

    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Please enter a valid name (at least 2 characters).")
        return

    uid_str = str(message.from_user.id)
    users[uid_str] = {
        "name": name,
        "upi": None,
        "balance": 0.0,
        "orders": [],
        "welcome_voice_sent": False
    }
    save_db()

    await message.answer(
        f"Welcome, {name} 👋\n"
        "Your Awallet account has been successfully created.\n\n"
        "To continue, please set up your UPI ID to receive earnings.\n"
        "Please enter your UPI ID (example: name@bank)"
    )
    await state.set_state(Registration.waiting_for_upi)


@router.message(Registration.waiting_for_upi)
async def reg_upi(message: types.Message, state: FSMContext):
    upi = message.text.strip().lower()
    if "@" not in upi or len(upi) < 6:
        await message.answer("Please enter a valid UPI ID (example: name@okaxis)")
        return

    await state.update_data(upi=upi)
    await message.answer("Please re-enter your UPI ID to confirm:")
    await state.set_state(Registration.waiting_for_upi_confirm)


@router.message(Registration.waiting_for_upi_confirm)
async def reg_upi_confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    entered = message.text.strip().lower()
    expected = data.get("upi", "").lower()

    if entered != expected:
        await message.answer("UPI IDs do not match. Please start over with /start")
        await state.clear()
        return

    uid_str = str(message.from_user.id)
    users[uid_str]["upi"] = expected

    await message.answer(
        "✅ UPI ID successfully saved.\n\n"
        "You can now use all Awallet features.",
        reply_markup=get_main_menu()
    )

    global welcome_media
    if welcome_media and not users[uid_str].get("welcome_voice_sent", False):
        try:
            file_id = welcome_media["file_id"]
            mtype = welcome_media["type"]

            if mtype == "voice":
                await message.answer_voice(
                    voice=file_id,
                    caption="🎙️ Welcome to Awallet – quick voice introduction"
                )
            elif mtype == "audio":
                await message.answer_audio(
                    audio=file_id,
                    caption="🎵 Welcome to Awallet – quick audio introduction"
                )

            users[uid_str]["welcome_voice_sent"] = True
            save_db()
        except Exception as e:
            logging.error(f"Failed to send welcome media to {uid_str}: {e}")

    await state.clear()


# ────────────────────────────────────────────────
# BUY ORDER FLOW – FIXED FSM consistency
# ────────────────────────────────────────────────

@router.message(BuyOrder.waiting_for_amount)
async def buy_amount(message: types.Message, state: FSMContext):
    try:
        amt = float(message.text.strip())
        if not 50 <= amt <= 10000:
            raise ValueError
    except:
        await message.answer("Please enter a number between 50 and 10000")
        return

    uid_str = str(message.from_user.id)
    order = {
        "amount": amt,
        "status": "created",
        "created_at": message.date.isoformat(),
        "txid": None,
        "proof_file_id": None
    }
    users[uid_str]["orders"].append(order)
    save_db()

    notify = f"📢 New Order Created\n\nUser ID: {message.from_user.id}\nAmount: ₹{amt:.2f}"
    for aid in admins:
        try:
            await bot.send_message(aid, notify)
        except:
            pass

    await message.answer("⏳ Please wait while we are creating your order...")
    await state.clear()


@router.message(F.photo, F.caption.startswith("/send"))
async def admin_send_qr(message: types.Message):
    if message.from_user.id not in admins:
        return

    command_text = message.caption or message.text or ""
    parts = command_text.strip().split(maxsplit=1)

    if len(parts) < 2:
        await message.reply("Usage: /send <userid>   (attach QR photo and send in one message)")
        return

    try:
        target_uid = int(parts[1])
    except:
        await message.reply("Invalid user ID")
        return

    target_str = str(target_uid)
    if target_str not in users or not users[target_str]["orders"]:
        await message.reply("User has no active orders")
        return

    order_idx = len(users[target_str]["orders"]) - 1
    order = users[target_str]["orders"][order_idx]

    if order["status"] != "created":
        await message.reply("This order is already processed.")
        return

    order["status"] = "qr_sent"
    photo_id = message.photo[-1].file_id

    try:
        await bot.send_photo(
            target_uid,
            photo=photo_id,
            caption=(
                f"Please complete the payment of ₹{order['amount']:.2f} using the QR code below.\n"
                "After payment, send your transaction ID here."
            )
        )

        # ─── FIXED: correctly set state & data for the TARGET user ───
        target_key = StorageKey(
            bot_id=bot.id,
            chat_id=target_uid,
            user_id=target_uid
        )

        await dp.storage.set_state(target_key, BuyOrder.waiting_for_txid)
        await dp.storage.update_data(target_key, {"current_order_index": order_idx})

        await message.reply(f"Payment QR sent to user {target_uid}")
        save_db()
    except Exception as e:
        await message.reply(f"Error sending QR: {str(e)}")


@router.message(BuyOrder.waiting_for_txid)
async def buy_txid(message: types.Message, state: FSMContext):
    txid = message.text.strip()
    if len(txid) < 4:
        await message.answer("Please send a valid transaction ID.")
        return

    data = await state.get_data()
    idx = data.get("current_order_index")

    if idx is None:
        await message.answer("Order session expired. Please create a new order.")
        await state.clear()
        return

    uid_str = str(message.from_user.id)
    users[uid_str]["orders"][idx]["txid"] = txid
    users[uid_str]["orders"][idx]["status"] = "txid_received"
    save_db()

    await message.answer("✅ Transaction ID received.\n\nPlease upload a screenshot of the payment for verification.")
    await state.set_state(BuyOrder.waiting_for_proof)


@router.message(BuyOrder.waiting_for_proof, F.photo)
async def buy_proof(message: types.Message, state: FSMContext):
    data = await state.get_data()
    idx = data.get("current_order_index")

    if idx is None:
        await message.answer("Order session expired. Please create a new order.")
        await state.clear()
        return

    uid_str = str(message.from_user.id)
    users[uid_str]["orders"][idx]["proof_file_id"] = message.photo[-1].file_id
    users[uid_str]["orders"][idx]["status"] = "proof_uploaded"
    save_db()

    await message.answer("⏳ Payment proof received.\nYour order is under verification. You will be notified once confirmed.")
    await state.clear()

    for aid in admins:
        try:
            await bot.send_photo(
                aid,
                photo=message.photo[-1].file_id,
                caption=f"Proof from {message.from_user.id} | Amount: ₹{users[uid_str]['orders'][idx]['amount']}"
            )
        except:
            pass


# ────────────────────────────────────────────────
# OTHER HANDLERS (unchanged)
# ────────────────────────────────────────────────

@router.callback_query(F.data == "help")
async def cb_help(c: types.CallbackQuery):
    await c.message.edit_text(
        "ℹ️ About Awallet\n\n"
        "AI-powered system that analyzes market data in real time.\n"
        "• AI-based analysis\n"
        "• Live market integration\n"
        "• Estimated attractive daily returns\n\n"
        "Earnings are sent to your registered UPI.",
        reply_markup=get_main_menu()
    )
    await c.answer()


@router.callback_query(F.data == "wallet")
async def cb_wallet(c: types.CallbackQuery):
    uid_str = str(c.from_user.id)
    if uid_str not in users:
        await c.message.edit_text("Please register first → /start")
        return

    d = users[uid_str]
    text = (
        f"👛 Your Wallet\n\n"
        f"User ID: {c.from_user.id}\n"
        f"Current Balance: ₹{d['balance']:.2f}\n"
        f"UPI ID: {d.get('upi', 'Not set')}\n\n"
        "Manage UPI:\n"
        "/deleteupi\n"
        "/newupi yourupi@bank"
    )
    await c.message.edit_text(text, reply_markup=get_main_menu())
    await c.answer()


@router.callback_query(F.data == "support")
async def cb_support(c: types.CallbackQuery):
    await c.message.edit_text(
        f"🎧 Support\n\n"
        f"If you have any questions or need assistance, please message:\n"
        f"{SUPPORT_USERNAME}",
        reply_markup=get_main_menu()
    )
    await c.answer()


@router.callback_query(F.data == "buy")
async def cb_buy(c: types.CallbackQuery, state: FSMContext):
    uid_str = str(c.from_user.id)
    if uid_str not in users or not users[uid_str].get("upi"):
        await c.message.edit_text("Please complete registration and set UPI first.")
        return

    await c.message.edit_text(
        "🛒 Buy Order\n\n"
        "Please enter a valid amount between ₹50 and ₹10,000 to purchase an order."
    )
    await state.set_state(BuyOrder.waiting_for_amount)
    await c.answer()


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

    custom_msg = parts[2].strip() if len(parts) > 2 else None
    user_message = (
        custom_msg
        or f"✅ Your order of ₹{amount:.2f} has been successfully confirmed!\n"
           f"Added to your wallet.\nNew balance: ₹{users[target_str]['balance']:.2f}"
    )

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


@router.message(Command("editbalance"))
async def cmd_editbalance(message: types.Message):
    if message.from_user.id not in admins:
        return
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Usage: /editbalance <userid> <new_balance>")
        return
    try:
        uid_str = parts[1]
        new_bal = float(parts[2])
        if uid_str not in users:
            await message.answer("User not found")
            return
        old = users[uid_str]["balance"]
        users[uid_str]["balance"] = new_bal
        save_db()
        await message.answer(f"Balance updated: {uid_str} → ₹{new_bal:.2f}")
        try:
            await bot.send_message(int(uid_str), f"Your balance is now ₹{new_bal:.2f}")
        except:
            pass
    except:
        await message.answer("Invalid number")


@router.message(Command("makeadmin"))
async def cmd_makeadmin(message: types.Message):
    if message.from_user.id != OWNER_ID:
        return
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /makeadmin <userid>")
        return
    try:
        new_a = int(parts[1])
        admins.add(new_a)
        save_db()
        await message.answer(f"User {new_a} is now admin.")
        await bot.send_message(new_a, "You have been promoted to admin.")
    except:
        await message.answer("Invalid ID")


@router.message(Command("newupi"))
async def cmd_newupi(message: types.Message):
    uid_str = str(message.from_user.id)
    if uid_str not in users:
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("Usage: /newupi your@upi")
        return
    upi = parts[1].strip().lower()
    if "@" not in upi:
        await message.answer("Invalid format")
        return
    users[uid_str]["upi"] = upi
    save_db()
    await message.answer(f"UPI updated: {upi}")


@router.message(Command("deleteupi"))
async def cmd_deleteupi(message: types.Message):
    uid_str = str(message.from_user.id)
    if uid_str in users:
        users[uid_str]["upi"] = None
        save_db()
        await message.answer("UPI has been removed.")


@router.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    if await state.get_state():
        await state.clear()
        await message.answer("Process cancelled.", reply_markup=get_main_menu())
    else:
        await message.answer("Nothing to cancel.")


# ────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────

async def main():
    logging.basicConfig(level=logging.INFO)
    load_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
