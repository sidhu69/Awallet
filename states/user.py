from aiogram.fsm.state import StatesGroup, State

class UserForm(StatesGroup):
    name = State()        # Optional if you want to collect user's name
    upi = State()         # For registration UPI
    screenshot = State()  # Waiting for payment screenshot
    video = State()       # Waiting for user video upload
