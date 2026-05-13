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
