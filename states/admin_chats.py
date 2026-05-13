from aiogram.fsm.state import State, StatesGroup


class AdminChatsState(StatesGroup):
    waiting_chat_button_title = State()  # подпись кнопки (копируется во все локали)
    waiting_chat_id = State()  # ввод -100... chat_id
