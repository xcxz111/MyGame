"""Тексты кнопок по языку (по образцу старого бота — только нужные строки)."""

from typing import Optional

DEFAULT_LANG = "ru"

LANG_NAMES = {
    "en": "🇬🇧 English",
    "ru": "🇷🇺 Русский",
    "pl": "🇵🇱 Polski",
    "uk": "🇺🇦 Українська",
}

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        "choose_language": "Выберите язык / Choose language:",
        "welcome_menu": "Добро пожаловать в бота для игр",
        "welcome_user_id": "Ваш ID: {user_id}",
        "welcome_balance": "Ваш баланс: {balance} PLN",
        "btn_cabinet": "💼Личный кабинет💼",
        "btn_topup": "💳 Пополнить баланс",
        "topup_enter_amount": "💳 <b>Пополнение баланса</b>\n\nВведите сумму пополнения в PLN (от {min} до {max} PLN):",
        "topup_invalid_amount": "❌ Неверная сумма. Введите число (например 50).",
        "topup_out_of_range": "❌ Сумма должна быть от {min} до {max} PLN.",
        "topup_no_accounts": "⚠️ Пополнения временно недоступны — нет активных платежных аккаунтов. Попробуйте позже.",
        "topup_order_created": (
            "💳 <b>Заявка на пополнение создана</b>\n\n"
            "Сумма: <b>{amount} PLN</b>\n"
            "Номер заявки: <code>{order_id}</code>\n\n"
            "📱 Сделайте BLIK-перевод на номер:\n<code>{blik}</code>\n\n"
            "⚠️ <b>В назначении платежа обязательно укажите код:</b>\n<code>{order_id}</code>\n\n"
            "После получения платежа баланс зачислится автоматически."
        ),
        "topup_btn_cancel_order": "❌ Отменить заявку",
        "topup_order_cancelled": "❌ Заявка <code>{order_id}</code> отменена.",
        "topup_order_not_found": "❌ Заявка не найдена или уже закрыта.",
        "btn_withdraw": "💸 Запросить вывод средств",
        "btn_cancel_withdraw": "❌ Отменить вывод средств",
        "withdraw_enter_amount": (
            "💸 <b>Вывод средств</b>\n\n"
            "Введите сумму вывода в PLN (минимум {min} PLN).\n"
            "Комиссия: <b>{fee}%</b>\n"
            "⏱ Вывод осуществляется в течение 24 часов."
        ),
        "withdraw_invalid_amount": "❌ Неверная сумма. Введите число (например 150).",
        "withdraw_below_min": "❌ Вывод доступен от {min} PLN.",
        "withdraw_not_enough": "❌ Недостаточно средств. Ваш баланс: {balance} PLN.",
        "withdraw_enter_blik": "📱 Введите номер BLIK (минимум 9 цифр):",
        "withdraw_invalid_blik": "❌ Неверный формат BLIK. Минимум 9 цифр.",
        "withdraw_confirm": (
            "💸 <b>Подтверждение вывода</b>\n\n"
            "Сумма с баланса: <b>{amount} PLN</b>\n"
            "Комиссия: <b>{fee}%</b> ({fee_amount} PLN)\n"
            "К выплате: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "Подтвердить вывод?"
        ),
        "withdraw_btn_yes": "✅ Да",
        "withdraw_btn_no": "❌ Нет",
        "withdraw_created": (
            "✅ <b>Заявка на вывод создана</b>\n\n"
            "Номер: <code>#{id}</code>\n"
            "К выплате: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "⏱ Вывод будет произведён в течение 24 часов."
        ),
        "withdraw_cancel_ask": "❓ Вы уверены, что хотите отменить вывод <code>#{id}</code>?",
        "withdraw_cancelled": "✅ Вывод <code>#{id}</code> отменён. Деньги возвращены на баланс.",
        "withdraw_not_pending": "❌ Заявка не найдена или уже обработана.",
        "withdraw_already_pending": "⚠️ У вас уже есть активная заявка на вывод. Отмените её, чтобы создать новую.",
        "withdraw_admin_message": (
            "🏦 <b>Новый запрос на вывод</b>\n\n"
            "👤 {mention}{username}\n"
            "🆔 <code>{user_id}</code>\n"
            "💸 Запрошено: <b>{amount} PLN</b>\n"
            "🧾 Комиссия: {fee}% ({fee_amount} PLN)\n"
            "💵 К выплате: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>"
        ),
        "withdraw_admin_btn_approve": "✅ Принять",
        "withdraw_admin_approved": "✅ <b>ОПЛАЧЕНО</b>",
        "withdraw_admin_cancelled": "❌ <b>ОТМЕНЕНО</b>",
        "withdraw_approved_user": (
            "✅ Ваш вывод <code>#{id}</code> на сумму <b>{payout} PLN</b> отправлен."
        ),
        "cabinet_title": "💼 Личный кабинет",
        "cabinet_balance": "💰 Баланс: <b>{balance} PLN</b>",
        "btn_signup": "🎮 Записаться на игру 🎯🎳🎲",
        "main_menu_chat_fallback": "💬 Чат",
        "btn_play_21_bot": "♠️♥️Играть в 21♣️♦️",
        "btn_casino": "🎰 Казино 🎰",
        "btn_admin": "Админка",
        "btn_lang": "🌐",
        "btn_main": "🏠 Главная",
        "btn_back": "← Назад",
        "admin_title": "Админка",
        "admin_no_access": "⛔ Нет доступа",
        "admin_btn_games": "🎯 Игры",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Казино",
        "admin_btn_checkers": "🔴 Шашки",
        "admin_btn_kmb": "🪖 КМБ",
        "admin_btn_stats": "📊 Статистика",
        "admin_btn_bot_settings": "⚙️ Настройки бота",
        "admin_games_title": "🎯 <b>Игры</b>",
        "admin_btn_create_game": "➕ Создать игру",
        "admin_btn_active_games": "🟢 Текущие игры",
        "admin_btn_past_games": "📚 Прошедшие игры",
        "admin_wip": "🚧 В разработке",
        "admin_settings_title": "⚙️ Настройки бота",
        "admin_btn_payments": "💳 Настройка платежей",
        "admin_btn_fees": "💸 Настройка комиссий",
        "admin_btn_withdraw_fee": "💸 Комиссия вывода",
        "admin_fees_title": "💸 <b>Настройка комиссий</b>",
        "admin_pay_title": "<b>MBanks</b> — аккаунты:",
        "admin_pay_empty": "<b>MBanks</b>\nАккаунтов нет.",
        "admin_pay_btn_add": "➕ Добавить аккаунт",
        "admin_pay_btn_withdraw_fee": "💸 Комиссия вывода",
        "admin_withdraw_fee_title": "💸 <b>Комиссия вывода</b>\n\nТекущее значение: <b>{percent}%</b>\n\nВведите новый процент (например <code>5</code> или <code>2.5</code>):",
        "admin_withdraw_fee_invalid": "❌ Неверный формат. Введите число от 0 до 100 (например <code>5</code> или <code>2.5</code>).",
        "admin_withdraw_fee_updated": "✅ Комиссия вывода обновлена: <b>{percent}%</b>",
        "admin_btn_game21_fees": "♠️ 21 — комиссии",
        "admin_fees_21_title": (
            "♠️ <b>Комиссии игры 21</b>\n\n"
            "Против бота: <b>{bot}%</b>\n"
            "Между пользователями: <b>{users}%</b>"
        ),
        "admin_game21_fee_btn_bot": "Против бота",
        "admin_game21_fee_btn_users": "Между пользователями",
        "admin_game21_fee_bot_title": "💸 Комиссия 21 (против бота)\n\nТекущее: <b>{percent}%</b>\n\nВведите новый процент:",
        "admin_game21_fee_users_title": "💸 Комиссия 21 (PvP)\n\nТекущее: <b>{percent}%</b>\n\nВведите новый процент:",
        "admin_game21_fee_updated": "✅ Комиссия 21 обновлена: <b>{percent}%</b>",
        "admin_21_title": (
            "♠️ <b>Режим 21</b>\n\n"
            "Против бота: {bot}\n\n"
            "Комиссии: бот {bot_fee}% · PvP {users_fee}%\n\n"
            "Включите PvP для каждого подключённого чата. Если бот уже знает темы форума в чате, после включения откроется экран — где можно играть (как в «Чаты → Темы для игр»)."
        ),
        "admin_21_on": "🟢 вкл",
        "admin_21_off": "⚪ выкл",
        "admin_21_btn_bot_on": "Против бота: выключить",
        "admin_21_btn_bot_off": "Против бота: включить",
        "admin_21_btn_users_on": "PvP глобально: выключить",
        "admin_21_btn_users_off": "PvP глобально: включить",
        "admin_21_chat_pvp_on": "PvP в «{title}»: выкл",
        "admin_21_chat_pvp_off": "PvP в «{title}»: вкл",
        "game21_active_notice": "У вас уже есть активная игра в 21. Сначала завершите её.",
        "game21_bot_midgame_menu_blocked": (
            "Вы сейчас находитесь в активной игре. Сначала завершите текущую игру."
        ),
        "game21_busy_screen_text": "У вас уже есть активная игра в чате {chat}",
        "game21_busy_screen_text_bot": (
            "У вас уже есть активная игра с ботом. Доиграйте партию в этом чате."
        ),
        "game21_btn_abort_session": "Отменить игру",
        "game21_active_cancelled_toast": "Текущая сессия 21 отменена.",
        "game21_no_active_search_to_cancel": (
            "Нет активного поиска соперника (поиск уже завершён или игра началась)."
        ),
        "game21_pvp_choose_topic": "Выберите игровую комнату (🟢 свободна, 🔴 занята):",
        "game21_pvp_topic_free": "🟢",
        "game21_pvp_topic_busy": "🔴",
        "game21_pvp_topic_general": "Общий чат",
        "game21_pvp_search_post_failed": "Не удалось опубликовать поиск в чате. Ставка возвращена.",
        "game21_pvp_decide_prompt_other": "{name}, бросьте кубик 🎲 один раз.",
        "game21_menu_title": "Режим 21",
        "game21_btn_rules": "Правила",
        "game21_btn_vs_bot": "Играть против бота",
        "game21_btn_vs_user_chat": "Играть против пользователя в чате",
        "game21_coming_soon_all_off": "Игра 21 пока недоступна.",
        "game21_coming_soon_play": "Игра 21 против бота недоступна.",
        "game21_enter_bet": "Введите сумму ставки (PLN):",
        "game21_bet_invalid": "Неверная сумма. Введите положительное число.",
        "game21_not_enough_balance": "Недостаточно средств на балансе.",
        "game21_confirm_bet_with_win": "Ставка: {amount} PLN\nВозможный выигрыш: {win} PLN\n\nСогласны?",
        "game21_btn_yes": "Да",
        "game21_btn_no": "Нет",
        "game21_cancelled": "Отменено.",
        "game21_rules_title": "<b>Правила игры 21</b>",
        "game21_rules": "См. разделы ниже.",
        "game21_rules_bot": (
            "<b>Против бота</b>\n"
            "Бросайте 🎲 в ЛС. Минимум 16, затем «Хватит». Бот бросает после вас."
        ),
        "game21_rules_users": (
            "<b>PvP в чате {chat_title}</b>\n"
            "Поиск соперника, затем кубик для очередности и раунд до 21."
        ),
        "game21_throw_now": "Бросайте кубик 🎲",
        "game21_player_result": "Ваш результат: {total}",
        "game21_player_busted": "Ваш результат: {total}\nПеребор!",
        "game21_player_blackjack": "У вас 21!",
        "game21_player_can_stop": "Ваш результат: {total}\nМожно продолжать или нажать «Хватит».",
        "game21_btn_stop": "Хватит",
        "game21_bot_turn_start": "Ход бота.",
        "game21_bot_result": "Результат бота: {total}",
        "game21_result_win": "Вы выиграли!",
        "game21_result_lose": "Вы проиграли.",
        "game21_result_draw": "Ничья.",
        "game21_end_bot_win": (
            "<b>Вы выиграли!</b>\n"
            "На баланс зачислено <b>{payout} PLN</b>.\n"
            "Счёт: вы {player_total} — бот {bot_total}."
        ),
        "game21_end_bot_lose": "Вы проиграли {bet} PLN\nСчёт: вы {player_total} — бот {bot_total}.",
        "game21_end_bot_lose_bust": "Вы проиграли {bet} PLN\nПеребор: {player_total}.",
        "game21_end_bot_draw": (
            "<b>Ничья.</b>\n"
            "Ставка <b>{bet} PLN</b> возвращена на баланс.\n"
            "Счёт: {player_total} — {bot_total}."
        ),
        "game21_pvp_enter_bet": "Введите сумму ставки (PLN):\n\nДля игры в 21 в {room}",
        "game21_pvp_confirm": "Согласны начать поиск соперника?\nСтавка: {amount} PLN\nВозможный выигрыш: {win} PLN",
        "game21_pvp_search_started": (
            "Поиск соперника запущен\n\n"
            "С вашего баланса списана ставка {amount} PLN"
        ),
        "game21_pvp_choose_chat": "Выберите чат:",
        "game21_pvp_no_available_chat": "Нет доступных чатов для PvP.",
        "game21_pvp_must_join_chat": "Нужно состоять в чате: {chat_title}",
        "game21_pvp_not_member_title": "Вы не в игровом чате",
        "game21_pvp_not_member_intro": "Чтобы играть в 21 с пользователем, вступите в чат по ссылке ниже. После этого снова нажмите «Играть против пользователя в чате».",
        "game21_pvp_main_active_exists": "Нельзя создать запрос на игру так как там в данный момент проходит игра.",
        "game21_pvp_active_exists": "В этом слоте уже идёт игра или поиск.",
        "game21_pvp_self_accept_forbidden": "Вы не можете играть сам с собой.",
        "game21_pvp_search_post": (
            "{user} ищет соперника в 21\n\n"
            "Ставка: {amount} PLN\nВозможный выигрыш: {win} PLN\n\n"
            "Игра на баланс бота {bot_link}"
        ),
        "game21_pvp_btn_accept": "Принять",
        "game21_pvp_match_title": "Игра в 21",
        "game21_pvp_match_started_in_topic": "Игра в 21 началась в {room}",
        "game21_pvp_match_prize": "<b>Сумма выигрыша: {win} PLN</b>",
        "game21_pvp_match_rules_heading": "Правила игры:",
        "game21_pvp_rules_body": (
            "В начале каждый один раз бросает кубик 🎲 — у кого меньше, тот ходит первым. "
            "Дальше по очереди набираете очки, цель — как можно ближе к 21, но не больше. "
            "Когда счёт совпал у обоих и наступила нужная фаза, можно «Хватит». "
            "После остановок или перебора сравниваются суммы; возможна ничья."
        ),
        "game21_pvp_started": (
            "Игра 21\n{p1}\n{p2}\n\nСтавка: {amount} PLN · выигрыш до {win} PLN\n{bot_link}"
        ),
        "game21_pvp_general_started_notice": (
            "Игра между {p1} и {p2} в 21 началась в <b>{room}</b>."
        ),
        "game21_pvp_topic_started_notice": (
            "Игра между {p1} и {p2} в 21 началась.\n\nПриз: {prize} PLN."
        ),
        "game21_pvp_decide_first": "{players} — бросьте кубик 🎲 по одному разу (кто меньше, ходит первым).",
        "game21_pvp_decide_roll_result": "{name}:, результат: {value}",
        "game21_pvp_decide_tie": "Результаты равны. Бросьте еще по одному разу.",
        "game21_pvp_turn_prompt": "{name}, ваш ход. Бросайте 🎲",
        "game21_pvp_player_result": "{name}, результат: {total}",
        "game21_pvp_player_busted": "{name}, результат: {total} — перебор!",
        "game21_pvp_player_blackjack": "{name} — 21!",
        "game21_pvp_player_can_stop": "{name}, результат: {total}. Можно «Хватит» или ещё бросок.",
        "game21_pvp_stop_announce": "Игрок {name} сказал «Хватит».\nЕго результат: {total}",
        "game21_pvp_not_your_turn_stop": "Сейчас ход игрока {name}",
        "game21_pvp_stop_only_on_equal": "«Хватит» доступно только при равном счёте.",
        "game21_pvp_winner": (
            "Игра окончена.\n"
            "Победитель: {name}\n\n"
            "Ваш выйгрыш {payout} PLN добавлен на баланс в боте {bot_link}"
        ),
        "game21_pvp_draw": "Ничья. Возврат {amount} PLN · {bot_link}",
        "game21_pvp_pm_bet_deducted": "Списана ставка {amount} PLN.",
        "game21_pvp_search_not_accepted": "Никто не принял заявку. Возврат {amount} PLN.",
        "game21_pvp_topic_forbidden": "Эта тема недоступна для игры.",
        "game21_pvp_topics_restricted_empty": "В этом чате нет тем, разрешённых администратором для игр.",
        # ---- Chats settings ----
        "admin_chats_title": "💬 <b>Подключённые чаты</b>",
        "admin_chats_empty": "Чатов пока нет.",
        "admin_chats_list_line": "• <code>{chat_id}</code> · {title}",
        "admin_chats_btn_add": "➕ Добавить чат",
        "admin_chats_btn_delete": "🗑 Удалить чат",
        "admin_chats_btn_game_topics": "📋 Темы для игр",
        "admin_chats_topics_choose_chat": "Выберите чат, в котором настроить, в каких темах форума можно играть (21 и игры с кубиком):",
        "admin_chats_topics_not_forum": "Этот чат не форум-супергруппа с темами — настройка не нужна.",
        "admin_chats_topics_chat_unavailable": "Не удалось открыть чат.",
        "admin_chats_topics_body_open": (
            "📋 <b>Темы для игр</b>: {title}\n\n"
            "Сейчас ограничений нет — PvP 21 и создание игр доступны во всех известных темах и в общем чате.\n\n"
            "Нажмите «Включить ограничения», чтобы явно выбрать, где разрешены игры (список заполнится текущими темами; снимите лишние галочки)."
        ),
        "admin_chats_topics_body_restricted": (
            "📋 <b>Темы для игр</b>: {title}\n\n"
            "Включён список разрешённых тем. Игры только там, где отмечено ✅.\n\n"
            "«Снять ограничения» — снова разрешить везде."
        ),
        "admin_chats_topics_btn_enable": "Включить ограничения по темам",
        "admin_chats_topics_btn_disable": "Снять ограничения (все темы)",
        "admin_chats_enter_button_title": (
            "Введите <b>название кнопки</b> — так она будет отображаться пользователям при выборе чата "
            "(для каждого языка интерфейса можно задать свой текст позже; сейчас одно и то же название "
            "запишется для ru / en / uk / pl).\n\n"
            "Длина до 200 символов."
        ),
        "admin_chats_invalid_button_title": "❌ Введите непустое название (до 200 символов).",
        "admin_chats_enter_chat_id": (
            "Введите <b>ID чата</b> (например <code>-1001234567890</code>).\n\n"
            "Чтобы узнать ID: добавьте бота в группу и перешлите оттуда любое сообщение боту "
            "<a href=\"https://t.me/userinfobot\">@userinfobot</a>, либо используйте сервис вроде getidsbot."
        ),
        "admin_chats_invalid_id": "❌ Неверный формат. Введите целое число, начинающееся с <code>-100</code>.",
        "admin_chats_already_added": "⚠️ Этот чат уже подключён.",
        "admin_chats_added": "✅ Чат <code>{chat_id}</code> подключён.",
        "admin_chats_invite_ok": "✅ Ссылка-приглашение создана автоматически.",
        "admin_chats_invite_link_failed": (
            "⚠️ Не удалось получить invite-ссылку: проверьте, что бот добавлен в чат как <b>администратор</b> "
            "с правом приглашать участников (или что у группы включены приглашения по ссылке)."
        ),
        "admin_chats_session_lost": "⚠️ Сессия добавления сброшена. Начните снова с «Добавить чат».",
        "admin_chats_delete_choose": "Выберите чат для удаления:",
        "admin_chats_delete_confirm": "Удалить чат <code>{chat_id}</code>?",
        "admin_chats_deleted": "✅ Чат удалён.",
        "admin_chats_delete_none": "Нет подключённых чатов для удаления.",
        # ---- Games create FSM ----
        "admin_game_no_chats": "⚠️ Сначала подключите хотя бы один чат в «Настройки бота → Настройка чатов».",
        "admin_game_pick_chat": "В каком чате анонсировать игру?",
        "admin_game_pick_forum_topic": "📂 <b>Тема форума</b>\n\nВыберите тему, где будет проходить игра (анонс, раунды, броски).\n\nПодпись «Ветка · id …» значит, что бот запомнил только внутренний номер ветки (Telegram не присылает название в обычных сообщениях). Чтобы было как в чате, один раз переименуйте тему в группе — бот обновит название.",
        "admin_game_pick_forum_topic_empty": "📂 <b>Тема форума</b>\n\nВ списке пусто: Telegram не отдаёт список тем через API, бот запоминает ветки из сообщений и сервисных событий.\n\nЕсли темы уже есть: отправьте в каждую нужную тему любое сообщение (или один раз переименуйте тему), затем нажмите «🔄 Обновить список тем».\n\nМожно пропустить и вести игру в общем чате без ветки.",
        "admin_game_forum_skip": "Без темы (общий чат)",
        "admin_game_forum_reload": "🔄 Обновить список тем",
        "admin_game_forum_thread_placeholder": "Ветка · id {id}",
        "admin_game_forum_reload_toast": "Список обновлён",
        "admin_game_forum_reload_lost": "⚠️ Сессия сброшена. Начните создание игры заново.",
        "admin_game_topic_forbidden": "Нельзя выбрать эту тему: её нет в списке разрешённых для этого чата.",
        "admin_game_pick_type": "🎯 <b>Тип игры</b>\n\nВыберите вид броска:",
        "admin_game_type_dice": "🎲 Кубики",
        "admin_game_type_bowling": "🎳 Боулинг",
        "admin_game_type_darts": "🎯 Дартс",
        "admin_game_type_any": "🎲 🎳 🎯 (любой бросок)",
        "admin_game_name_prefix": "Игра",
        "admin_game_enter_participants": "👥 <b>Кол-во участников</b>\n\nВведите минимум и максимум через «/» или «-».\nПример: <code>10/100</code>",
        "admin_game_invalid_participants": "❌ Формат: <code>min/max</code>, оба — положительные числа, min ≤ max.",
        "admin_game_enter_prizes": "🏆 <b>Призы</b>\n\nВведите суммы в PLN, каждая с новой строки. Сколько строк — столько призовых мест.\nПример:\n<code>20\n10\n5</code>\n\nПобедителям эти суммы будут начислены на баланс автоматически.",
        "admin_game_invalid_prizes": "❌ Призы должны быть положительными числами (например <code>20</code> или <code>10.5</code>), каждый с новой строки.",
        "admin_game_prizes_more_than_max": "❌ Призовых мест ({n}) больше, чем максимум участников ({max}). Уменьшите количество призов или измените участников.",
        "admin_game_enter_min_topup": "💰 <b>Условие записи: минимальная сумма пополнений</b>\n\nФорматы:\n• <code>0</code> — без условия\n• <code>100</code> — пополнил хотя бы на 100 PLN за всё время\n• <code>100 : 01.01.2026</code> — пополнил хотя бы на 100 PLN с указанной даты до старта игры",
        "admin_game_invalid_min_topup": "❌ Формат: число PLN (<code>100</code>) или число и дата через «:» (<code>100 : 01.01.2026</code>).",
        "admin_game_enter_entry_fee": "💵 <b>Стоимость взноса</b>\n\nВведите сумму в PLN (0 — бесплатно).",
        "admin_game_invalid_entry_fee": "❌ Введите число ≥ 0 (например <code>0</code> или <code>5</code>).",
        "admin_game_enter_datetime": "🗓 <b>Дата и время старта</b>\n\nФорматы:\n• <code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n• <code>ЧЧ:ММ</code> (сегодня)",
        "admin_game_invalid_datetime": "❌ Не удалось распознать дату/время. Пример: <code>25.12.2026 19:30</code>.",
        "admin_game_datetime_in_past": "❌ Время старта должно быть в будущем.",
        "admin_game_topup_since_after_start": "❌ Дата начала периода пополнений позже даты старта игры. Поменяйте условие или дату.",
        "admin_game_preview_title": "📋 <b>Превью игры</b>",
        "admin_game_preview_chat": "Чат: <b>{chat}</b>",
        "admin_game_preview_forum_topic": "Тема: <b>{topic}</b>",
        "admin_game_preview_type": "Тип: <b>{type}</b>",
        "admin_game_preview_participants": "Участники: <b>{min}–{max}</b>",
        "admin_game_preview_prizes": "Призы:",
        "admin_game_preview_min_topup_none": "Условие: <b>без условий</b>",
        "admin_game_preview_min_topup_alltime": "Условие: пополнения от <b>{n} PLN</b> (за всё время)",
        "admin_game_preview_min_topup_period": "Условие: пополнения от <b>{n} PLN</b> с <b>{since}</b>",
        "admin_game_preview_pay_free": "Тип: <b>бесплатная</b>",
        "admin_game_preview_pay_paid": "Тип: <b>платная</b>, взнос <b>{fee} PLN</b>",
        "admin_game_preview_datetime": "Старт: <b>{datetime}</b>",
        "admin_btn_confirm_create": "✅ Создать",
        "admin_btn_cancel_create": "❌ Отменить",
        "admin_game_created": "✅ Игра #{id} создана.",
        "admin_game_create_cancelled": "❌ Создание отменено.",
        # ---- Game lists ----
        "admin_games_active_title": "🟢 <b>Текущие игры</b>",
        "admin_games_past_title": "📚 <b>Прошедшие игры</b>",
        "admin_games_empty_active": "Сейчас активных игр нет.",
        "admin_games_empty_past": "Прошедших игр пока нет.",
        "admin_game_detail_title": "🎯 <b>Игра #{id}</b>",
        "admin_game_detail_status": "Статус: <b>{status}</b>",
        "admin_game_detail_participants_count": "Записалось: <b>{count}/{max}</b> (минимум {min})",
        "admin_game_status_draft": "ожидает старта",
        "admin_game_status_active": "идёт сейчас",
        "admin_game_status_finished": "завершена",
        "admin_game_status_cancelled": "отменена",
        # ---- Announcement (in chat + DM) ----
        "game_announce_title": "🎯 Игра для <b>{chat}</b> создана",
        "game_announce_date": "Дата: <b>{date}</b>",
        "game_announce_participants_range": "Участников: <b>{min}–{max}</b>",
        "game_announce_conditions": "<b>Условия участия:</b>",
        "game_announce_cond_min_topup_alltime": "• минимум пополнений: <b>{n} PLN</b> (за всё время)",
        "game_announce_cond_min_topup_period": "• минимум пополнений: <b>{n} PLN</b> (с {since} до старта игры)",
        "game_announce_cond_pay_free": "• бесплатно",
        "game_announce_cond_pay_paid": "• платная, взнос <b>{fee} PLN</b>",
        "game_announce_cond_none": "• без дополнительных условий",
        "game_announce_prizes": "<b>Призы:</b>",
        "game_announce_signup_link": "Запись на игру через бота {bot_link}",
        "game_announce_signup_no_link": "Запись на игру — напишите боту в личные сообщения.",
        "game_btn_signup": "🎮 Записаться на игру",
        "game_reminder_5min": "⏳ До игры в чате «{chat_title}» осталось около 5 минут.",
        "game_cancelled_not_enough_players_dm": "Игра отменена: набралось только {current} из {required} участников.",
        "game_cancelled_refund_full_fee": "Взнос {fee} PLN возвращён на ваш баланс.",
        "game_start_header": "<b>Условия игры:</b>\n{conditions}\n\n<b>Призы:</b>\n{prizes}",
        "game_start_cond_min_topup_period": "• минимум пополнений: {n} PLN (с {since} до {until})",
        "game_start_cond_min_topup_alltime": "• минимум пополнений: {n} PLN (за всё время)",
        "game_start_cond_paid": "• платная игра, взнос {fee} PLN",
        "game_start_cond_free": "• бесплатная игра",
        "game_start_cond_none": "• без дополнительных условий",
        "game_rules_block": (
            "Правила:\n"
            "1) Раунды по очереди, по 3 броска на игрока.\n"
            "2) Можно бросать 🎲 🎳 🎯 (или тем же текстом).\n"
            "3) После раунда — проходной балл по среднему среди сделавших броски.\n"
            "4) Пропустившие ход получают догоняющую попытку.\n"
            "5) Финал и тай-брейк — по правилам бота."
        ),
        "game_round1_list_intro": "Первый раунд!",
        "round_list_participants": "Список участников",
        "round_score_pending": "…",
        "round_score_eliminated": "выл",
        "round_your_result": "Ваш бросок: {value}",
        "round_throw_2_more": "Сделайте ещё 2 броска {emoji}",
        "round_throw_1_more": "Сделайте ещё 1 бросок {emoji}",
        "round_third_throw_done": "{result_line}\n{name}, итог в этом раунде: <b>{total}</b>",
        "round_throw_prompt": "{name}, сделайте 3 броска любым эмодзи: {emoji}",
        "round_turn_60sec_left": "{name}, осталась 1 минута на ход.",
        "round_participant_skipped": "{name} — ход пропущен.",
        "round_participants_missed": "Участники без очков в этом раунде:",
        "round_catchup_5min": "У вас есть время на 3 броска (ускоренный режим).",
        "round_1_finished": "Первый раунд завершён.",
        "round_N_finished": "Раунд {round} завершён.",
        "round_passing_score": "Проходной балл: {score}",
        "round_list_passed": "В следующий раунд проходят:",
        "round_list_passed_final": "В финальный раунд проходят:",
        "round_results_header": "Результаты:",
        "round_tiebreak": "Тай-брейк!",
        "round_tiebreak_for": "Для определения: {places}",
        "round_tiebreak_place_one": "{n}-е место",
        "round_tiebreak_place_span": "мест с {a} по {b}",
        "round_tiebreak_throw": "{name}, сделайте 1 бросок {emoji}",
        "round_tiebreak_result": "{name} — бросок тай-брейка: {value}",
        "round_final_finished": "Финальный раунд завершён.",
        "round_winners": "Победители:",
        "game_sponsor_line": "Спонсор: {bot_link}",
        "game_dm_prize_won": "🎉 Вы заняли {place} место! На баланс зачислено <b>{amount} PLN</b>.",
        "game_signup_no_games": "Сейчас нет игр с открытой записью.",
        "game_signup_list_title": "Открытая запись на игры (нажмите игру):",
        "game_signup_list_item": "#{id} {when} — {chat}",
        "game_signup_btn_join": "✅ Записаться",
        "game_signup_btn_leave": "🚫 Выйти",
        "game_signup_not_found": "Игра не найдена.",
        "game_signup_not_draft": "Запись недоступна (игра уже не в статусе ожидания).",
        "game_signup_started": "Игра уже стартовала или запись закрыта.",
        "game_signup_full": "Мест больше нет.",
        "game_signup_min_topup": "Недостаточно пополнений: нужно {need} PLN, у вас {have} PLN (по правилам игры).",
        "game_signup_low_balance": "Недостаточно средств: взнос {fee} PLN, баланс {balance} PLN.",
        "game_signup_already_in": "Вы уже в списке участников.",
        "game_signup_ok": "Вы записаны.",
        "game_signup_left": "Вы вышли из списка участников.",
        "game_signup_not_in": "Вы не были записаны.",
        "game_signup_card": (
            "🎯 <b>Игра #{id}</b>\n"
            "Чат: {chat}\n"
            "Старт: <b>{start}</b>\n"
            "Игроки: <b>{count}</b> / {max_p} (мин. {min_p})\n\n"
            "<b>Условия:</b>\n{conditions}\n\n"
            "<b>Призы (PLN):</b>\n{prizes}"
        ),
        "game_signup_cond_topup_period": "• пополнения от {n} PLN с {since}",
        "game_signup_cond_topup_alltime": "• пополнения от {n} PLN за всё время",
        "game_signup_cond_paid": "• взнос {fee} PLN",
        "game_signup_cond_free": "• бесплатно",
        "game_signup_cond_none": "—",
        "admin_pay_btn_activate": "▶️ Запустить",
        "admin_pay_btn_deactivate": "⏹ Остановить",
        "admin_pay_btn_edit_proxy": "🌐 Изменить прокси",
        "admin_pay_btn_edit_blik": "📱 Изменить BLIK",
        "admin_pay_btn_edit_limit": "📊 Изменить лимит",
        "admin_pay_btn_rescan": "🔁 Перечитать последние письма",
        "admin_pay_btn_delete": "🗑 Удалить",
        "admin_pay_btn_delete_confirm": "✅ Подтвердить удаление",
        "admin_pay_btn_cancel": "❌ Отмена",
        "admin_pay_btn_bank_custom": "✏️ Другой",
        "admin_btn_chats": "💬 Настройка чатов",
        "admin_btn_forbidden_words": "🚫 Запрещённые слова",
        "admin_btn_admins": "👥 Настройка админов",
    },
    "en": {
        "choose_language": "Choose language / Выберите язык:",
        "welcome_menu": "Welcome to the game bot",
        "welcome_user_id": "Your ID: {user_id}",
        "welcome_balance": "Your balance: {balance} PLN",
        "btn_cabinet": "Personal account",
        "btn_topup": "💳 Top up balance",
        "topup_enter_amount": "💳 <b>Top up balance</b>\n\nEnter the top-up amount in PLN (from {min} to {max} PLN):",
        "topup_invalid_amount": "❌ Invalid amount. Enter a number (e.g. 50).",
        "topup_out_of_range": "❌ Amount must be between {min} and {max} PLN.",
        "topup_no_accounts": "⚠️ Top-ups are temporarily unavailable — no active payment accounts. Please try later.",
        "topup_order_created": (
            "💳 <b>Top-up order created</b>\n\n"
            "Amount: <b>{amount} PLN</b>\n"
            "Order ID: <code>{order_id}</code>\n\n"
            "📱 Make a BLIK transfer to:\n<code>{blik}</code>\n\n"
            "⚠️ <b>Include this code in the payment title:</b>\n<code>{order_id}</code>\n\n"
            "Your balance will be credited automatically after the payment arrives."
        ),
        "topup_btn_cancel_order": "❌ Cancel order",
        "topup_order_cancelled": "❌ Order <code>{order_id}</code> cancelled.",
        "topup_order_not_found": "❌ Order not found or already closed.",
        "btn_withdraw": "💸 Request withdrawal",
        "btn_cancel_withdraw": "❌ Cancel withdrawal",
        "withdraw_enter_amount": (
            "💸 <b>Withdrawal</b>\n\n"
            "Enter the amount in PLN (minimum {min} PLN).\n"
            "Fee: <b>{fee}%</b>\n"
            "⏱ Withdrawals are processed within 24 hours."
        ),
        "withdraw_invalid_amount": "❌ Invalid amount. Enter a number (e.g. 150).",
        "withdraw_below_min": "❌ Withdrawal is available from {min} PLN.",
        "withdraw_not_enough": "❌ Not enough funds. Your balance: {balance} PLN.",
        "withdraw_enter_blik": "📱 Enter your BLIK number (at least 9 digits):",
        "withdraw_invalid_blik": "❌ Invalid BLIK format. At least 9 digits.",
        "withdraw_confirm": (
            "💸 <b>Confirm withdrawal</b>\n\n"
            "Debited from balance: <b>{amount} PLN</b>\n"
            "Fee: <b>{fee}%</b> ({fee_amount} PLN)\n"
            "Payout: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "Confirm withdrawal?"
        ),
        "withdraw_btn_yes": "✅ Yes",
        "withdraw_btn_no": "❌ No",
        "withdraw_created": (
            "✅ <b>Withdrawal request created</b>\n\n"
            "ID: <code>#{id}</code>\n"
            "Payout: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "⏱ It will be processed within 24 hours."
        ),
        "withdraw_cancel_ask": "❓ Are you sure you want to cancel withdrawal <code>#{id}</code>?",
        "withdraw_cancelled": "✅ Withdrawal <code>#{id}</code> cancelled. Funds returned to your balance.",
        "withdraw_not_pending": "❌ Request not found or already processed.",
        "withdraw_already_pending": "⚠️ You already have an active withdrawal. Cancel it before creating a new one.",
        "withdraw_admin_message": (
            "🏦 <b>New withdrawal request</b>\n\n"
            "👤 {mention}{username}\n"
            "🆔 <code>{user_id}</code>\n"
            "💸 Requested: <b>{amount} PLN</b>\n"
            "🧾 Fee: {fee}% ({fee_amount} PLN)\n"
            "💵 Payout: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>"
        ),
        "withdraw_admin_btn_approve": "✅ Approve",
        "withdraw_admin_approved": "✅ <b>PAID</b>",
        "withdraw_admin_cancelled": "❌ <b>CANCELLED</b>",
        "withdraw_approved_user": (
            "✅ Your withdrawal <code>#{id}</code> for <b>{payout} PLN</b> has been sent."
        ),
        "cabinet_title": "💼 Personal account",
        "cabinet_balance": "💰 Balance: <b>{balance} PLN</b>",
        "btn_signup": "Sign up for a game",
        "main_menu_chat_fallback": "💬 Chat",
        "btn_play_21_bot": "Play 21",
        "btn_casino": "🎰 Casino 🎰",
        "btn_admin": "Admin",
        "btn_lang": "🌐",
        "btn_main": "🏠 Main",
        "btn_back": "← Back",
        "admin_title": "Admin panel",
        "admin_no_access": "⛔ Access denied",
        "admin_btn_games": "🎯 Games",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Casino",
        "admin_btn_checkers": "🔴 Checkers",
        "admin_btn_kmb": "🪖 KMB",
        "admin_btn_stats": "📊 Statistics",
        "admin_btn_bot_settings": "⚙️ Bot settings",
        "admin_games_title": "🎯 <b>Games</b>",
        "admin_btn_create_game": "➕ Create game",
        "admin_btn_active_games": "🟢 Active games",
        "admin_btn_past_games": "📚 Past games",
        "admin_wip": "🚧 Work in progress",
        "admin_settings_title": "⚙️ Bot settings",
        "admin_btn_payments": "💳 Payments settings",
        "admin_btn_fees": "💸 Fees settings",
        "admin_btn_withdraw_fee": "💸 Withdrawal fee",
        "admin_fees_title": "💸 <b>Fees settings</b>",
        "admin_pay_title": "<b>MBanks</b> — accounts:",
        "admin_pay_empty": "<b>MBanks</b>\nNo accounts yet.",
        "admin_pay_btn_add": "➕ Add account",
        "admin_pay_btn_withdraw_fee": "💸 Withdrawal fee",
        "admin_withdraw_fee_title": "💸 <b>Withdrawal fee</b>\n\nCurrent: <b>{percent}%</b>\n\nEnter a new percent (e.g. <code>5</code> or <code>2.5</code>):",
        "admin_withdraw_fee_invalid": "❌ Invalid format. Enter a number between 0 and 100 (e.g. <code>5</code> or <code>2.5</code>).",
        "admin_withdraw_fee_updated": "✅ Withdrawal fee updated: <b>{percent}%</b>",
        "admin_btn_game21_fees": "♠️ 21 — fees",
        "admin_fees_21_title": "♠️ <b>Game 21 fees</b>\n\nVs bot: <b>{bot}%</b>\nPvP: <b>{users}%</b>",
        "admin_game21_fee_btn_bot": "Vs bot",
        "admin_game21_fee_btn_users": "Between users",
        "admin_game21_fee_bot_title": "💸 21 fee (vs bot)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_users_title": "💸 21 fee (PvP)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_updated": "✅ 21 fee updated: <b>{percent}%</b>",
        "admin_21_title": "♠️ <b>Game 21</b>\n\nVs bot: {bot}\n\nFees: bot {bot_fee}% · PvP {users_fee}%\n\nTurn PvP on per connected chat. If the bot already knows forum topics in that chat, enabling PvP opens the topic allowlist screen.",
        "admin_21_on": "🟢 on",
        "admin_21_off": "⚪ off",
        "admin_21_btn_bot_on": "Vs bot: turn off",
        "admin_21_btn_bot_off": "Vs bot: turn on",
        "admin_21_btn_users_on": "PvP global: turn off",
        "admin_21_btn_users_off": "PvP global: turn on",
        "admin_21_chat_pvp_on": "PvP in «{title}»: off",
        "admin_21_chat_pvp_off": "PvP in «{title}»: on",
        "game21_active_notice": "You already have an active 21 game.",
        "game21_bot_midgame_menu_blocked": (
            "You are currently in an active game. First finish the current game."
        ),
        "game21_busy_screen_text": "You already have an active game in {chat}.",
        "game21_busy_screen_text_bot": (
            "You already have an active game vs the bot. Finish the round in this chat."
        ),
        "game21_btn_abort_session": "Cancel game",
        "game21_active_cancelled_toast": "Your 21 session was cancelled.",
        "game21_no_active_search_to_cancel": (
            "There is no active opponent search (it was already cancelled or the match has started)."
        ),
        "game21_pvp_choose_topic": "Choose a game room (🟢 free, 🔴 busy):",
        "game21_pvp_topic_free": "🟢",
        "game21_pvp_topic_busy": "🔴",
        "game21_pvp_topic_general": "General",
        "game21_pvp_search_post_failed": "Could not post search. Bet refunded.",
        "game21_pvp_decide_prompt_other": "{name}, roll the dice 🎲 once.",
        "game21_menu_title": "Game 21",
        "game21_btn_rules": "Rules",
        "game21_btn_vs_bot": "Play vs bot",
        "game21_btn_vs_user_chat": "Play vs user in chat",
        "game21_coming_soon_all_off": "Game 21 is unavailable.",
        "game21_coming_soon_play": "Vs bot is unavailable.",
        "game21_enter_bet": "Enter bet (PLN):",
        "game21_bet_invalid": "Invalid amount.",
        "game21_not_enough_balance": "Insufficient balance.",
        "game21_confirm_bet_with_win": "Bet: {amount} PLN\nPossible win: {win} PLN\n\nConfirm?",
        "game21_btn_yes": "Yes",
        "game21_btn_no": "No",
        "game21_cancelled": "Cancelled.",
        "game21_rules_title": "<b>Rules 21</b>",
        "game21_rules": "See sections below.",
        "game21_rules_bot": "<b>Vs bot</b>\nRoll 🎲 in DM. Min 16, then Stop. Bot rolls after you.",
        "game21_rules_users": "<b>PvP in {chat_title}</b>\nFind opponent, roll for order, play to 21.",
        "game21_throw_now": "Roll the dice 🎲",
        "game21_player_result": "Your total: {total}",
        "game21_player_busted": "Your total: {total}\nBust!",
        "game21_player_blackjack": "You have 21!",
        "game21_player_can_stop": "Your total: {total}\nRoll or press Stop.",
        "game21_btn_stop": "Stop",
        "game21_bot_turn_start": "Bot's turn.",
        "game21_bot_result": "Bot total: {total}",
        "game21_result_win": "You won!",
        "game21_result_lose": "You lost.",
        "game21_result_draw": "Draw.",
        "game21_end_bot_win": (
            "<b>You won!</b>\n"
            "Credited to balance: <b>{payout} PLN</b>.\n"
            "Score: you {player_total} — bot {bot_total}."
        ),
        "game21_end_bot_lose": "You lost {bet} PLN\nScore: you {player_total} — bot {bot_total}.",
        "game21_end_bot_lose_bust": "You lost {bet} PLN\nBust at {player_total}.",
        "game21_end_bot_draw": (
            "<b>Draw.</b>\n"
            "Stake <b>{bet} PLN</b> refunded to your balance.\n"
            "Score: {player_total} — {bot_total}."
        ),
        "game21_pvp_enter_bet": "Enter bet (PLN):\n\nPlaying 21 in {room}",
        "game21_pvp_confirm": "Start opponent search?\nBet: {amount} PLN\nPossible win: {win} PLN",
        "game21_pvp_search_started": (
            "Opponent search started.\n\n"
            "{amount} PLN has been deducted from your balance."
        ),
        "game21_pvp_choose_chat": "Choose a chat:",
        "game21_pvp_no_available_chat": "No chats available for PvP.",
        "game21_pvp_must_join_chat": "You must be in the chat: {chat_title}",
        "game21_pvp_not_member_title": "You're not in the game chat",
        "game21_pvp_not_member_intro": "To play 21 vs another user, join the chat using the link below, then tap «Play vs user in chat» again.",
        "game21_pvp_main_active_exists": "You can't create a game request there — a game is in progress.",
        "game21_pvp_active_exists": "This slot already has a game or search.",
        "game21_pvp_self_accept_forbidden": "You cannot accept your own request.",
        "game21_pvp_search_post": "{user} looks for a 21 opponent\n\nBet: {amount} PLN\nWin up to: {win} PLN\n\nBalance in bot {bot_link}",
        "game21_pvp_btn_accept": "Accept",
        "game21_pvp_match_title": "Game 21",
        "game21_pvp_match_started_in_topic": "Game 21 started in {room}",
        "game21_pvp_match_prize": "<b>Payout: {win} PLN</b>",
        "game21_pvp_match_rules_heading": "Rules:",
        "game21_pvp_rules_body": (
            "Each rolls 🎲 once — lower roll goes first. "
            "Then take turns; get as close to 21 as you can without going over. "
            "When allowed, you can tap Stop. "
            "After both finish or bust, totals are compared; a draw is possible."
        ),
        "game21_pvp_started": "Game 21\n{p1}\n{p2}\n\nBet: {amount} PLN · win up to {win} PLN\n{bot_link}",
        "game21_pvp_general_started_notice": "A game of 21 between {p1} and {p2} has started in <b>{room}</b>.",
        "game21_pvp_topic_started_notice": "A game of 21 between {p1} and {p2} has started.\n\nPrize: {prize} PLN.",
        "game21_pvp_decide_first": "{players} — roll 🎲 once each (lower starts).",
        "game21_pvp_decide_roll_result": "{name} rolled {value}",
        "game21_pvp_decide_tie": "Tie on rolls. Roll again.",
        "game21_pvp_turn_prompt": "{name}, your turn. Roll 🎲",
        "game21_pvp_player_result": "{name}: {total}",
        "game21_pvp_player_busted": "{name}: {total} — bust!",
        "game21_pvp_player_blackjack": "{name} — 21!",
        "game21_pvp_player_can_stop": "{name}: {total}. Stop or roll again.",
        "game21_pvp_stop_announce": "{name} stopped at {total}",
        "game21_pvp_not_your_turn_stop": "It is {name}'s turn now.",
        "game21_pvp_stop_only_on_equal": "Stop is only when totals are equal.",
        "game21_pvp_winner": "Winner: {name}\nPayout {payout} PLN · {bot_link}",
        "game21_pvp_draw": "Draw. Refund {amount} PLN · {bot_link}",
        "game21_pvp_pm_bet_deducted": "Bet deducted: {amount} PLN.",
        "game21_pvp_search_not_accepted": "No one accepted. Refund {amount} PLN.",
        "game21_pvp_topic_forbidden": "This topic is not available for play.",
        "game21_pvp_topics_restricted_empty": "There are no topics allowed by the admin for games in this chat.",
        # ---- Chats settings ----
        "admin_chats_title": "💬 <b>Connected chats</b>",
        "admin_chats_empty": "No chats yet.",
        "admin_chats_list_line": "• <code>{chat_id}</code> · {title}",
        "admin_chats_btn_add": "➕ Add chat",
        "admin_chats_btn_delete": "🗑 Delete chat",
        "admin_chats_btn_game_topics": "📋 Game topics",
        "admin_chats_topics_choose_chat": "Pick a chat to configure which forum topics allow games (21 PvP and dice games):",
        "admin_chats_topics_not_forum": "This chat is not a forum supergroup with topics — nothing to configure.",
        "admin_chats_topics_chat_unavailable": "Could not open the chat.",
        "admin_chats_topics_body_open": (
            "📋 <b>Game topics</b>: {title}\n\n"
            "No restrictions now — 21 PvP and game creation are allowed in all known topics and the main chat.\n\n"
            "Tap «Enable topic limits» to choose where play is allowed (the list will be filled with current topics; uncheck what you do not need)."
        ),
        "admin_chats_topics_body_restricted": (
            "📋 <b>Game topics</b>: {title}\n\n"
            "An allowlist is on. Games are only where ✅ is set.\n\n"
            "«Remove limits» allows all topics again."
        ),
        "admin_chats_topics_btn_enable": "Enable topic limits",
        "admin_chats_topics_btn_disable": "Remove limits (all topics)",
        "admin_chats_enter_button_title": (
            "Send the <b>button label</b> — users will see it when picking a chat for a game. "
            "The same text will be stored for <b>ru / en / uk / pl</b> for now; you can set per-language "
            "labels later.\n\n"
            "Up to 200 characters."
        ),
        "admin_chats_invalid_button_title": "❌ Send a non-empty label (max 200 characters).",
        "admin_chats_enter_chat_id": (
            "Send the <b>chat ID</b> (e.g. <code>-1001234567890</code>).\n\n"
            "To find the ID: add the bot to the group and forward any message from there to "
            "<a href=\"https://t.me/userinfobot\">@userinfobot</a>, or use a bot like getidsbot."
        ),
        "admin_chats_invalid_id": "❌ Invalid format. Send an integer starting with <code>-100</code>.",
        "admin_chats_already_added": "⚠️ This chat is already connected.",
        "admin_chats_added": "✅ Chat <code>{chat_id}</code> connected.",
        "admin_chats_invite_ok": "✅ Invite link was created automatically.",
        "admin_chats_invite_link_failed": (
            "⚠️ Could not create an invite link: make sure the bot is an <b>admin</b> in the chat "
            "with permission to invite users (or that the group allows invite links)."
        ),
        "admin_chats_session_lost": "⚠️ Add-chat session was reset. Tap «Add chat» again.",
        "admin_chats_delete_choose": "Choose a chat to delete:",
        "admin_chats_delete_confirm": "Delete chat <code>{chat_id}</code>?",
        "admin_chats_deleted": "✅ Chat deleted.",
        "admin_chats_delete_none": "There are no connected chats to delete.",
        # ---- Games create FSM ----
        "admin_game_no_chats": "⚠️ Connect at least one chat first: Bot settings → Chats.",
        "admin_game_pick_chat": "Which chat to announce the game in?",
        "admin_game_pick_forum_topic": "📂 <b>Forum topic</b>\n\nPick the topic where the game will run (announcement, rounds, throws).\n\nIf a button shows «Topic · id …», the bot only knows Telegram’s internal thread id (plain messages don’t include the visible title). Rename the topic once in the group — the bot will pick up the new name.",
        "admin_game_pick_forum_topic_empty": "📂 <b>Forum topic</b>\n\nThe list is empty: Telegram does not expose forum topics via the Bot API; the bot learns threads from messages and service events.\n\nIf topics already exist: send any message in each topic you need (or rename a topic once), then tap «🔄 …».\n\nYou can skip and run the game in the main chat without a topic.",
        "admin_game_forum_skip": "No topic (main chat)",
        "admin_game_forum_reload": "🔄 Refresh topic list",
        "admin_game_forum_thread_placeholder": "Topic · id {id}",
        "admin_game_forum_reload_toast": "List updated",
        "admin_game_forum_reload_lost": "⚠️ Session lost. Start creating the game again.",
        "admin_game_topic_forbidden": "This topic is not on the allowlist for this chat.",
        "admin_game_pick_type": "🎯 <b>Game type</b>\n\nPick the throw kind:",
        "admin_game_type_dice": "🎲 Dice",
        "admin_game_type_bowling": "🎳 Bowling",
        "admin_game_type_darts": "🎯 Darts",
        "admin_game_type_any": "🎲 🎳 🎯 (any throw)",
        "admin_game_name_prefix": "Game",
        "admin_game_enter_participants": "👥 <b>Participants</b>\n\nSend min and max separated by «/» or «-».\nExample: <code>10/100</code>",
        "admin_game_invalid_participants": "❌ Format: <code>min/max</code>, both positive integers, min ≤ max.",
        "admin_game_enter_prizes": "🏆 <b>Prizes</b>\n\nSend prize amounts in PLN, one per line. Number of lines = number of prize places.\nExample:\n<code>20\n10\n5</code>\n\nWinners will be credited automatically.",
        "admin_game_invalid_prizes": "❌ Prizes must be positive numbers (e.g. <code>20</code> or <code>10.5</code>), one per line.",
        "admin_game_prizes_more_than_max": "❌ Prize places ({n}) exceed max participants ({max}).",
        "admin_game_enter_min_topup": "💰 <b>Signup requirement: minimum top-ups</b>\n\nFormats:\n• <code>0</code> — no requirement\n• <code>100</code> — topped up at least 100 PLN all time\n• <code>100 : 01.01.2026</code> — topped up at least 100 PLN since that date",
        "admin_game_invalid_min_topup": "❌ Format: a number (<code>100</code>) or number + date with «:» (<code>100 : 01.01.2026</code>).",
        "admin_game_enter_entry_fee": "💵 <b>Entry fee</b>\n\nSend amount in PLN (0 = free).",
        "admin_game_invalid_entry_fee": "❌ Send a number ≥ 0 (e.g. <code>0</code> or <code>5</code>).",
        "admin_game_enter_datetime": "🗓 <b>Start date & time</b>\n\nFormats:\n• <code>DD.MM.YYYY HH:MM</code>\n• <code>HH:MM</code> (today)",
        "admin_game_invalid_datetime": "❌ Could not parse date/time. Example: <code>25.12.2026 19:30</code>.",
        "admin_game_datetime_in_past": "❌ Start time must be in the future.",
        "admin_game_topup_since_after_start": "❌ Top-up period start is after the game start. Adjust condition or date.",
        "admin_game_preview_title": "📋 <b>Game preview</b>",
        "admin_game_preview_chat": "Chat: <b>{chat}</b>",
        "admin_game_preview_forum_topic": "Topic: <b>{topic}</b>",
        "admin_game_preview_type": "Type: <b>{type}</b>",
        "admin_game_preview_participants": "Participants: <b>{min}–{max}</b>",
        "admin_game_preview_prizes": "Prizes:",
        "admin_game_preview_min_topup_none": "Requirement: <b>none</b>",
        "admin_game_preview_min_topup_alltime": "Requirement: top-ups from <b>{n} PLN</b> (all time)",
        "admin_game_preview_min_topup_period": "Requirement: top-ups from <b>{n} PLN</b> since <b>{since}</b>",
        "admin_game_preview_pay_free": "Type: <b>free</b>",
        "admin_game_preview_pay_paid": "Type: <b>paid</b>, fee <b>{fee} PLN</b>",
        "admin_game_preview_datetime": "Start: <b>{datetime}</b>",
        "admin_btn_confirm_create": "✅ Create",
        "admin_btn_cancel_create": "❌ Cancel",
        "admin_game_created": "✅ Game #{id} created.",
        "admin_game_create_cancelled": "❌ Cancelled.",
        # ---- Game lists ----
        "admin_games_active_title": "🟢 <b>Active games</b>",
        "admin_games_past_title": "📚 <b>Past games</b>",
        "admin_games_empty_active": "No active games right now.",
        "admin_games_empty_past": "No past games yet.",
        "admin_game_detail_title": "🎯 <b>Game #{id}</b>",
        "admin_game_detail_status": "Status: <b>{status}</b>",
        "admin_game_detail_participants_count": "Registered: <b>{count}/{max}</b> (min {min})",
        "admin_game_status_draft": "awaiting start",
        "admin_game_status_active": "in progress",
        "admin_game_status_finished": "finished",
        "admin_game_status_cancelled": "cancelled",
        # ---- Announcement ----
        "game_announce_title": "🎯 Game for <b>{chat}</b> is set",
        "game_announce_date": "Date: <b>{date}</b>",
        "game_announce_participants_range": "Participants: <b>{min}–{max}</b>",
        "game_announce_conditions": "<b>Conditions:</b>",
        "game_announce_cond_min_topup_alltime": "• min top-ups: <b>{n} PLN</b> (all time)",
        "game_announce_cond_min_topup_period": "• min top-ups: <b>{n} PLN</b> (since {since} until start)",
        "game_announce_cond_pay_free": "• free",
        "game_announce_cond_pay_paid": "• paid, entry fee <b>{fee} PLN</b>",
        "game_announce_cond_none": "• no extra conditions",
        "game_announce_prizes": "<b>Prizes:</b>",
        "game_announce_signup_link": "Sign up via {bot_link}",
        "game_announce_signup_no_link": "Sign up — message the bot in DM.",
        "game_btn_signup": "🎮 Sign up",
        "game_reminder_5min": "⏳ About 5 minutes until the game in «{chat_title}».",
        "game_cancelled_not_enough_players_dm": "Game cancelled: only {current} of {required} players signed up.",
        "game_cancelled_refund_full_fee": "Entry fee {fee} PLN was refunded to your balance.",
        "game_start_header": "<b>Conditions:</b>\n{conditions}\n\n<b>Prizes:</b>\n{prizes}",
        "game_start_cond_min_topup_period": "• min top-ups: {n} PLN (from {since} until {until})",
        "game_start_cond_min_topup_alltime": "• min top-ups: {n} PLN (all time)",
        "game_start_cond_paid": "• paid game, entry fee {fee} PLN",
        "game_start_cond_free": "• free game",
        "game_start_cond_none": "• no extra conditions",
        "game_rules_block": (
            "Rules:\n"
            "1) Rounds in turn order, 3 throws each.\n"
            "2) You may throw 🎲 🎳 🎯 (dice message or the same emojis as text).\n"
            "3) After a round, passing score is the integer average among players who threw.\n"
            "4) Missed turns get a catch-up pass.\n"
            "5) Final round and tie-break follow bot logic."
        ),
        "game_round1_list_intro": "Round 1!",
        "round_list_participants": "Players",
        "round_score_pending": "…",
        "round_score_eliminated": "out",
        "round_your_result": "Your throw: {value}",
        "round_throw_2_more": "Throw 2 more times {emoji}",
        "round_throw_1_more": "Throw 1 more time {emoji}",
        "round_third_throw_done": "{result_line}\n{name}, your round total: <b>{total}</b>",
        "round_throw_prompt": "{name}, make 3 throws with any emoji: {emoji}",
        "round_turn_60sec_left": "{name}, 1 minute left for your throw.",
        "round_participant_skipped": "{name} — turn skipped.",
        "round_participants_missed": "Players with 0 in this round:",
        "round_catchup_5min": "You have time for 3 throws (faster mode).",
        "round_1_finished": "Round 1 finished.",
        "round_N_finished": "Round {round} finished.",
        "round_passing_score": "Passing score: {score}",
        "round_list_passed": "Advancing to the next round:",
        "round_list_passed_final": "Advancing to the final round:",
        "round_results_header": "Results:",
        "round_tiebreak": "Tie-break!",
        "round_tiebreak_for": "To decide: {places}",
        "round_tiebreak_place_one": "{n} place",
        "round_tiebreak_place_span": "places {a}–{b}",
        "round_tiebreak_throw": "{name}, make 1 throw {emoji}",
        "round_tiebreak_result": "{name} — tie-break throw: {value}",
        "round_final_finished": "Final round finished.",
        "round_winners": "Winners:",
        "game_sponsor_line": "Sponsor: {bot_link}",
        "game_dm_prize_won": "🎉 You placed {place}! <b>{amount} PLN</b> credited to your balance.",
        "game_signup_no_games": "No games open for signup right now.",
        "game_signup_list_title": "Open signups (tap a game):",
        "game_signup_list_item": "#{id} {when} — {chat}",
        "game_signup_btn_join": "✅ Join",
        "game_signup_btn_leave": "🚫 Leave",
        "game_signup_not_found": "Game not found.",
        "game_signup_not_draft": "Signup is closed (game is not in draft).",
        "game_signup_started": "The game already started or signup closed.",
        "game_signup_full": "No free slots.",
        "game_signup_min_topup": "Not enough top-ups: need {need} PLN, you have {have} PLN (per game rules).",
        "game_signup_low_balance": "Not enough balance: fee {fee} PLN, your balance {balance} PLN.",
        "game_signup_already_in": "You are already registered.",
        "game_signup_ok": "You are registered.",
        "game_signup_left": "You left the game.",
        "game_signup_not_in": "You were not registered.",
        "game_signup_card": (
            "🎯 <b>Game #{id}</b>\n"
            "Chat: {chat}\n"
            "Start: <b>{start}</b>\n"
            "Players: <b>{count}</b> / {max_p} (min {min_p})\n\n"
            "<b>Conditions:</b>\n{conditions}\n\n"
            "<b>Prizes (PLN):</b>\n{prizes}"
        ),
        "game_signup_cond_topup_period": "• top-ups from {n} PLN since {since}",
        "game_signup_cond_topup_alltime": "• top-ups from {n} PLN (all time)",
        "game_signup_cond_paid": "• entry fee {fee} PLN",
        "game_signup_cond_free": "• free",
        "game_signup_cond_none": "—",
        "admin_pay_btn_activate": "▶️ Start",
        "admin_pay_btn_deactivate": "⏹ Stop",
        "admin_pay_btn_edit_proxy": "🌐 Edit proxy",
        "admin_pay_btn_edit_blik": "📱 Edit BLIK",
        "admin_pay_btn_edit_limit": "📊 Edit limit",
        "admin_pay_btn_rescan": "🔁 Re-scan recent emails",
        "admin_pay_btn_delete": "🗑 Delete",
        "admin_pay_btn_delete_confirm": "✅ Confirm delete",
        "admin_pay_btn_cancel": "❌ Cancel",
        "admin_pay_btn_bank_custom": "✏️ Other",
        "admin_btn_chats": "💬 Chats settings",
        "admin_btn_forbidden_words": "🚫 Forbidden words",
        "admin_btn_admins": "👥 Admins settings",
    },
    "uk": {
        "choose_language": "Оберіть мову / Choose language:",
        "welcome_menu": "Ласкаво просимо в бота для ігор",
        "welcome_user_id": "Ваш ID: {user_id}",
        "welcome_balance": "Ваш баланс: {balance} PLN",
        "btn_cabinet": "Особистий кабінет",
        "btn_topup": "💳 Поповнити баланс",
        "topup_enter_amount": "💳 <b>Поповнення балансу</b>\n\nВведіть суму поповнення в PLN (від {min} до {max} PLN):",
        "topup_invalid_amount": "❌ Невірна сума. Введіть число (наприклад 50).",
        "topup_out_of_range": "❌ Сума повинна бути від {min} до {max} PLN.",
        "topup_no_accounts": "⚠️ Поповнення тимчасово недоступне — немає активних платіжних акаунтів. Спробуйте пізніше.",
        "topup_order_created": (
            "💳 <b>Заявку на поповнення створено</b>\n\n"
            "Сума: <b>{amount} PLN</b>\n"
            "Номер заявки: <code>{order_id}</code>\n\n"
            "📱 Зробіть BLIK-переказ на номер:\n<code>{blik}</code>\n\n"
            "⚠️ <b>У призначенні платежу обов'язково вкажіть код:</b>\n<code>{order_id}</code>\n\n"
            "Після отримання платежу баланс зарахується автоматично."
        ),
        "topup_btn_cancel_order": "❌ Скасувати заявку",
        "topup_order_cancelled": "❌ Заявку <code>{order_id}</code> скасовано.",
        "topup_order_not_found": "❌ Заявку не знайдено або вже закрито.",
        "btn_withdraw": "💸 Запросити виведення",
        "btn_cancel_withdraw": "❌ Скасувати виведення",
        "withdraw_enter_amount": (
            "💸 <b>Виведення коштів</b>\n\n"
            "Введіть суму у PLN (мінімум {min} PLN).\n"
            "Комісія: <b>{fee}%</b>\n"
            "⏱ Виведення протягом 24 годин."
        ),
        "withdraw_invalid_amount": "❌ Невірна сума. Введіть число (наприклад 150).",
        "withdraw_below_min": "❌ Виведення доступне від {min} PLN.",
        "withdraw_not_enough": "❌ Недостатньо коштів. Ваш баланс: {balance} PLN.",
        "withdraw_enter_blik": "📱 Введіть номер BLIK (мінімум 9 цифр):",
        "withdraw_invalid_blik": "❌ Невірний формат BLIK. Мінімум 9 цифр.",
        "withdraw_confirm": (
            "💸 <b>Підтвердження виведення</b>\n\n"
            "З балансу: <b>{amount} PLN</b>\n"
            "Комісія: <b>{fee}%</b> ({fee_amount} PLN)\n"
            "До виплати: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "Підтвердити виведення?"
        ),
        "withdraw_btn_yes": "✅ Так",
        "withdraw_btn_no": "❌ Ні",
        "withdraw_created": (
            "✅ <b>Заявку на виведення створено</b>\n\n"
            "Номер: <code>#{id}</code>\n"
            "До виплати: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "⏱ Виведення протягом 24 годин."
        ),
        "withdraw_cancel_ask": "❓ Ви впевнені, що хочете скасувати виведення <code>#{id}</code>?",
        "withdraw_cancelled": "✅ Виведення <code>#{id}</code> скасовано. Кошти повернено на баланс.",
        "withdraw_not_pending": "❌ Заявку не знайдено або вже опрацьовано.",
        "withdraw_already_pending": "⚠️ У вас вже є активна заявка на виведення. Скасуйте її, щоб створити нову.",
        "withdraw_admin_message": (
            "🏦 <b>Новий запит на виведення</b>\n\n"
            "👤 {mention}{username}\n"
            "🆔 <code>{user_id}</code>\n"
            "💸 Запит: <b>{amount} PLN</b>\n"
            "🧾 Комісія: {fee}% ({fee_amount} PLN)\n"
            "💵 До виплати: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>"
        ),
        "withdraw_admin_btn_approve": "✅ Прийняти",
        "withdraw_admin_approved": "✅ <b>ОПЛАЧЕНО</b>",
        "withdraw_admin_cancelled": "❌ <b>СКАСОВАНО</b>",
        "withdraw_approved_user": (
            "✅ Ваше виведення <code>#{id}</code> на суму <b>{payout} PLN</b> надіслано."
        ),
        "cabinet_title": "💼 Особистий кабінет",
        "cabinet_balance": "💰 Баланс: <b>{balance} PLN</b>",
        "btn_signup": "Записатися на гру",
        "main_menu_chat_fallback": "💬 Чат",
        "btn_play_21_bot": "Грати в 21",
        "btn_casino": "🎰 Казино 🎰",
        "btn_admin": "Адмінка",
        "btn_lang": "🌐",
        "btn_main": "🏠 Головна",
        "btn_back": "← Назад",
        "admin_title": "Адмінка",
        "admin_no_access": "⛔ Немає доступу",
        "admin_btn_games": "🎯 Ігри",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Казино",
        "admin_btn_checkers": "🔴 Шашки",
        "admin_btn_kmb": "🪖 КМБ",
        "admin_btn_stats": "📊 Статистика",
        "admin_btn_bot_settings": "⚙️ Налаштування бота",
        "admin_games_title": "🎯 <b>Ігри</b>",
        "admin_btn_create_game": "➕ Створити гру",
        "admin_btn_active_games": "🟢 Поточні ігри",
        "admin_btn_past_games": "📚 Минулі ігри",
        "admin_wip": "🚧 У розробці",
        "admin_settings_title": "⚙️ Налаштування бота",
        "admin_btn_payments": "💳 Налаштування платежів",
        "admin_btn_fees": "💸 Налаштування комісій",
        "admin_btn_withdraw_fee": "💸 Комісія виводу",
        "admin_fees_title": "💸 <b>Налаштування комісій</b>",
        "admin_pay_title": "<b>MBanks</b> — акаунти:",
        "admin_pay_empty": "<b>MBanks</b>\nАкаунтів немає.",
        "admin_pay_btn_add": "➕ Додати акаунт",
        "admin_pay_btn_withdraw_fee": "💸 Комісія виводу",
        "admin_withdraw_fee_title": "💸 <b>Комісія виводу</b>\n\nПоточне значення: <b>{percent}%</b>\n\nВведіть новий відсоток (наприклад <code>5</code> або <code>2.5</code>):",
        "admin_withdraw_fee_invalid": "❌ Невірний формат. Введіть число від 0 до 100 (наприклад <code>5</code> або <code>2.5</code>).",
        "admin_withdraw_fee_updated": "✅ Комісію виводу оновлено: <b>{percent}%</b>",
        "admin_btn_game21_fees": "♠️ 21 — fees",
        "admin_fees_21_title": "♠️ <b>Game 21 fees</b>\n\nVs bot: <b>{bot}%</b>\nPvP: <b>{users}%</b>",
        "admin_game21_fee_btn_bot": "Vs bot",
        "admin_game21_fee_btn_users": "Between users",
        "admin_game21_fee_bot_title": "💸 21 fee (vs bot)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_users_title": "💸 21 fee (PvP)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_updated": "✅ 21 fee updated: <b>{percent}%</b>",
        "admin_21_title": "♠️ <b>Гра 21</b>\n\nБот: {bot}\n\nКомісії: бот {bot_fee}% · PvP {users_fee}%\n\nУвімкніть PvP для кожного підключеного чату. Якщо бот уже знає теми форуму в цьому чаті, після увімкнення відкриється екран дозволених тем.",
        "admin_21_on": "🟢 on",
        "admin_21_off": "⚪ off",
        "admin_21_btn_bot_on": "Vs bot: turn off",
        "admin_21_btn_bot_off": "Vs bot: turn on",
        "admin_21_btn_users_on": "PvP global: turn off",
        "admin_21_btn_users_off": "PvP global: turn on",
        "admin_21_chat_pvp_on": "PvP in «{title}»: off",
        "admin_21_chat_pvp_off": "PvP in «{title}»: on",
        "game21_active_notice": "You already have an active 21 game.",
        "game21_bot_midgame_menu_blocked": (
            "Ви зараз у активній грі. Спочатку завершіть поточну гру."
        ),
        "game21_busy_screen_text": "У вас вже є активна гра в чаті {chat}",
        "game21_busy_screen_text_bot": (
            "У вас вже є активна гра з ботом. Доіграйте партію в цьому чаті."
        ),
        "game21_btn_abort_session": "Скасувати гру",
        "game21_active_cancelled_toast": "Поточну сесію 21 скасовано.",
        "game21_no_active_search_to_cancel": (
            "Немає активного пошуку суперника (його вже скасовано або гра почалася)."
        ),
        "game21_pvp_choose_topic": "Оберіть ігрову кімнату (🟢 вільна, 🔴 зайнята):",
        "game21_pvp_topic_free": "🟢",
        "game21_pvp_topic_busy": "🔴",
        "game21_pvp_topic_general": "General",
        "game21_pvp_search_post_failed": "Could not post search. Bet refunded.",
        "game21_pvp_decide_prompt_other": "{name}, roll the dice 🎲 once.",
        "game21_menu_title": "Game 21",
        "game21_btn_rules": "Rules",
        "game21_btn_vs_bot": "Play vs bot",
        "game21_btn_vs_user_chat": "Play vs user in chat",
        "game21_coming_soon_all_off": "Game 21 is unavailable.",
        "game21_coming_soon_play": "Vs bot is unavailable.",
        "game21_enter_bet": "Enter bet (PLN):",
        "game21_bet_invalid": "Invalid amount.",
        "game21_not_enough_balance": "Insufficient balance.",
        "game21_confirm_bet_with_win": "Bet: {amount} PLN\nPossible win: {win} PLN\n\nConfirm?",
        "game21_btn_yes": "Yes",
        "game21_btn_no": "No",
        "game21_cancelled": "Cancelled.",
        "game21_rules_title": "<b>Rules 21</b>",
        "game21_rules": "See sections below.",
        "game21_rules_bot": "<b>Vs bot</b>\nRoll 🎲 in DM. Min 16, then Stop. Bot rolls after you.",
        "game21_rules_users": "<b>PvP in {chat_title}</b>\nFind opponent, roll for order, play to 21.",
        "game21_throw_now": "Roll the dice 🎲",
        "game21_player_result": "Your total: {total}",
        "game21_player_busted": "Your total: {total}\nBust!",
        "game21_player_blackjack": "You have 21!",
        "game21_player_can_stop": "Your total: {total}\nRoll or press Stop.",
        "game21_btn_stop": "Stop",
        "game21_bot_turn_start": "Bot's turn.",
        "game21_bot_result": "Bot total: {total}",
        "game21_result_win": "You won!",
        "game21_result_lose": "You lost.",
        "game21_result_draw": "Draw.",
        "game21_end_bot_win": (
            "<b>Ви виграли!</b>\n"
            "На баланс зараховано <b>{payout} PLN</b>.\n"
            "Рахунок: ви {player_total} — бот {bot_total}."
        ),
        "game21_end_bot_lose": "Ви програли {bet} PLN\nРахунок: ви {player_total} — бот {bot_total}.",
        "game21_end_bot_lose_bust": "Ви програли {bet} PLN\nПеребір: {player_total}.",
        "game21_end_bot_draw": (
            "<b>Нічия.</b>\n"
            "Ставку <b>{bet} PLN</b> повернуто на баланс.\n"
            "Рахунок: {player_total} — {bot_total}."
        ),
        "game21_pvp_enter_bet": "Введіть суму ставки (PLN):\n\nГра в 21 у {room}",
        "game21_pvp_confirm": "Start opponent search?\nBet: {amount} PLN\nPossible win: {win} PLN",
        "game21_pvp_search_started": (
            "Пошук суперника розпочато\n\n"
            "З вашого балансу списано ставку {amount} PLN"
        ),
        "game21_pvp_choose_chat": "Choose a chat:",
        "game21_pvp_no_available_chat": "No chats available for PvP.",
        "game21_pvp_must_join_chat": "You must be in the chat: {chat_title}",
        "game21_pvp_not_member_title": "Ви не в ігровому чаті",
        "game21_pvp_not_member_intro": "Щоб грати в 21 з іншим користувачем, увійдіть у чат за посиланням нижче. Потім знову оберіть у боті пункт гри з користувачем у чаті.",
        "game21_pvp_main_active_exists": "Неможливо створити запит на гру, бо там зараз триває гра.",
        "game21_pvp_active_exists": "This slot already has a game or search.",
        "game21_pvp_self_accept_forbidden": "You cannot accept your own request.",
        "game21_pvp_search_post": "{user} looks for a 21 opponent\n\nBet: {amount} PLN\nWin up to: {win} PLN\n\nBalance in bot {bot_link}",
        "game21_pvp_btn_accept": "Accept",
        "game21_pvp_match_title": "Гра в 21",
        "game21_pvp_match_started_in_topic": "Гра в 21 розпочалась у {room}",
        "game21_pvp_match_prize": "<b>Сума виграшу: {win} PLN</b>",
        "game21_pvp_match_rules_heading": "Правила гри:",
        "game21_pvp_rules_body": (
            "Спочатку кожен один раз кидає кубик 🎲 — менший результат ходить першим. "
            "Далі по черзі набираєте очки, ціль — якомога ближче до 21, не більше. "
            "Коли дозволено правилами, можна «Стоп». "
            "Після зупинок або перебору порівнюють суми; можлива нічия."
        ),
        "game21_pvp_started": "Game 21\n{p1}\n{p2}\n\nBet: {amount} PLN · win up to {win} PLN\n{bot_link}",
        "game21_pvp_general_started_notice": "Гра в 21 між {p1} та {p2} розпочалась у <b>{room}</b>.",
        "game21_pvp_topic_started_notice": "Гра в 21 між {p1} та {p2} розпочалась.\n\nНагорода: {prize} PLN.",
        "game21_pvp_decide_first": "{players} — roll 🎲 once each (lower starts).",
        "game21_pvp_decide_roll_result": "{name} rolled {value}",
        "game21_pvp_decide_tie": "Tie on rolls. Roll again.",
        "game21_pvp_turn_prompt": "{name}, your turn. Roll 🎲",
        "game21_pvp_player_result": "{name}: {total}",
        "game21_pvp_player_busted": "{name}: {total} — bust!",
        "game21_pvp_player_blackjack": "{name} — 21!",
        "game21_pvp_player_can_stop": "{name}: {total}. Stop or roll again.",
        "game21_pvp_stop_announce": "{name} stopped at {total}",
        "game21_pvp_not_your_turn_stop": "It is {name}'s turn now.",
        "game21_pvp_stop_only_on_equal": "Stop is only when totals are equal.",
        "game21_pvp_winner": "Winner: {name}\nPayout {payout} PLN · {bot_link}",
        "game21_pvp_draw": "Draw. Refund {amount} PLN · {bot_link}",
        "game21_pvp_pm_bet_deducted": "Bet deducted: {amount} PLN.",
        "game21_pvp_search_not_accepted": "No one accepted. Refund {amount} PLN.",
        "game21_pvp_topic_forbidden": "Ця тема недоступна для гри.",
        "game21_pvp_topics_restricted_empty": "У цьому чаті немає тем, дозволених адміністратором для ігор.",
        # ---- Chats settings ----
        "admin_chats_title": "💬 <b>Підключені чати</b>",
        "admin_chats_empty": "Чатів поки немає.",
        "admin_chats_list_line": "• <code>{chat_id}</code> · {title}",
        "admin_chats_btn_add": "➕ Додати чат",
        "admin_chats_btn_delete": "🗑 Видалити чат",
        "admin_chats_btn_game_topics": "📋 Теми для ігор",
        "admin_chats_topics_choose_chat": "Оберіть чат, у якому налаштувати, у яких темах форуму можна грати (21 PvP та ігри з кубиком):",
        "admin_chats_topics_not_forum": "Цей чат не форум-супергрупа з темами — налаштування не потрібне.",
        "admin_chats_topics_chat_unavailable": "Не вдалося відкрити чат.",
        "admin_chats_topics_body_open": (
            "📋 <b>Теми для ігор</b>: {title}\n\n"
            "Зараз без обмежень — 21 PvP і створення ігор доступні в усіх відомих темах і в загальному чаті.\n\n"
            "Натисніть «Увімкнути обмеження за темами», щоб явно обрати, де дозволені ігри (список заповниться поточними темами; зніміть зайві галочки)."
        ),
        "admin_chats_topics_body_restricted": (
            "📋 <b>Теми для ігор</b>: {title}\n\n"
            "Увімкнено список дозволених тем. Ігри лише там, де стоїть ✅.\n\n"
            "«Зняти обмеження» — знову дозволити всюди."
        ),
        "admin_chats_topics_btn_enable": "Увімкнути обмеження за темами",
        "admin_chats_topics_btn_disable": "Зняти обмеження (усі теми)",
        "admin_chats_enter_button_title": (
            "Введіть <b>назву кнопки</b> — так вона відображатиметься користувачам при виборі чату. "
            "Зараз один і той самий текст буде збережено для <b>ru / en / uk / pl</b>; пізніше можна "
            "задати окремі підписи для кожної мови.\n\n"
            "До 200 символів."
        ),
        "admin_chats_invalid_button_title": "❌ Введіть непорожню назву (до 200 символів).",
        "admin_chats_enter_chat_id": (
            "Введіть <b>ID чату</b> (наприклад <code>-1001234567890</code>).\n\n"
            "Щоб дізнатися ID: додайте бота в групу і перешліть звідти будь-яке повідомлення боту "
            "<a href=\"https://t.me/userinfobot\">@userinfobot</a>, або скористайтеся сервісом на кшталт getidsbot."
        ),
        "admin_chats_invalid_id": "❌ Невірний формат. Введіть число, що починається з <code>-100</code>.",
        "admin_chats_already_added": "⚠️ Цей чат уже підключений.",
        "admin_chats_added": "✅ Чат <code>{chat_id}</code> підключено.",
        "admin_chats_invite_ok": "✅ Посилання-запрошення створено автоматично.",
        "admin_chats_invite_link_failed": (
            "⚠️ Не вдалося отримати invite-посилання: переконайтеся, що бот у чаті як <b>адміністратор</b> "
            "з правом запрошувати учасників (або що в групі дозволені запрошення за посиланням)."
        ),
        "admin_chats_session_lost": "⚠️ Сесію додавання скинуто. Почніть знову з «Додати чат».",
        "admin_chats_delete_choose": "Оберіть чат для видалення:",
        "admin_chats_delete_confirm": "Видалити чат <code>{chat_id}</code>?",
        "admin_chats_deleted": "✅ Чат видалений.",
        "admin_chats_delete_none": "Немає підключених чатів для видалення.",
        # ---- Games create FSM ----
        "admin_game_no_chats": "⚠️ Спершу підключіть хоч один чат: Налаштування бота → Чати.",
        "admin_game_pick_chat": "В якому чаті анонсувати гру?",
        "admin_game_pick_forum_topic": "📂 <b>Тема форуму</b>\n\nОберіть тему, де відбуватиметься гра (анонс, раунди, кидки).\n\nЯкщо на кнопці «Гілка · id …»: бот бачить лише внутрішній id вітки (у звичайних повідомленнях немає видимої назви). Один раз перейменуйте тему в групі — бот оновить підпис.",
        "admin_game_pick_forum_topic_empty": "📂 <b>Тема форуму</b>\n\nСписок порожній: Telegram не віддає список тем через API, бот запам’ятовує вітки з повідомлень і службових подій.\n\nЯкщо теми вже є: надішліть у кожну потрібну тему будь-яке повідомлення (або один раз перейменуйте тему), потім натисніть «🔄 …».\n\nМожна пропустити й вести гру в загальному чаті без гілки.",
        "admin_game_forum_skip": "Без теми (загальний чат)",
        "admin_game_forum_reload": "🔄 Оновити список тем",
        "admin_game_forum_thread_placeholder": "Гілка · id {id}",
        "admin_game_forum_reload_toast": "Список оновлено",
        "admin_game_forum_reload_lost": "⚠️ Сесію скинуто. Почніть створення гри знову.",
        "admin_game_topic_forbidden": "Неможливо обрати цю тему: її немає в списку дозволених для цього чату.",
        "admin_game_pick_type": "🎯 <b>Тип гри</b>\n\nОберіть вид кидка:",
        "admin_game_type_dice": "🎲 Кубики",
        "admin_game_type_bowling": "🎳 Боулінг",
        "admin_game_type_darts": "🎯 Дартс",
        "admin_game_type_any": "🎲 🎳 🎯 (будь-який кидок)",
        "admin_game_name_prefix": "Гра",
        "admin_game_enter_participants": "👥 <b>Кількість учасників</b>\n\nВведіть мін./макс. через «/» або «-».\nПриклад: <code>10/100</code>",
        "admin_game_invalid_participants": "❌ Формат: <code>min/max</code>, обидва — додатні числа, min ≤ max.",
        "admin_game_enter_prizes": "🏆 <b>Призи</b>\n\nВведіть суми у PLN, кожна з нового рядка. Кількість рядків = кількість місць.\nПриклад:\n<code>20\n10\n5</code>\n\nПереможцям ці суми будуть нараховані на баланс автоматично.",
        "admin_game_invalid_prizes": "❌ Призи мають бути додатними числами (наприклад <code>20</code> або <code>10.5</code>), кожне з нового рядка.",
        "admin_game_prizes_more_than_max": "❌ Призових місць ({n}) більше за максимум учасників ({max}).",
        "admin_game_enter_min_topup": "💰 <b>Умова: мінімальна сума поповнень</b>\n\nФормати:\n• <code>0</code> — без умов\n• <code>100</code> — поповнив на 100 PLN за весь час\n• <code>100 : 01.01.2026</code> — поповнив на 100 PLN з вказаної дати",
        "admin_game_invalid_min_topup": "❌ Формат: число (<code>100</code>) або число + дата через «:» (<code>100 : 01.01.2026</code>).",
        "admin_game_enter_entry_fee": "💵 <b>Вартість внеску</b>\n\nВведіть суму у PLN (0 — безкоштовно).",
        "admin_game_invalid_entry_fee": "❌ Введіть число ≥ 0 (наприклад <code>0</code> або <code>5</code>).",
        "admin_game_enter_datetime": "🗓 <b>Дата і час старту</b>\n\nФормати:\n• <code>ДД.ММ.РРРР ГГ:ХХ</code>\n• <code>ГГ:ХХ</code> (сьогодні)",
        "admin_game_invalid_datetime": "❌ Не вдалося розпізнати дату/час. Приклад: <code>25.12.2026 19:30</code>.",
        "admin_game_datetime_in_past": "❌ Час старту має бути в майбутньому.",
        "admin_game_topup_since_after_start": "❌ Дата початку періоду пізніша за дату старту гри.",
        "admin_game_preview_title": "📋 <b>Превʼю гри</b>",
        "admin_game_preview_chat": "Чат: <b>{chat}</b>",
        "admin_game_preview_forum_topic": "Тема: <b>{topic}</b>",
        "admin_game_preview_type": "Тип: <b>{type}</b>",
        "admin_game_preview_participants": "Учасники: <b>{min}–{max}</b>",
        "admin_game_preview_prizes": "Призи:",
        "admin_game_preview_min_topup_none": "Умова: <b>без умов</b>",
        "admin_game_preview_min_topup_alltime": "Умова: поповнення від <b>{n} PLN</b> (за весь час)",
        "admin_game_preview_min_topup_period": "Умова: поповнення від <b>{n} PLN</b> з <b>{since}</b>",
        "admin_game_preview_pay_free": "Тип: <b>безкоштовна</b>",
        "admin_game_preview_pay_paid": "Тип: <b>платна</b>, внесок <b>{fee} PLN</b>",
        "admin_game_preview_datetime": "Старт: <b>{datetime}</b>",
        "admin_btn_confirm_create": "✅ Створити",
        "admin_btn_cancel_create": "❌ Скасувати",
        "admin_game_created": "✅ Гра #{id} створена.",
        "admin_game_create_cancelled": "❌ Скасовано.",
        # ---- Game lists ----
        "admin_games_active_title": "🟢 <b>Поточні ігри</b>",
        "admin_games_past_title": "📚 <b>Минулі ігри</b>",
        "admin_games_empty_active": "Зараз активних ігор немає.",
        "admin_games_empty_past": "Минулих ігор поки немає.",
        "admin_game_detail_title": "🎯 <b>Гра #{id}</b>",
        "admin_game_detail_status": "Статус: <b>{status}</b>",
        "admin_game_detail_participants_count": "Записалось: <b>{count}/{max}</b> (мін. {min})",
        "admin_game_status_draft": "очікує старту",
        "admin_game_status_active": "йде зараз",
        "admin_game_status_finished": "завершена",
        "admin_game_status_cancelled": "скасована",
        # ---- Announcement ----
        "game_announce_title": "🎯 Гра для <b>{chat}</b> створена",
        "game_announce_date": "Дата: <b>{date}</b>",
        "game_announce_participants_range": "Учасники: <b>{min}–{max}</b>",
        "game_announce_conditions": "<b>Умови участі:</b>",
        "game_announce_cond_min_topup_alltime": "• мінімум поповнень: <b>{n} PLN</b> (за весь час)",
        "game_announce_cond_min_topup_period": "• мінімум поповнень: <b>{n} PLN</b> (з {since} до старту)",
        "game_announce_cond_pay_free": "• безкоштовно",
        "game_announce_cond_pay_paid": "• платна, внесок <b>{fee} PLN</b>",
        "game_announce_cond_none": "• без додаткових умов",
        "game_announce_prizes": "<b>Призи:</b>",
        "game_announce_signup_link": "Запис на гру через бота {bot_link}",
        "game_announce_signup_no_link": "Запис на гру — напишіть боту в особисті.",
        "game_btn_signup": "🎮 Записатись на гру",
        "game_reminder_5min": "⏳ До гри в «{chat_title}» залишилось близько 5 хвилин.",
        "game_cancelled_not_enough_players_dm": "Гру скасовано: записалося лише {current} з {required} учасників.",
        "game_cancelled_refund_full_fee": "Внесок {fee} PLN повернуто на баланс.",
        "game_start_header": "<b>Умови:</b>\n{conditions}\n\n<b>Призи:</b>\n{prizes}",
        "game_start_cond_min_topup_period": "• мінімум поповнень: {n} PLN (з {since} до {until})",
        "game_start_cond_min_topup_alltime": "• мінімум поповнень: {n} PLN (за весь час)",
        "game_start_cond_paid": "• платна гра, внесок {fee} PLN",
        "game_start_cond_free": "• безкоштовна гра",
        "game_start_cond_none": "• без додаткових умов",
        "game_rules_block": (
            "Правила:\n"
            "1) Раунди по черзі, по 3 кидки на гравця.\n"
            "2) Можна кидати 🎲 🎳 🎯 (або тим самим текстом).\n"
            "3) Після раунду — прохідний бал за середнім серед тих, хто кинув.\n"
            "4) Пропуски — доганяюча спроба.\n"
            "5) Фінал і тай-брейк — за логікою бота."
        ),
        "game_round1_list_intro": "Перший раунд!",
        "round_list_participants": "Список учасників",
        "round_score_pending": "…",
        "round_score_eliminated": "вибув",
        "round_your_result": "Ваш кидок: {value}",
        "round_throw_2_more": "Зробіть ще 2 кидки {emoji}",
        "round_throw_1_more": "Зробіть ще 1 кидок {emoji}",
        "round_third_throw_done": "{result_line}\n{name}, підсумок у раунді: <b>{total}</b>",
        "round_throw_prompt": "{name}, зробіть 3 кидки будь-яким емодзі: {emoji}",
        "round_turn_60sec_left": "{name}, залишилась 1 хвилина на хід.",
        "round_participant_skipped": "{name} — хід пропущено.",
        "round_participants_missed": "Учасники без очок у цьому раунді:",
        "round_catchup_5min": "Є час на 3 кидки (прискорений режим).",
        "round_1_finished": "Перший раунд завершено.",
        "round_N_finished": "Раунд {round} завершено.",
        "round_passing_score": "Прохідний бал: {score}",
        "round_list_passed": "До наступного раунду проходять:",
        "round_list_passed_final": "До фінального раунду проходять:",
        "round_results_header": "Результати:",
        "round_tiebreak": "Тай-брейк!",
        "round_tiebreak_for": "Щоб визначити: {places}",
        "round_tiebreak_place_one": "{n}-е місце",
        "round_tiebreak_place_span": "місця з {a} по {b}",
        "round_tiebreak_throw": "{name}, зробіть 1 кидок {emoji}",
        "round_tiebreak_result": "{name} — кидок тай-брейку: {value}",
        "round_final_finished": "Фінальний раунд завершено.",
        "round_winners": "Переможці:",
        "game_sponsor_line": "Спонсор: {bot_link}",
        "game_dm_prize_won": "🎉 Ви зайняли {place} місце! На баланс зараховано <b>{amount} PLN</b>.",
        "game_signup_no_games": "Зараз немає ігор з відкритим записом.",
        "game_signup_list_title": "Відкритий запис (оберіть гру):",
        "game_signup_list_item": "#{id} {when} — {chat}",
        "game_signup_btn_join": "✅ Записатись",
        "game_signup_btn_leave": "🚫 Вийти",
        "game_signup_not_found": "Гру не знайдено.",
        "game_signup_not_draft": "Запис недоступний (гра не в чернетці).",
        "game_signup_started": "Гра вже стартувала або запис закрито.",
        "game_signup_full": "Місць немає.",
        "game_signup_min_topup": "Недостатньо поповнень: потрібно {need} PLN, у вас {have} PLN.",
        "game_signup_low_balance": "Недостатньо коштів: внесок {fee} PLN, баланс {balance} PLN.",
        "game_signup_already_in": "Ви вже в списку.",
        "game_signup_ok": "Вас записано.",
        "game_signup_left": "Ви вийшли зі списку.",
        "game_signup_not_in": "Вас не було в списку.",
        "game_signup_card": (
            "🎯 <b>Гра #{id}</b>\n"
            "Чат: {chat}\n"
            "Старт: <b>{start}</b>\n"
            "Гравці: <b>{count}</b> / {max_p} (мін. {min_p})\n\n"
            "<b>Умови:</b>\n{conditions}\n\n"
            "<b>Призи (PLN):</b>\n{prizes}"
        ),
        "game_signup_cond_topup_period": "• поповнення від {n} PLN з {since}",
        "game_signup_cond_topup_alltime": "• поповнення від {n} PLN за весь час",
        "game_signup_cond_paid": "• внесок {fee} PLN",
        "game_signup_cond_free": "• безкоштовно",
        "game_signup_cond_none": "—",
        "admin_pay_btn_activate": "▶️ Запустити",
        "admin_pay_btn_deactivate": "⏹ Зупинити",
        "admin_pay_btn_edit_proxy": "🌐 Змінити проксі",
        "admin_pay_btn_edit_blik": "📱 Змінити BLIK",
        "admin_pay_btn_edit_limit": "📊 Змінити ліміт",
        "admin_pay_btn_rescan": "🔁 Перечитати останні листи",
        "admin_pay_btn_delete": "🗑 Видалити",
        "admin_pay_btn_delete_confirm": "✅ Підтвердити видалення",
        "admin_pay_btn_cancel": "❌ Скасувати",
        "admin_pay_btn_bank_custom": "✏️ Інший",
        "admin_btn_chats": "💬 Налаштування чатів",
        "admin_btn_forbidden_words": "🚫 Заборонені слова",
        "admin_btn_admins": "👥 Налаштування адмінів",
    },
    "pl": {
        "choose_language": "Wybierz język / Choose language:",
        "welcome_menu": "Witamy w bocie do gier",
        "welcome_user_id": "Twój ID: {user_id}",
        "welcome_balance": "Twoje saldo: {balance} PLN",
        "btn_cabinet": "Konto osobiste",
        "btn_topup": "💳 Doładuj saldo",
        "topup_enter_amount": "💳 <b>Doładowanie salda</b>\n\nWprowadź kwotę doładowania w PLN (od {min} do {max} PLN):",
        "topup_invalid_amount": "❌ Nieprawidłowa kwota. Wprowadź liczbę (np. 50).",
        "topup_out_of_range": "❌ Kwota musi być od {min} do {max} PLN.",
        "topup_no_accounts": "⚠️ Doładowania chwilowo niedostępne — brak aktywnych kont płatniczych. Spróbuj później.",
        "topup_order_created": (
            "💳 <b>Zamówienie doładowania utworzone</b>\n\n"
            "Kwota: <b>{amount} PLN</b>\n"
            "Numer zamówienia: <code>{order_id}</code>\n\n"
            "📱 Wykonaj przelew BLIK na numer:\n<code>{blik}</code>\n\n"
            "⚠️ <b>W tytule przelewu musisz wpisać kod:</b>\n<code>{order_id}</code>\n\n"
            "Saldo zostanie doładowane automatycznie po otrzymaniu wpłaty."
        ),
        "topup_btn_cancel_order": "❌ Anuluj zamówienie",
        "topup_order_cancelled": "❌ Zamówienie <code>{order_id}</code> anulowane.",
        "topup_order_not_found": "❌ Zamówienie nie znalezione lub już zamknięte.",
        "btn_withdraw": "💸 Wypłata środków",
        "btn_cancel_withdraw": "❌ Anuluj wypłatę",
        "withdraw_enter_amount": (
            "💸 <b>Wypłata środków</b>\n\n"
            "Wpisz kwotę w PLN (minimum {min} PLN).\n"
            "Prowizja: <b>{fee}%</b>\n"
            "⏱ Wypłata realizowana w ciągu 24 godzin."
        ),
        "withdraw_invalid_amount": "❌ Nieprawidłowa kwota. Wpisz liczbę (np. 150).",
        "withdraw_below_min": "❌ Wypłata dostępna od {min} PLN.",
        "withdraw_not_enough": "❌ Niewystarczające środki. Twoje saldo: {balance} PLN.",
        "withdraw_enter_blik": "📱 Wpisz numer BLIK (minimum 9 cyfr):",
        "withdraw_invalid_blik": "❌ Nieprawidłowy format BLIK. Minimum 9 cyfr.",
        "withdraw_confirm": (
            "💸 <b>Potwierdzenie wypłaty</b>\n\n"
            "Z salda: <b>{amount} PLN</b>\n"
            "Prowizja: <b>{fee}%</b> ({fee_amount} PLN)\n"
            "Do wypłaty: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "Potwierdzić wypłatę?"
        ),
        "withdraw_btn_yes": "✅ Tak",
        "withdraw_btn_no": "❌ Nie",
        "withdraw_created": (
            "✅ <b>Zlecenie wypłaty utworzone</b>\n\n"
            "Numer: <code>#{id}</code>\n"
            "Do wypłaty: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>\n\n"
            "⏱ Wypłata w ciągu 24 godzin."
        ),
        "withdraw_cancel_ask": "❓ Czy na pewno chcesz anulować wypłatę <code>#{id}</code>?",
        "withdraw_cancelled": "✅ Wypłata <code>#{id}</code> anulowana. Środki zwrócone na saldo.",
        "withdraw_not_pending": "❌ Zlecenie nie znalezione lub już przetworzone.",
        "withdraw_already_pending": "⚠️ Masz już aktywne zlecenie wypłaty. Anuluj je, aby utworzyć nowe.",
        "withdraw_admin_message": (
            "🏦 <b>Nowe zlecenie wypłaty</b>\n\n"
            "👤 {mention}{username}\n"
            "🆔 <code>{user_id}</code>\n"
            "💸 Żądane: <b>{amount} PLN</b>\n"
            "🧾 Prowizja: {fee}% ({fee_amount} PLN)\n"
            "💵 Do wypłaty: <b>{payout} PLN</b>\n"
            "📱 BLIK: <code>{blik}</code>"
        ),
        "withdraw_admin_btn_approve": "✅ Zatwierdź",
        "withdraw_admin_approved": "✅ <b>OPŁACONE</b>",
        "withdraw_admin_cancelled": "❌ <b>ANULOWANE</b>",
        "withdraw_approved_user": (
            "✅ Twoja wypłata <code>#{id}</code> na kwotę <b>{payout} PLN</b> została wysłana."
        ),
        "cabinet_title": "💼 Konto osobiste",
        "cabinet_balance": "💰 Saldo: <b>{balance} PLN</b>",
        "btn_signup": "Zapisz się na grę",
        "main_menu_chat_fallback": "💬 Czat",
        "btn_play_21_bot": "Graj w 21",
        "btn_casino": "🎰 Kasyno 🎰",
        "btn_admin": "Panel admina",
        "btn_lang": "🌐",
        "btn_main": "🏠 Główna",
        "btn_back": "← Wstecz",
        "admin_title": "Panel admina",
        "admin_no_access": "⛔ Brak dostępu",
        "admin_btn_games": "🎯 Gry",
        "admin_btn_21": "♠️ 21",
        "admin_btn_casino": "🎰 Kasyno",
        "admin_btn_checkers": "🔴 Warcaby",
        "admin_btn_kmb": "🪖 KMB",
        "admin_btn_stats": "📊 Statystyka",
        "admin_btn_bot_settings": "⚙️ Ustawienia bota",
        "admin_games_title": "🎯 <b>Gry</b>",
        "admin_btn_create_game": "➕ Utwórz grę",
        "admin_btn_active_games": "🟢 Bieżące gry",
        "admin_btn_past_games": "📚 Minione gry",
        "admin_wip": "🚧 W trakcie tworzenia",
        "admin_settings_title": "⚙️ Ustawienia bota",
        "admin_btn_payments": "💳 Ustawienia płatności",
        "admin_btn_fees": "💸 Ustawienia prowizji",
        "admin_btn_withdraw_fee": "💸 Prowizja wypłaty",
        "admin_fees_title": "💸 <b>Ustawienia prowizji</b>",
        "admin_pay_title": "<b>MBanks</b> — konta:",
        "admin_pay_empty": "<b>MBanks</b>\nBrak kont.",
        "admin_pay_btn_add": "➕ Dodaj konto",
        "admin_pay_btn_withdraw_fee": "💸 Prowizja wypłaty",
        "admin_withdraw_fee_title": "💸 <b>Prowizja wypłaty</b>\n\nObecnie: <b>{percent}%</b>\n\nWpisz nowy procent (np. <code>5</code> lub <code>2.5</code>):",
        "admin_withdraw_fee_invalid": "❌ Nieprawidłowy format. Wpisz liczbę od 0 do 100 (np. <code>5</code> lub <code>2.5</code>).",
        "admin_withdraw_fee_updated": "✅ Prowizja wypłaty zaktualizowana: <b>{percent}%</b>",
        "admin_btn_game21_fees": "♠️ 21 — fees",
        "admin_fees_21_title": "♠️ <b>Game 21 fees</b>\n\nVs bot: <b>{bot}%</b>\nPvP: <b>{users}%</b>",
        "admin_game21_fee_btn_bot": "Vs bot",
        "admin_game21_fee_btn_users": "Between users",
        "admin_game21_fee_bot_title": "💸 21 fee (vs bot)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_users_title": "💸 21 fee (PvP)\n\nCurrent: <b>{percent}%</b>\n\nEnter new percent:",
        "admin_game21_fee_updated": "✅ 21 fee updated: <b>{percent}%</b>",
        "admin_21_title": "♠️ <b>Gra 21</b>\n\nVs bot: {bot}\n\nProwizje: bot {bot_fee}% · PvP {users_fee}%\n\nWłącz PvP osobno dla każdego podłączonego czatu. Gdy bot zna wątki forum w tym czacie, po włączeniu otworzy się ekran dozwolonych wątków.",
        "admin_21_on": "🟢 on",
        "admin_21_off": "⚪ off",
        "admin_21_btn_bot_on": "Vs bot: turn off",
        "admin_21_btn_bot_off": "Vs bot: turn on",
        "admin_21_btn_users_on": "PvP global: turn off",
        "admin_21_btn_users_off": "PvP global: turn on",
        "admin_21_chat_pvp_on": "PvP in «{title}»: off",
        "admin_21_chat_pvp_off": "PvP in «{title}»: on",
        "game21_active_notice": "You already have an active 21 game.",
        "game21_bot_midgame_menu_blocked": (
            "Jesteś w trakcie aktywnej gry. Najpierw dokończ bieżącą grę."
        ),
        "game21_busy_screen_text": "Masz już aktywną grę na czacie {chat}.",
        "game21_busy_screen_text_bot": (
            "Masz już aktywną grę z botem. Dokończ rundę na tym czacie."
        ),
        "game21_btn_abort_session": "Anuluj grę",
        "game21_active_cancelled_toast": "Sesja 21 została anulowana.",
        "game21_no_active_search_to_cancel": (
            "Brak aktywnego szukania przeciwnika (już anulowane lub mecz się rozpoczął)."
        ),
        "game21_pvp_choose_topic": "Wybierz pokój gry (🟢 wolny, 🔴 zajęty):",
        "game21_pvp_topic_free": "🟢",
        "game21_pvp_topic_busy": "🔴",
        "game21_pvp_topic_general": "General",
        "game21_pvp_search_post_failed": "Could not post search. Bet refunded.",
        "game21_pvp_decide_prompt_other": "{name}, roll the dice 🎲 once.",
        "game21_menu_title": "Game 21",
        "game21_btn_rules": "Rules",
        "game21_btn_vs_bot": "Play vs bot",
        "game21_btn_vs_user_chat": "Play vs user in chat",
        "game21_coming_soon_all_off": "Game 21 is unavailable.",
        "game21_coming_soon_play": "Vs bot is unavailable.",
        "game21_enter_bet": "Enter bet (PLN):",
        "game21_bet_invalid": "Invalid amount.",
        "game21_not_enough_balance": "Insufficient balance.",
        "game21_confirm_bet_with_win": "Bet: {amount} PLN\nPossible win: {win} PLN\n\nConfirm?",
        "game21_btn_yes": "Yes",
        "game21_btn_no": "No",
        "game21_cancelled": "Cancelled.",
        "game21_rules_title": "<b>Rules 21</b>",
        "game21_rules": "See sections below.",
        "game21_rules_bot": "<b>Vs bot</b>\nRoll 🎲 in DM. Min 16, then Stop. Bot rolls after you.",
        "game21_rules_users": "<b>PvP in {chat_title}</b>\nFind opponent, roll for order, play to 21.",
        "game21_throw_now": "Roll the dice 🎲",
        "game21_player_result": "Your total: {total}",
        "game21_player_busted": "Your total: {total}\nBust!",
        "game21_player_blackjack": "You have 21!",
        "game21_player_can_stop": "Your total: {total}\nRoll or press Stop.",
        "game21_btn_stop": "Stop",
        "game21_bot_turn_start": "Bot's turn.",
        "game21_bot_result": "Bot total: {total}",
        "game21_result_win": "You won!",
        "game21_result_lose": "You lost.",
        "game21_result_draw": "Draw.",
        "game21_end_bot_win": (
            "<b>Wygrałeś!</b>\n"
            "Na balans wpłacono <b>{payout} PLN</b>.\n"
            "Wynik: ty {player_total} — bot {bot_total}."
        ),
        "game21_end_bot_lose": "Przegrałeś {bet} PLN\nWynik: ty {player_total} — bot {bot_total}.",
        "game21_end_bot_lose_bust": "Przegrałeś {bet} PLN\nPrzebicie: {player_total}.",
        "game21_end_bot_draw": (
            "<b>Remis.</b>\n"
            "Stawka <b>{bet} PLN</b> zwrócona na balans.\n"
            "Wynik: {player_total} — {bot_total}."
        ),
        "game21_pvp_enter_bet": "Wpisz stawkę (PLN):\n\nGra w 21 w {room}",
        "game21_pvp_confirm": "Start opponent search?\nBet: {amount} PLN\nPossible win: {win} PLN",
        "game21_pvp_search_started": (
            "Szukanie przeciwnika rozpoczęte.\n\n"
            "Z Twojego salda potrącono stawkę {amount} PLN"
        ),
        "game21_pvp_choose_chat": "Choose a chat:",
        "game21_pvp_no_available_chat": "No chats available for PvP.",
        "game21_pvp_must_join_chat": "You must be in the chat: {chat_title}",
        "game21_pvp_not_member_title": "Nie jesteś na czacie gry",
        "game21_pvp_not_member_intro": "Aby grać w 21 z innym użytkownikiem, dołącz do czatu przez poniższy link, a potem ponownie wybierz w bocie grę z użytkownikiem na czacie.",
        "game21_pvp_main_active_exists": "Nie można utworzyć zaproszenia do gry, ponieważ tam właśnie trwa gra.",
        "game21_pvp_active_exists": "This slot already has a game or search.",
        "game21_pvp_self_accept_forbidden": "You cannot accept your own request.",
        "game21_pvp_search_post": "{user} looks for a 21 opponent\n\nBet: {amount} PLN\nWin up to: {win} PLN\n\nBalance in bot {bot_link}",
        "game21_pvp_btn_accept": "Accept",
        "game21_pvp_match_title": "Gra w 21",
        "game21_pvp_match_started_in_topic": "Gra w 21 rozpoczęta w {room}",
        "game21_pvp_match_prize": "<b>Kwota wygranej: {win} PLN</b>",
        "game21_pvp_match_rules_heading": "Zasady:",
        "game21_pvp_rules_body": (
            "Na początku każdy raz rzuca kością 🎲 — mniejszy wynik zaczyna. "
            "Potem na zmianę zbieracie punkty, celem jest jak najbliżej 21, nie więcej. "
            "Gdy zasady na to pozwalają, można «Stop». "
            "Po zakończeniu lub przebiciu porównuje się sumy; możliwy jest remis."
        ),
        "game21_pvp_started": "Game 21\n{p1}\n{p2}\n\nBet: {amount} PLN · win up to {win} PLN\n{bot_link}",
        "game21_pvp_general_started_notice": "Gra w 21 między {p1} a {p2} rozpoczęła się w <b>{room}</b>.",
        "game21_pvp_topic_started_notice": "Gra w 21 między {p1} a {p2} rozpoczęła się.\n\nNagroda: {prize} PLN.",
        "game21_pvp_decide_first": "{players} — roll 🎲 once each (lower starts).",
        "game21_pvp_decide_roll_result": "{name} rolled {value}",
        "game21_pvp_decide_tie": "Tie on rolls. Roll again.",
        "game21_pvp_turn_prompt": "{name}, your turn. Roll 🎲",
        "game21_pvp_player_result": "{name}: {total}",
        "game21_pvp_player_busted": "{name}: {total} — bust!",
        "game21_pvp_player_blackjack": "{name} — 21!",
        "game21_pvp_player_can_stop": "{name}: {total}. Stop or roll again.",
        "game21_pvp_stop_announce": "{name} stopped at {total}",
        "game21_pvp_not_your_turn_stop": "Teraz ruch gracza {name}.",
        "game21_pvp_stop_only_on_equal": "Stop is only when totals are equal.",
        "game21_pvp_winner": "Winner: {name}\nPayout {payout} PLN · {bot_link}",
        "game21_pvp_draw": "Draw. Refund {amount} PLN · {bot_link}",
        "game21_pvp_pm_bet_deducted": "Bet deducted: {amount} PLN.",
        "game21_pvp_search_not_accepted": "No one accepted. Refund {amount} PLN.",
        "game21_pvp_topic_forbidden": "Ten wątek nie jest dostępny do gry.",
        "game21_pvp_topics_restricted_empty": "W tym czacie nie ma tematów dozwolonych przez administratora do gier.",
        # ---- Chats settings ----
        "admin_chats_title": "💬 <b>Podłączone czaty</b>",
        "admin_chats_empty": "Brak czatów.",
        "admin_chats_list_line": "• <code>{chat_id}</code> · {title}",
        "admin_chats_btn_add": "➕ Dodaj czat",
        "admin_chats_btn_delete": "🗑 Usuń czat",
        "admin_chats_btn_game_topics": "📋 Tematy do gier",
        "admin_chats_topics_choose_chat": "Wybierz czat, w którym ustawisz, w jakich wątkach forum można grać (21 PvP i gry z kośćmi):",
        "admin_chats_topics_not_forum": "Ten czat nie jest supergrupą forum z wątkami — nic do ustawiania.",
        "admin_chats_topics_chat_unavailable": "Nie udało się otworzyć czatu.",
        "admin_chats_topics_body_open": (
            "📋 <b>Tematy do gier</b>: {title}\n\n"
            "Teraz bez ograniczeń — 21 PvP i tworzenie gier są dozwolone we wszystkich znanych wątkach i w głównym czacie.\n\n"
            "Dotknij «Włącz limity wątków», aby wybrać, gdzie gra jest dozwolona (lista wypełni się bieżącymi wątkami; odznacz niepotrzebne)."
        ),
        "admin_chats_topics_body_restricted": (
            "📋 <b>Tematy do gier</b>: {title}\n\n"
            "Włączona jest lista dozwolonych wątków. Gra tylko tam, gdzie jest ✅.\n\n"
            "«Usuń limity» — znów wszędzie."
        ),
        "admin_chats_topics_btn_enable": "Włącz limity wątków",
        "admin_chats_topics_btn_disable": "Usuń limity (wszystkie wątki)",
        "admin_chats_enter_button_title": (
            "Wyślij <b>tekst przycisku</b> — taki zobaczą użytkownicy przy wyborze czatu. "
            "Ten sam tekst zapiszemy na razie dla <b>ru / en / uk / pl</b>; później można dodać "
            "osobne napisy dla każdego języka.\n\n"
            "Maks. 200 znaków."
        ),
        "admin_chats_invalid_button_title": "❌ Podaj niepusty tekst (maks. 200 znaków).",
        "admin_chats_enter_chat_id": (
            "Wyślij <b>ID czatu</b> (np. <code>-1001234567890</code>).\n\n"
            "Jak sprawdzić ID: dodaj bota do grupy i przekaż mu stamtąd dowolną wiadomość przez "
            "<a href=\"https://t.me/userinfobot\">@userinfobot</a> albo użyj bota typu getidsbot."
        ),
        "admin_chats_invalid_id": "❌ Nieprawidłowy format. Liczba całkowita zaczynająca się od <code>-100</code>.",
        "admin_chats_already_added": "⚠️ Ten czat jest już podłączony.",
        "admin_chats_added": "✅ Czat <code>{chat_id}</code> podłączony.",
        "admin_chats_invite_ok": "✅ Link zaproszenia utworzony automatycznie.",
        "admin_chats_invite_link_failed": (
            "⚠️ Nie udało się utworzyć linku zaproszenia: upewnij się, że bot jest <b>adminem</b> w czacie "
            "z prawem zapraszania użytkowników (albo że grupa zezwala na linki zaproszeń)."
        ),
        "admin_chats_session_lost": "⚠️ Sesja dodawania została zresetowana. Zacznij od «Dodaj czat».",
        "admin_chats_delete_choose": "Wybierz czat do usunięcia:",
        "admin_chats_delete_confirm": "Usunąć czat <code>{chat_id}</code>?",
        "admin_chats_deleted": "✅ Czat usunięty.",
        "admin_chats_delete_none": "Brak podłączonych czatów do usunięcia.",
        # ---- Games create FSM ----
        "admin_game_no_chats": "⚠️ Najpierw podłącz co najmniej jeden czat: Ustawienia bota → Czaty.",
        "admin_game_pick_chat": "W którym czacie ogłosić grę?",
        "admin_game_pick_forum_topic": "📂 <b>Wątek forum</b>\n\nWybierz wątek, w którym odbędzie się gra (ogłoszenie, rundy, rzuty).\n\nJeśli na przycisku jest «Wątek · id …», bot zna tylko wewnętrzny identyfikator (zwykłe wiadomości nie zawierają widocznej nazwy). Zmień raz nazwę wątku w grupie — bot zaktualizuje podpis.",
        "admin_game_pick_forum_topic_empty": "📂 <b>Wątek forum</b>\n\nLista jest pusta: Telegram nie udostępnia listy wątków w Bot API; bot uczy się wątków z wiadomości i zdarzeń serwisowych.\n\nJeśli wątki już są: wyślij dowolną wiadomość w każdym potrzebnym wątku (albo raz zmień nazwę), potem dotknij «🔄 …».\n\nMożesz pominąć i prowadzić grę w głównym czacie bez wątku.",
        "admin_game_forum_skip": "Bez wątku (główny czat)",
        "admin_game_forum_reload": "🔄 Odśwież listę wątków",
        "admin_game_forum_thread_placeholder": "Wątek · id {id}",
        "admin_game_forum_reload_toast": "Lista zaktualizowana",
        "admin_game_forum_reload_lost": "⚠️ Sesja wygasła. Zacznij tworzenie gry od nowa.",
        "admin_game_topic_forbidden": "Nie można wybrać tego wątku: nie ma go na liście dozwolonych dla tego czatu.",
        "admin_game_pick_type": "🎯 <b>Typ gry</b>\n\nWybierz rodzaj rzutu:",
        "admin_game_type_dice": "🎲 Kości",
        "admin_game_type_bowling": "🎳 Kręgle",
        "admin_game_type_darts": "🎯 Lotki",
        "admin_game_type_any": "🎲 🎳 🎯 (dowolny rzut)",
        "admin_game_name_prefix": "Gra",
        "admin_game_enter_participants": "👥 <b>Liczba uczestników</b>\n\nWpisz min/max przez «/» lub «-».\nPrzykład: <code>10/100</code>",
        "admin_game_invalid_participants": "❌ Format: <code>min/max</code>, dodatnie liczby, min ≤ max.",
        "admin_game_enter_prizes": "🏆 <b>Nagrody</b>\n\nWpisz kwoty w PLN, każda w nowej linii. Liczba linii = liczba miejsc.\nPrzykład:\n<code>20\n10\n5</code>\n\nZwycięzcy dostaną kwoty automatycznie na saldo.",
        "admin_game_invalid_prizes": "❌ Nagrody muszą być dodatnimi liczbami (np. <code>20</code> lub <code>10.5</code>), każda w nowej linii.",
        "admin_game_prizes_more_than_max": "❌ Miejsc nagrodowych ({n}) jest więcej niż maks. uczestników ({max}).",
        "admin_game_enter_min_topup": "💰 <b>Warunek: minimalna kwota doładowań</b>\n\nFormaty:\n• <code>0</code> — bez warunku\n• <code>100</code> — co najmniej 100 PLN w sumie\n• <code>100 : 01.01.2026</code> — co najmniej 100 PLN od podanej daty",
        "admin_game_invalid_min_topup": "❌ Format: liczba (<code>100</code>) lub liczba i data przez «:» (<code>100 : 01.01.2026</code>).",
        "admin_game_enter_entry_fee": "💵 <b>Opłata wejściowa</b>\n\nWpisz kwotę w PLN (0 = za darmo).",
        "admin_game_invalid_entry_fee": "❌ Wpisz liczbę ≥ 0 (np. <code>0</code> lub <code>5</code>).",
        "admin_game_enter_datetime": "🗓 <b>Data i czas startu</b>\n\nFormaty:\n• <code>DD.MM.RRRR HH:MM</code>\n• <code>HH:MM</code> (dziś)",
        "admin_game_invalid_datetime": "❌ Nie udało się rozpoznać daty/czasu. Przykład: <code>25.12.2026 19:30</code>.",
        "admin_game_datetime_in_past": "❌ Czas startu musi być w przyszłości.",
        "admin_game_topup_since_after_start": "❌ Data początku okresu doładowań jest po dacie startu.",
        "admin_game_preview_title": "📋 <b>Podgląd gry</b>",
        "admin_game_preview_chat": "Czat: <b>{chat}</b>",
        "admin_game_preview_forum_topic": "Wątek: <b>{topic}</b>",
        "admin_game_preview_type": "Typ: <b>{type}</b>",
        "admin_game_preview_participants": "Uczestnicy: <b>{min}–{max}</b>",
        "admin_game_preview_prizes": "Nagrody:",
        "admin_game_preview_min_topup_none": "Warunek: <b>brak</b>",
        "admin_game_preview_min_topup_alltime": "Warunek: doładowania od <b>{n} PLN</b> (cały czas)",
        "admin_game_preview_min_topup_period": "Warunek: doładowania od <b>{n} PLN</b> od <b>{since}</b>",
        "admin_game_preview_pay_free": "Typ: <b>za darmo</b>",
        "admin_game_preview_pay_paid": "Typ: <b>płatna</b>, wejście <b>{fee} PLN</b>",
        "admin_game_preview_datetime": "Start: <b>{datetime}</b>",
        "admin_btn_confirm_create": "✅ Utwórz",
        "admin_btn_cancel_create": "❌ Anuluj",
        "admin_game_created": "✅ Gra #{id} utworzona.",
        "admin_game_create_cancelled": "❌ Anulowano.",
        # ---- Game lists ----
        "admin_games_active_title": "🟢 <b>Bieżące gry</b>",
        "admin_games_past_title": "📚 <b>Minione gry</b>",
        "admin_games_empty_active": "Brak bieżących gier.",
        "admin_games_empty_past": "Brak minionych gier.",
        "admin_game_detail_title": "🎯 <b>Gra #{id}</b>",
        "admin_game_detail_status": "Status: <b>{status}</b>",
        "admin_game_detail_participants_count": "Zapisanych: <b>{count}/{max}</b> (min. {min})",
        "admin_game_status_draft": "oczekuje startu",
        "admin_game_status_active": "trwa",
        "admin_game_status_finished": "zakończona",
        "admin_game_status_cancelled": "anulowana",
        # ---- Announcement ----
        "game_announce_title": "🎯 Gra dla <b>{chat}</b> została utworzona",
        "game_announce_date": "Data: <b>{date}</b>",
        "game_announce_participants_range": "Uczestnicy: <b>{min}–{max}</b>",
        "game_announce_conditions": "<b>Warunki uczestnictwa:</b>",
        "game_announce_cond_min_topup_alltime": "• min. doładowania: <b>{n} PLN</b> (cały czas)",
        "game_announce_cond_min_topup_period": "• min. doładowania: <b>{n} PLN</b> (od {since} do startu)",
        "game_announce_cond_pay_free": "• za darmo",
        "game_announce_cond_pay_paid": "• płatna, wejście <b>{fee} PLN</b>",
        "game_announce_cond_none": "• bez dodatkowych warunków",
        "game_announce_prizes": "<b>Nagrody:</b>",
        "game_announce_signup_link": "Zapis przez bota {bot_link}",
        "game_announce_signup_no_link": "Zapisz się przez prywatną wiadomość do bota.",
        "game_btn_signup": "🎮 Zapisz się",
        "game_reminder_5min": "⏳ Do gry w «{chat_title}» zostało ok. 5 minut.",
        "game_cancelled_not_enough_players_dm": "Gra anulowana: zapisano tylko {current} z {required} graczy.",
        "game_cancelled_refund_full_fee": "Wpłata {fee} PLN została zwrócona na saldo.",
        "game_start_header": "<b>Warunki:</b>\n{conditions}\n\n<b>Nagrody:</b>\n{prizes}",
        "game_start_cond_min_topup_period": "• min. doładowań: {n} PLN (od {since} do {until})",
        "game_start_cond_min_topup_alltime": "• min. doładowań: {n} PLN (cały czas)",
        "game_start_cond_paid": "• gra płatna, wpisowe {fee} PLN",
        "game_start_cond_free": "• gra darmowa",
        "game_start_cond_none": "• bez dodatkowych warunków",
        "game_rules_block": (
            "Zasady:\n"
            "1) Rundy po kolei, 3 rzuty na gracza.\n"
            "2) Można rzucać 🎲 🎳 🎯 (wiadomość dice lub te same emoji w tekście).\n"
            "3) Po rundzie próg to średnia (całkowita część) wśród graczy, którzy rzucali.\n"
            "4) Pominięcia — dogrywka.\n"
            "5) Finał i dogrywka według logiki bota."
        ),
        "game_round1_list_intro": "Runda 1!",
        "round_list_participants": "Lista graczy",
        "round_score_pending": "…",
        "round_score_eliminated": "out",
        "round_your_result": "Twój rzut: {value}",
        "round_throw_2_more": "Rzuć jeszcze 2 razy {emoji}",
        "round_throw_1_more": "Rzuć jeszcze raz {emoji}",
        "round_third_throw_done": "{result_line}\n{name}, wynik rundy: <b>{total}</b>",
        "round_throw_prompt": "{name}, zrób 3 rzuty dowolnym emoji: {emoji}",
        "round_turn_60sec_left": "{name}, została 1 minuta na ruch.",
        "round_participant_skipped": "{name} — pominięty ruch.",
        "round_participants_missed": "Gracze z 0 w tej rundzie:",
        "round_catchup_5min": "Masz czas na 3 rzuty (tryb przyspieszony).",
        "round_1_finished": "Runda 1 zakończona.",
        "round_N_finished": "Runda {round} zakończona.",
        "round_passing_score": "Próg przejścia: {score}",
        "round_list_passed": "Awans do następnej rundy:",
        "round_list_passed_final": "Awans do rundy finałowej:",
        "round_results_header": "Wyniki:",
        "round_tiebreak": "Dogrywka!",
        "round_tiebreak_for": "Aby ustalić: {places}",
        "round_tiebreak_place_one": "{n}. miejsce",
        "round_tiebreak_place_span": "miejsca {a}–{b}",
        "round_tiebreak_throw": "{name}, zrób 1 rzut {emoji}",
        "round_tiebreak_result": "{name} — rzut dogrywki: {value}",
        "round_final_finished": "Finał zakończony.",
        "round_winners": "Zwycięzcy:",
        "game_sponsor_line": "Sponsor: {bot_link}",
        "game_dm_prize_won": "🎉 Zająłeś(-aś) {place}. miejsce! Na saldo dodano <b>{amount} PLN</b>.",
        "game_signup_no_games": "Brak gier z otwartym zapisem.",
        "game_signup_list_title": "Otwarty zapis (wybierz grę):",
        "game_signup_list_item": "#{id} {when} — {chat}",
        "game_signup_btn_join": "✅ Zapisz się",
        "game_signup_btn_leave": "🚫 Wypisz się",
        "game_signup_not_found": "Nie znaleziono gry.",
        "game_signup_not_draft": "Zapis niedostępny (gra nie jest w szkicu).",
        "game_signup_started": "Gra już wystartowała lub zapis zamknięty.",
        "game_signup_full": "Brak wolnych miejsc.",
        "game_signup_min_topup": "Za mało doładowań: wymagane {need} PLN, masz {have} PLN.",
        "game_signup_low_balance": "Za mało środków: wpisowe {fee} PLN, saldo {balance} PLN.",
        "game_signup_already_in": "Jesteś już zapisany(-a).",
        "game_signup_ok": "Zapisano.",
        "game_signup_left": "Wypisano z gry.",
        "game_signup_not_in": "Nie byłeś(-aś) zapisany(-a).",
        "game_signup_card": (
            "🎯 <b>Gra #{id}</b>\n"
            "Czat: {chat}\n"
            "Start: <b>{start}</b>\n"
            "Gracze: <b>{count}</b> / {max_p} (min {min_p})\n\n"
            "<b>Warunki:</b>\n{conditions}\n\n"
            "<b>Nagrody (PLN):</b>\n{prizes}"
        ),
        "game_signup_cond_topup_period": "• doładowania od {n} PLN od {since}",
        "game_signup_cond_topup_alltime": "• doładowania od {n} PLN (cały czas)",
        "game_signup_cond_paid": "• wpisowe {fee} PLN",
        "game_signup_cond_free": "• za darmo",
        "game_signup_cond_none": "—",
        "admin_pay_btn_activate": "▶️ Uruchom",
        "admin_pay_btn_deactivate": "⏹ Zatrzymaj",
        "admin_pay_btn_edit_proxy": "🌐 Zmień proxy",
        "admin_pay_btn_edit_blik": "📱 Zmień BLIK",
        "admin_pay_btn_edit_limit": "📊 Zmień limit",
        "admin_pay_btn_rescan": "🔁 Sprawdź ostatnie maile",
        "admin_pay_btn_delete": "🗑 Usuń",
        "admin_pay_btn_delete_confirm": "✅ Potwierdź usunięcie",
        "admin_pay_btn_cancel": "❌ Anuluj",
        "admin_pay_btn_bank_custom": "✏️ Inny",
        "admin_btn_chats": "💬 Ustawienia czatów",
        "admin_btn_forbidden_words": "🚫 Zabronione słowa",
        "admin_btn_admins": "👥 Ustawienia adminów",
    },
}


def get_lang(language_code: Optional[str]) -> str:
    if not language_code or not str(language_code).strip():
        return DEFAULT_LANG
    lang = str(language_code).strip().split("-")[0].split("_")[0].lower()
    return lang if lang in TEXTS else DEFAULT_LANG


def t(key: str, language_code: Optional[str] = None) -> str:
    lang = get_lang(language_code)
    return TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(
        key, TEXTS[DEFAULT_LANG].get(key, key)
    )
