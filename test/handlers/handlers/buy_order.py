# handlers/buy_order.py - Fixed TXID + proof flow for auto & manual
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext

from config import auto_qr_enabled, auto_qr_file_id, users, admins
from database import save_db
from .registration import get_main_menu  # shared menu

router = Router()

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

    user_upi = users[uid_str].get("upi", "Not set")

    if auto_qr_enabled and auto_qr_file_id:
        try:
            await bot.send_photo(
                message.from_user.id,
                photo=auto_qr_file_id,
                caption=(
                    f"Order created for ₹{amt:.2f}\n\n"
                    "Please complete the payment using the QR code below.\n"
                    "After payment, reply here with your **Transaction ID**."
                )
            )

            await state.set_state(BuyOrder.waiting_for_txid)
            await state.update_data(current_order_index=len(users[uid_str]["orders"]) - 1)

            await message.answer("⏳ Your order is ready! QR code sent above. Proceed with payment.")

            notify_msg = (
                f"🔔 New order (AUTO-QR sent)\n"
                f"User ID: {uid_str}\n"
                f"Amount: ₹{amt:.2f}\n"
                f"UPI: {user_upi}\n"
                f"Status: created (QR auto-sent)"
            )
            for aid in admins:
                try:
                    await bot.send_message(aid, notify_msg)
                except:
                    pass

        except Exception as e:
            logging.error(f"Auto-QR send failed: {e}")
            await message.answer("Order created, but failed to send auto-QR. Please wait for admin.")
    else:
        notify = f"📢 New Order Created\n\nUser ID: {uid_str}\nAmount: ₹{amt:.2f}\nUPI: {user_upi}"
        for aid in admins:
            try:
                await bot.send_message(aid, notify)
            except:
                pass

        await message.answer("⏳ Please wait while we are creating your order... (admin will send QR soon)")

    await state.clear()


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

    await message.answer(
        "✅ Transaction ID received.\n\n"
        "Now please upload a screenshot of the payment for verification."
    )
    await state.set_state(BuyOrder.waiting_for_proof)

    amt = users[uid_str]["orders"][idx]["amount"]
    user_upi = users[uid_str].get("upi", "Not set")

    notify_msg = (
        f"🔔 TXID received\n"
        f"User ID: {uid_str}\n"
        f"Amount: ₹{amt:.2f}\n"
        f"UPI: {user_upi}\n"
        f"TXID: {txid}\n"
        f"Status: TXID_RECEIVED"
    )
    for aid in admins:
        try:
            await bot.send_message(aid, notify_msg)
        except:
            pass


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

    await message.answer(
        "Your payment is under process please wait bot will confirm your payment."
    )
    await state.clear()

    amt = users[uid_str]["orders"][idx]["amount"]
    user_upi = users[uid_str].get("upi", "Not set")
    txid = users[uid_str]["orders"][idx].get("txid", "Not provided")

    notify_msg = (
        f"🔔 Proof uploaded – ready for /confirm\n"
        f"User ID: {uid_str}\n"
        f"Amount: ₹{amt:.2f}\n"
        f"UPI: {user_upi}\n"
        f"TXID: {txid}\n"
        f"Status: PROOF_UPLOADED"
    )

    for aid in admins:
        try:
            await bot.send_message(aid, notify_msg)
            await bot.send_photo(
                aid,
                photo=message.photo[-1].file_id,
                caption=notify_msg
            )
        except:
            pass
