from aiogram import Router, types
from database.db import get_wallet, get_user, get_referrer, get_referrals

router = Router()

@router.message(lambda m: m.text.lower() == "refer & earn")
async def referral_stats(message: types.Message):
    user_id = message.from_user.id
    wallet = get_wallet(user_id)
    referrals = get_referrals(user_id)  # you will create this in db.py

    text = f"💰 Wallet: <b>{wallet}</b>\n🎁 Referrals:\n"
    for ref in referrals:
        text += f"- {ref[0]} deposited {ref[1]}\n"

    await message.answer(text)
