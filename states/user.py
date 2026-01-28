from aiogram.fsm.state import State, StatesGroup


class UserForm(StatesGroup):
    waiting_for_name = State()
