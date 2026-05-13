from aiogram.fsm.state import State, StatesGroup


class WithdrawState(StatesGroup):
    waiting_amount = State()
    waiting_blik = State()
    waiting_confirm = State()
