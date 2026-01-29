from aiogram.fsm.state import StatesGroup, State

class BuyOrder(StatesGroup):
    amount = State()
    screenshot = State()
