from aiogram import Router, types
from aiogram.types import CallbackQuery
from database.db import get_referrals, get_wallet

router = Router()

@router.callback_query(lambda c: c.data == "refer_earn")
async def referral_callback(call: CallbackQuery):
    user_id = call.from_user.id
    wallet = get_wallet(user_id)
    referrals = get_referrals(user_id)  # returns list of referrals and their deposits

    text = f"💰 Wallet: <b>{wallet}</b> coins\n🎁 Referrals:\n"
    if not referrals:
        text += "No referrals yet!"
    else:
        for ref in referrals:
            text += f"- <code>{ref[0]}</code> deposited <b>{ref[1]}</b>\n"

    await call.answer()  # -> acknowledge callback
    await call.message.answer(text)
