from aiogram.fsm.state import State, StatesGroup


class SlotState(StatesGroup):
    waiting_bet = State()
    waiting_spin = State()


class SlotAdminRulesState(StatesGroup):
    waiting_text = State()
