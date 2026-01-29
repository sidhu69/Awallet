from aiogram.fsm.state import StatesGroup, State

class UserForm(StatesGroup):
    name = State()
    upi = State()
