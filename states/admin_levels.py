from aiogram.fsm.state import State, StatesGroup


class AdminLevelState(StatesGroup):
    waiting_title = State()
    waiting_required = State()
    waiting_reward = State()
    waiting_withdraw_discount = State()
    waiting_referral_bonus = State()
