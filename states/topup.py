from aiogram.fsm.state import State, StatesGroup


class TopupState(StatesGroup):
    waiting_amount = State()
