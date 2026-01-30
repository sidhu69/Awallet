from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import main_menu_keyboard, back_button
from database.db import get_wallet
from states.user import UserForm

router = Router()

# =========================
# /menu → SHOW MAIN MENU
# =========================
@router.message(Command("menu"))
async def show_main_menu(message: types.Message):
    wallet = get_wallet(message.from_user.id)
    await message.answer(
        f"👋 <b>Hey there! Welcome to Awallet 💟</b>\n\n"
        "Awallet is always here to help you grow your income.\n"
        f"Your wallet is: <b>{wallet}</b> coins\n"
        "Buy your orders to earn more 💰\n\n"
        "👇 <b>Select an option below:</b>",
        reply_markup=main_menu_keyboard()
    )

@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu_handler(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    wallet = get_wallet(call.from_user.id)
    await call.message.edit_text(
        f"👋 <b>Hey there! Welcome to Awallet 💟</b>\n\n"
        "Awallet is always here to help you grow your income.\n"
        f"Your wallet is: <b>{wallet}</b> coins\n"
        "Buy your orders to earn more 💰\n\n"
        "👇 <b>Select an option below:</b>",
        reply_markup=main_menu_keyboard()
    )
    await call.answer()

# =========================
# HELP HANDLER
# =========================
@router.callback_query(lambda c: c.data == "help")
async def help_handler(call: types.CallbackQuery):
    help_text = (
        "🤖 <b>AWallet Help Center</b>\n\n"
        "💰 <b>Wallet & Deposits</b>\n"
        "• Deposit amount using UPI.\n"
        "• Amount will be added after bot approval.\n"
        "• Minimum deposit is 200.\n\n"
        "🛒 <b>Buying Orders</b>\n"
        "• Use Buy Orders button to place orders\n"
        "• Orders are processed instantly\n"
        "• No refunds after order completion.\n\n"
        "👥 <b>Referral Program</b>\n"
        "• Share your referral link\n"
        "• Earn 0.4% bonus when your referral deposits\n"
        "• Bonus is added automatically to your wallet\n\n"
        "⚠️ <b>Important Rules</b>\n"
        "• Fake payments = permanent ban\n"
        "• Self-referrals are not allowed\n"
        "• Bot will hold your first 300.\n"
        "• Do not send edited screenshots\n\n"
        "🆘 <b>Need Support?</b>\n"
        "• Contact admin @Awalletsupportbot if payment is approved late\n"
        "• Include Transaction ID / Screenshot\n\n"
        "📌 <b>Tip:</b>\n"
        "Invite more users to earn passive coins 💸\n\n"
        "<b>Important note:</b>\n\n"
        "You will not receive your withdrawal if your amount is below 300."
    )
    await call.message.edit_text(help_text, reply_markup=back_button())
    await call.answer()

# =========================
# ACCOUNT SETTINGS HANDLER
# =========================
@router.callback_query(lambda c: c.data == "account_settings")
async def account_settings_handler(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer(
        "⚙️ <b>Account Settings</b>\n\n"
        "Please enter your new UPI ID:\n"
        "👉 कृपया अपना नया UPI ID दर्ज करें",
        reply_markup=back_button()
    )
    await state.set_state(UserForm.upi)
    await call.answer()
