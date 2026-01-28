from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.user import UserForm

router = Router()


@router.message(UserForm.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    name = message.text.strip()

    # Basic validation
    if len(name) < 2:
        await message.answer(
            "❌ Please enter a valid name.\n"
            "❌ कृपया सही नाम दर्ज करें।"
        )
        return

    # Save name (for now only in FSM)
    await state.update_data(name=name)

    await message.answer(
        f"✅ Thank you, {name}!\n"
        f"✅ धन्यवाद, {name}!"
    )

    # Clear state (important)
    await state.clear()
