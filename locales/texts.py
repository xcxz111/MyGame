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
        "cabinet_title": "💼 Личный кабинет",
        "btn_signup": "🎮 Записаться на игру 🎯🎳🎲",
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
        "admin_settings_title": "⚙️ Настройки бота",
        "admin_btn_payments": "💳 Настройка платежей",
        "admin_pay_title": "<b>MBanks</b> — аккаунты:",
        "admin_pay_empty": "<b>MBanks</b>\nАккаунтов нет.",
        "admin_pay_btn_add": "➕ Добавить аккаунт",
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
        "cabinet_title": "💼 Personal account",
        "btn_signup": "Sign up for a game",
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
        "admin_settings_title": "⚙️ Bot settings",
        "admin_btn_payments": "💳 Payments settings",
        "admin_pay_title": "<b>MBanks</b> — accounts:",
        "admin_pay_empty": "<b>MBanks</b>\nNo accounts yet.",
        "admin_pay_btn_add": "➕ Add account",
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
        "cabinet_title": "💼 Особистий кабінет",
        "btn_signup": "Записатися на гру",
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
        "admin_settings_title": "⚙️ Налаштування бота",
        "admin_btn_payments": "💳 Налаштування платежів",
        "admin_pay_title": "<b>MBanks</b> — акаунти:",
        "admin_pay_empty": "<b>MBanks</b>\nАкаунтів немає.",
        "admin_pay_btn_add": "➕ Додати акаунт",
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
        "cabinet_title": "💼 Konto osobiste",
        "btn_signup": "Zapisz się na grę",
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
        "admin_settings_title": "⚙️ Ustawienia bota",
        "admin_btn_payments": "💳 Ustawienia płatności",
        "admin_pay_title": "<b>MBanks</b> — konta:",
        "admin_pay_empty": "<b>MBanks</b>\nBrak kont.",
        "admin_pay_btn_add": "➕ Dodaj konto",
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
