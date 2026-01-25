# handlers/registration.py
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

from config import welcome_media, users
from database import save_db

router = Router()

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
                await message.answer_voice(voice=file_id, caption="🎙️ Welcome to Awallet")
            elif mtype == "audio":
                await message.answer_audio(audio=file_id, caption="🎵 Welcome to Awallet")

            users[uid_str]["welcome_voice_sent"] = True
            save_db()
        except Exception as e:
            logging.error(f"Failed to send welcome media: {e}")

    await state.clear()
