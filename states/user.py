from aiogram.fsm.state import StatesGroup, State

class UserForm(StatesGroup):
    name = State()        # user enters their name
    upi = State()         # user enters their UPI ID
    subscribe = State()   # user clicks Subscribe / chooses plan
    screenshot = State()  # user sends payment screenshot
    post_video = State()  # user can post video after approval
