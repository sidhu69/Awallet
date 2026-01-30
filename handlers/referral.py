from aiogram import Router, types
from database.db import get_wallet, get_referrals
from config import BOT_TOKEN

router = Router()


# =========================
# SHOW REFERRAL STATS
# Triggered when user clicks "Refer & Earn"
# =========================
@router.callback_query(lambda c: c.data == "refer_earn")
async def referral_stats_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    wallet = get_wallet(user_id)
    referrals = get_referrals(user_id)
    
    # Get bot username for referral link
    bot = await call.bot.get_me()
    ref_link = f"https://t.me/{bot.username}?start={user_id}"

    text = f"<b>👥 Refer & Earn</b>\n\n"
    text += f"💰 Your Wallet: <b>{wallet}</b> coins\n"
    text += f"🔗 Your Referral Link:\n<code>{ref_link}</code>\n\n"
    text += "🎁 <i>Earn 0.4% bonus from every deposit your referrals make!</i>\n\n"

    if not referrals:
        text += "📊 You have no referrals yet."
    else:
        text += "📊 <b>Your Referrals:</b>\n"
        for ref in referrals:
            ref_user_id, ref_wallet = ref
            text += f"- User ID <code>{ref_user_id}</code> (Balance: {ref_wallet})\n"

    await call.message.edit_text(text)
    await call.answer()


@router.message(lambda m: m.text and m.text.lower() in ["refer & earn", "👥 refer & earn"])
async def referral_stats_message(message: types.Message):
    user_id = message.from_user.id
    wallet = get_wallet(user_id)
    referrals = get_referrals(user_id)
    
    bot = await message.bot.get_me()
    ref_link = f"https://t.me/{bot.username}?start={user_id}"

    text = f"<b>👥 Refer & Earn</b>\n\n"
    text += f"💰 Your Wallet: <b>{wallet}</b> coins\n"
    text += f"🔗 Your Referral Link:\n<code>{ref_link}</code>\n\n"
    text += "🎁 <i>Earn 0.4% bonus from every deposit your referrals make!</i>\n\n"

    if not referrals:
        text += "📊 You have no referrals yet."
    else:
        text += "📊 <b>Your Referrals:</b>\n"
        for ref in referrals:
            ref_user_id, ref_wallet = ref
            text += f"- User ID <code>{ref_user_id}</code> (Balance: {ref_wallet})\n"

    await message.answer(text)
