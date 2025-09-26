from aiogram.fsm.state import State, StatesGroup
class SupportForm(StatesGroup):
    waiting_for_text  = State()
    chosen_chat = State()
    waiting_for_file = State()
