from aiogram.fsm.state import State, StatesGroup


class MBankAccountState(StatesGroup):
    add_credentials = State()      # ожидание ввода email:password:blik
    add_bank_custom = State()      # ввод произвольного названия банка
    add_proxy = State()            # ввод прокси (или «Без прокси»)
    edit_proxy = State()
    edit_limit = State()
    edit_blik = State()


class WithdrawFeeState(StatesGroup):
    waiting_percent = State()


class SlotFeeState(StatesGroup):
    waiting_percent = State()


class CheckersFeeState(StatesGroup):
    waiting_percent = State()


class KmbFeeState(StatesGroup):
    waiting_percent = State()


class ReferralFeeState(StatesGroup):
    waiting_percent = State()
