from aiogram.fsm.state import State, StatesGroup


class KmbState(StatesGroup):
    waiting_wins = State()
    waiting_bet = State()
    waiting_confirm = State()


class KmbAdminRulesState(StatesGroup):
    waiting_text = State()
