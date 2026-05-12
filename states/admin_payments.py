from aiogram.fsm.state import State, StatesGroup


class MBankAccountState(StatesGroup):
    add_credentials = State()      # ожидание ввода email:password:blik
    add_bank_custom = State()      # ввод произвольного названия банка
    add_proxy = State()            # ввод прокси (или «Без прокси»)
    edit_proxy = State()
    edit_limit = State()
    edit_blik = State()
