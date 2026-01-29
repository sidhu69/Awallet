from aiogram import Router, types
from database.db import get_wallet, get_user, get_referrer, get_referrals  # get_referrals will fetch all users referred by this user

router = Router()


# =========================
# SHOW REFERRAL STATS
# Triggered when user clicks "Refer & Earn"
# =========================
@router.message(lambda m: m.text.lower() in ["refer & earn", "👥 refer & earn"])
async def referral_stats(message: types.Message):
    user_id = message.from_user.id
    wallet = get_wallet(user_id)
    referrals = get_referrals(user_id)  # This function returns a list of tuples (ref_id, total_deposit)

    if not referrals:
        text = f"💰 Your Wallet: <b>{wallet}</b> coins\n\nYou have no referrals yet."
    else:
        text = f"💰 Your Wallet: <b>{wallet}</b> coins\n\n🎁 Your Referrals:\n"
        for ref in referrals:
            ref_user_id, ref_wallet = ref
            text += f"- User ID <code>{ref_user_id}</code> deposited <b>{ref_wallet}</b> coins\n"

    await message.answer(text)
