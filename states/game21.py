from aiogram.fsm.state import State, StatesGroup


class Play21BotState(StatesGroup):
    waiting_bet = State()
    waiting_confirm = State()


class Play21PvpState(StatesGroup):
    waiting_bet = State()
    waiting_confirm = State()


class Game21FeeState(StatesGroup):
    waiting_percent = State()


class Game21RulesState(StatesGroup):
    waiting_text = State()
