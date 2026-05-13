"""FSM для создания игры в админ-панели."""

from aiogram.fsm.state import State, StatesGroup


class AdminCreateGameState(StatesGroup):
    waiting_chat = State()         # выбор целевого чата (если их несколько)
    waiting_forum_topic = State()   # тема форума (если у чата включены Topics)
    waiting_participants = State()  # min/max участников: "10/100"
    waiting_prizes = State()        # призы построчно: 20\n10\n5
    waiting_min_topup = State()     # мин. сумма пополнений (с опц. датой)
    waiting_entry_fee = State()     # стоимость взноса (0 = бесплатно)
    waiting_datetime = State()      # дата и время старта
    waiting_confirm = State()       # подтверждение
