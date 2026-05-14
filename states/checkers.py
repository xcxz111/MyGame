from aiogram.fsm.state import State, StatesGroup


class CheckersState(StatesGroup):
    waiting_bet = State()
    waiting_confirm = State()


class CheckersAdminRulesState(StatesGroup):
    waiting_text = State()
