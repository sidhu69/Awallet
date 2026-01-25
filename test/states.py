# states.py - All FSM states
from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    waiting_for_name        = State()
    waiting_for_upi         = State()
    waiting_for_upi_confirm = State()


class BuyOrder(StatesGroup):
    waiting_for_amount   = State()
    waiting_for_txid     = State()
    waiting_for_proof    = State()
