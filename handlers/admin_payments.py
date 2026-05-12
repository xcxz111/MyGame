"""Админ‑UI «Настройка платежей»: список mbank‑аккаунтов, добавление,
карточка, изменение прокси/BLIK/лимита, удаление."""

import logging
import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
)
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.models.payments.account import MBankAccount
from database.repositories.payments import accounts as accounts_repo
from services.payments import MonitorManager
from keyboards.admin_payments import (
    BANK_LABELS,
    NO_PROXY_BTN_TEXT,
    REMOVE_LIMIT_BTN_TEXT,
    account_detail_keyboard,
    bank_select_keyboard,
    delete_confirm_keyboard,
    no_proxy_keyboard,
    payments_list_keyboard,
    remove_limit_keyboard,
)
from locales.texts import get_lang, t
from permissions import is_admin
from settings import get_settings
from states.admin_payments import MBankAccountState

logger = logging.getLogger(__name__)

router = Router(name="admin_payments")

WARSAW_TZ = ZoneInfo("Europe/Warsaw")

# Прокси: http(s)://user:pass@host:port  или  socks4/5://user:pass@host:port
_PROXY_RE = re.compile(r"^(https?|socks[45])://[^:@]+:[^@]+@[\w.\-]+:\d+$")

LIMIT_TYPE_LABELS = {
    "all": "Все транзакции",
    "matched": "Созданные ботом",
}


# ── Helpers ───────────────────────────────────────────────────────────────────


def _resolve_lang(user: User, event) -> str:
    return user.language_code or get_lang(getattr(event.from_user, "language_code", None))


async def _deny_if_not_admin_cb(callback: CallbackQuery, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await callback.answer(t("admin_no_access", lang), show_alert=True)
    return True


async def _deny_if_not_admin_msg(message: Message, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await message.answer(t("admin_no_access", lang))
    return True


def _fmt_dt(dt: datetime | None) -> str:
    if not dt:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(WARSAW_TZ).strftime("%d.%m %H:%M")


def _fmt_limit(daily_limit: Decimal | None) -> str:
    if daily_limit is None:
        return "без лимита"
    # Без .00, если ровное число
    if daily_limit == daily_limit.to_integral_value():
        return str(int(daily_limit))
    return str(daily_limit)


def _fmt_balance(balance: Decimal | None) -> str:
    if balance is None:
        return "—"
    return f"{float(balance):.2f}"


def _status(account: MBankAccount) -> tuple[str, str]:
    if not account.is_active:
        return "⚪", "Остановлен"
    if account.limit_sleeping:
        return "😴", "Спит (лимит)"
    return "🟢", "Активен"


def _account_short_line(account: MBankAccount) -> str:
    emoji, label = _status(account)
    sleep = " 😴" if account.limit_sleeping else ""
    used = account.daily_used or Decimal("0")
    return (
        f"{emoji} <b>#{account.id}</b> <code>{account.email}</code>"
        f" | {label}\n"
        f"🔢 {account.blik_number or '—'}\n"
        f"💰 {_fmt_balance(account.balance)} PLN | "
        f"🕒 баланс: {_fmt_dt(account.balance_updated_at)}\n"
        f"📊 {used}/{_fmt_limit(account.daily_limit)}{sleep}"
    )


def _account_full_text(account: MBankAccount) -> str:
    emoji, label = _status(account)
    sleep = " 😴" if account.limit_sleeping else ""
    bank_label = BANK_LABELS.get(account.bank, account.bank or "—").replace("🏦 ", "")
    limit_type_label = LIMIT_TYPE_LABELS.get(account.limit_type, account.limit_type)
    return (
        f"{emoji} <b>Аккаунт #{account.id}</b> <code>{account.email}</code>\n"
        f"🏦 Банк: <b>{bank_label}</b>\n"
        f"📌 Статус: <b>{label}</b>\n\n"
        f"💰 Баланс: <b>{_fmt_balance(account.balance)} PLN</b>\n"
        f"🕒 Обновление баланса: <b>{_fmt_dt(account.balance_updated_at)}</b>\n\n"
        f"📊 Поступления за день: <b>{account.daily_used or 0}</b>\n"
        f"📈 Лимит: <b>{_fmt_limit(account.daily_limit)}</b>{sleep}\n"
        f"🧾 Тип лимита: <b>{limit_type_label}</b>\n\n"
        f"🌐 Прокси: <code>{account.proxy or '—'}</code>\n"
        f"📱 BLIK: <code>{account.blik_number or '—'}</code>"
    )


async def _render_list(callback: CallbackQuery, session: AsyncSession, lang: str) -> None:
    accounts = await accounts_repo.list_all(session)
    if accounts:
        lines = [t("admin_pay_title", lang), ""]
        lines += [_account_short_line(a) for a in accounts]
        text = "\n\n".join(lines)
    else:
        text = t("admin_pay_empty", lang)
    await callback.message.edit_text(
        text, reply_markup=payments_list_keyboard(accounts, lang)
    )


async def _render_account_cb(
    callback: CallbackQuery, session: AsyncSession, account_id: int, lang: str
) -> None:
    account = await accounts_repo.get(session, account_id)
    if account is None:
        await callback.answer("Аккаунт не найден", show_alert=True)
        await _render_list(callback, session, lang)
        return
    await callback.message.edit_text(
        _account_full_text(account),
        reply_markup=account_detail_keyboard(account, lang),
    )


async def _send_account(
    message: Message, session: AsyncSession, account_id: int, lang: str
) -> None:
    account = await accounts_repo.get(session, account_id)
    if account is None:
        await message.answer("Аккаунт не найден")
        return
    await message.answer(
        _account_full_text(account),
        reply_markup=account_detail_keyboard(account, lang),
    )


# ── List / detail ─────────────────────────────────────────────────────────────


@router.callback_query(
    F.data == "admin:settings:payments", F.message.chat.type == "private"
)
async def on_payments_open(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    await state.clear()
    await _render_list(callback, session, lang)
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:pay:acc:"), F.message.chat.type == "private"
)
async def on_account_open(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    account_id = int(callback.data.split(":")[-1])
    await _render_account_cb(callback, session, account_id, lang)
    await callback.answer()


# ── Activate / Deactivate ────────────────────────────────────────────────────


@router.callback_query(
    F.data.startswith("admin:pay:activate:"), F.message.chat.type == "private"
)
async def on_activate(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    mbanks_manager: MonitorManager | None = None,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    account_id = int(callback.data.split(":")[-1])
    await accounts_repo.set_active(session, account_id, True)
    await session.commit()
    if mbanks_manager is not None:
        await mbanks_manager.restart_account(account_id)
    await _render_account_cb(callback, session, account_id, lang)
    await callback.answer("▶️ Запущен")


@router.callback_query(
    F.data.startswith("admin:pay:deactivate:"), F.message.chat.type == "private"
)
async def on_deactivate(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    mbanks_manager: MonitorManager | None = None,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    account_id = int(callback.data.split(":")[-1])
    await accounts_repo.set_active(session, account_id, False)
    await session.commit()
    if mbanks_manager is not None:
        await mbanks_manager.remove_account(account_id)
    await _render_account_cb(callback, session, account_id, lang)
    await callback.answer("⏹ Остановлен")


# ── Rescan recent emails ─────────────────────────────────────────────────────


@router.callback_query(
    F.data.startswith("admin:pay:rescan:"), F.message.chat.type == "private"
)
async def on_rescan(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    mbanks_manager: MonitorManager | None = None,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    account_id = int(callback.data.split(":")[-1])
    # сбрасываем last_uid и активируем — монитор при следующем подключении
    # сделает initial backfill последних N писем (imap_initial_backfill_count)
    await accounts_repo.update(session, account_id, last_uid=0, is_active=True)
    await session.commit()
    if mbanks_manager is not None:
        await mbanks_manager.restart_account(account_id)
    await _render_account_cb(callback, session, account_id, lang)
    await callback.answer("🔁 Перечитываю последние письма…")


# ── Delete ────────────────────────────────────────────────────────────────────


@router.callback_query(
    F.data.startswith("admin:pay:delete:"), F.message.chat.type == "private"
)
async def on_delete_ask(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    account_id = int(callback.data.split(":")[-1])
    await callback.message.edit_text(
        f"⚠️ Вы уверены, что хотите удалить аккаунт <b>#{account_id}</b>?",
        reply_markup=delete_confirm_keyboard(account_id, lang),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:pay:delete_confirm:"), F.message.chat.type == "private"
)
async def on_delete_confirm(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    mbanks_manager: MonitorManager | None = None,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    account_id = int(callback.data.split(":")[-1])
    if mbanks_manager is not None:
        await mbanks_manager.remove_account(account_id)
    await accounts_repo.delete(session, account_id)
    await callback.answer("✅ Аккаунт удалён")
    await _render_list(callback, session, lang)


# ── Edit: proxy ───────────────────────────────────────────────────────────────


@router.callback_query(
    F.data.startswith("admin:pay:edit_proxy:"), F.message.chat.type == "private"
)
async def on_edit_proxy_start(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    account_id = int(callback.data.split(":")[-1])
    await state.set_state(MBankAccountState.edit_proxy)
    await state.update_data(account_id=account_id)
    await callback.message.edit_text(
        "🌐 Введите новый прокси в формате:\n"
        "<code>http://user:pass@host:port</code>\n"
        "<code>socks5://user:pass@host:port</code>"
    )
    await callback.answer()


@router.message(StateFilter(MBankAccountState.edit_proxy), F.chat.type == "private")
async def on_edit_proxy_input(
    message: Message,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    mbanks_manager: MonitorManager | None = None,
) -> None:
    lang = _resolve_lang(user, message)
    if await _deny_if_not_admin_msg(message, user, lang):
        await state.clear()
        return

    proxy = (message.text or "").strip()
    if not _PROXY_RE.match(proxy):
        await message.answer(
            "❌ Неверный формат. Пример:\n"
            "<code>http://user:pass@host:port</code>\n"
            "<code>socks5://user:pass@host:port</code>"
        )
        return

    data = await state.get_data()
    account_id = int(data["account_id"])
    await state.clear()
    await accounts_repo.update(session, account_id, proxy=proxy)
    await session.commit()
    if mbanks_manager is not None:
        await mbanks_manager.restart_account(account_id)
    await message.answer("✅ Прокси обновлён.")
    await _send_account(message, session, account_id, lang)


# ── Edit: BLIK ────────────────────────────────────────────────────────────────


@router.callback_query(
    F.data.startswith("admin:pay:edit_blik:"), F.message.chat.type == "private"
)
async def on_edit_blik_start(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    account_id = int(callback.data.split(":")[-1])
    await state.set_state(MBankAccountState.edit_blik)
    await state.update_data(account_id=account_id)
    await callback.message.edit_text("📱 Введите новый BLIK:")
    await callback.answer()


@router.message(StateFilter(MBankAccountState.edit_blik), F.chat.type == "private")
async def on_edit_blik_input(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)
    if await _deny_if_not_admin_msg(message, user, lang):
        await state.clear()
        return

    text = (message.text or "").strip()
    if not text.lstrip("+").isdigit():
        await message.answer("❌ Неверный формат BLIK")
        return

    data = await state.get_data()
    account_id = int(data["account_id"])
    await state.clear()
    await accounts_repo.update(session, account_id, blik_number=text)
    await message.answer("✅ BLIK номер обновлён.")
    await _send_account(message, session, account_id, lang)


# ── Edit: limit ───────────────────────────────────────────────────────────────


@router.callback_query(
    F.data.startswith("admin:pay:edit_limit:"), F.message.chat.type == "private"
)
async def on_edit_limit_start(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    account_id = int(callback.data.split(":")[-1])
    await state.set_state(MBankAccountState.edit_limit)
    await state.update_data(account_id=account_id)
    await callback.message.answer(
        "📊 <b>Установка дневного лимита</b>\n\n"
        "Введите число — лимит суммы поступлений за день (PLN):\n\n"
        "• <code>1000</code> — лимит 1000 PLN, учитываются <b>все</b> входящие транзакции\n"
        "• <code>1000**</code> — лимит 1000 PLN, учитываются <b>только транзакции, созданные ботом</b>\n"
        "• <code>0</code> — лимит 0 PLN (аккаунт сразу уходит в сон)\n\n"
        "Чтобы <b>снять лимит</b> — нажмите кнопку ниже.",
        reply_markup=remove_limit_keyboard(),
    )
    await callback.answer()


@router.message(StateFilter(MBankAccountState.edit_limit), F.chat.type == "private")
async def on_edit_limit_input(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)
    if await _deny_if_not_admin_msg(message, user, lang):
        await state.clear()
        return

    text = (message.text or "").strip()
    data = await state.get_data()
    account_id = int(data["account_id"])

    if text == REMOVE_LIMIT_BTN_TEXT:
        daily_limit: Decimal | None = None
        limit_type = "all"
    elif text.endswith("**"):
        raw = text[:-2]
        try:
            daily_limit = Decimal(raw)
            limit_type = "matched"
        except (InvalidOperation, ValueError):
            await message.answer("❌ Неверный формат. Пример: <code>1000**</code>")
            return
    else:
        try:
            daily_limit = Decimal(text)
            limit_type = "all"
        except (InvalidOperation, ValueError):
            await message.answer(
                "❌ Неверный формат.\n"
                "Примеры: <code>1000</code> / <code>1000**</code> / <code>0</code>"
            )
            return

    await state.clear()
    await accounts_repo.update(
        session,
        account_id,
        daily_limit=daily_limit,
        limit_type=limit_type,
        limit_sleeping=False,
        daily_used=Decimal("0.00"),
    )

    if daily_limit is None:
        lim_text = "снят (без лимита)"
    elif limit_type == "matched":
        lim_text = f"{daily_limit:f} PLN (только созданные ботом)"
    else:
        lim_text = f"{daily_limit:f} PLN (все транзакции)"

    await message.answer(
        f"✅ Лимит обновлён: {lim_text}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await _send_account(message, session, account_id, lang)


# ── Add account flow ──────────────────────────────────────────────────────────


@router.callback_query(F.data == "admin:pay:add", F.message.chat.type == "private")
async def on_add_start(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    await state.set_state(MBankAccountState.add_credentials)
    await callback.message.edit_text(
        "➕ <b>Добавление MBanks аккаунта</b>\n\n"
        "Введите данные в формате:\n"
        "<code>email:password:blik</code>\n\n"
        "Пример: <code>user@bank.com:pass123:+48123456789</code>"
    )
    await callback.answer()


@router.message(
    StateFilter(MBankAccountState.add_credentials), F.chat.type == "private"
)
async def on_add_credentials(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)
    if await _deny_if_not_admin_msg(message, user, lang):
        await state.clear()
        return

    text = (message.text or "").strip()
    parts = text.split(":", 2)
    if len(parts) != 3 or not all(parts):
        await message.answer(
            "❌ Неверный формат. Пример: <code>email:password:+48123456789</code>"
        )
        return
    email, password, blik = parts
    if " " in password or len(password) < 4:
        await message.answer("❌ Пароль слишком короткий или содержит пробелы")
        return
    if not blik.lstrip("+").isdigit():
        await message.answer("❌ Неверный формат BLIK")
        return

    existing = await accounts_repo.get_by_email(session, email)
    if existing is not None:
        await message.answer(
            f"❌ Аккаунт с email <code>{email}</code> уже существует (#{existing.id})"
        )
        return

    await state.update_data(email=email, password=password, blik=blik)
    await message.answer("🏦 Выберите банк:", reply_markup=bank_select_keyboard(lang))


@router.callback_query(
    F.data.startswith("admin:pay:bank:"), F.message.chat.type == "private"
)
async def on_add_bank_chosen(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    if await state.get_state() != MBankAccountState.add_credentials.state:
        await callback.answer()
        return

    bank = callback.data.split(":")[-1]
    await state.update_data(bank=bank)
    await state.set_state(MBankAccountState.add_proxy)
    await callback.message.edit_text(
        "🌐 Введите прокси в формате:\n"
        "<code>http://user:pass@host:port</code>\n"
        "<code>socks5://user:pass@host:port</code>\n\n"
        "Или нажмите «🚫 Без прокси»."
    )
    await callback.message.answer(
        "Если без прокси — нажмите кнопку ниже:",
        reply_markup=no_proxy_keyboard(),
    )
    await callback.answer()


@router.callback_query(
    F.data == "admin:pay:bank_custom", F.message.chat.type == "private"
)
async def on_add_bank_custom_start(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin_cb(callback, user, lang):
        return
    if await state.get_state() != MBankAccountState.add_credentials.state:
        await callback.answer()
        return
    await state.set_state(MBankAccountState.add_bank_custom)
    await callback.message.edit_text("✏️ Введите название банка:")
    await callback.answer()


@router.message(
    StateFilter(MBankAccountState.add_bank_custom), F.chat.type == "private"
)
async def on_add_bank_custom_input(
    message: Message, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)
    if await _deny_if_not_admin_msg(message, user, lang):
        await state.clear()
        return

    bank = (message.text or "").strip()
    if not bank:
        await message.answer("❌ Название не может быть пустым")
        return
    await state.update_data(bank=bank)
    await state.set_state(MBankAccountState.add_proxy)
    await message.answer(
        "🌐 Введите прокси в формате:\n"
        "<code>http://user:pass@host:port</code>\n"
        "<code>socks5://user:pass@host:port</code>\n\n"
        "Или нажмите «🚫 Без прокси».",
        reply_markup=no_proxy_keyboard(),
    )


@router.message(StateFilter(MBankAccountState.add_proxy), F.chat.type == "private")
async def on_add_proxy_input(
    message: Message,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    mbanks_manager: MonitorManager | None = None,
) -> None:
    lang = _resolve_lang(user, message)
    if await _deny_if_not_admin_msg(message, user, lang):
        await state.clear()
        return

    proxy_text = (message.text or "").strip()
    if proxy_text == NO_PROXY_BTN_TEXT:
        proxy: str | None = None
    elif _PROXY_RE.match(proxy_text):
        proxy = proxy_text
    else:
        await message.answer(
            "❌ Неверный формат. Пример:\n"
            "<code>http://user:pass@host:port</code>\n"
            "<code>socks5://user:pass@host:port</code>"
        )
        return

    data = await state.get_data()
    await state.clear()

    settings = get_settings()
    account = await accounts_repo.create(
        session,
        email=data["email"],
        password=data["password"],
        bank=data["bank"],
        blik_number=data["blik"],
        proxy=proxy,
        daily_limit=settings.default_bank_daily_limit,
        limit_type=settings.default_bank_limit_type,
        is_active=True,
    )
    await session.commit()
    if mbanks_manager is not None:
        await mbanks_manager.add_account(account.id)

    await message.answer(
        f"✅ Аккаунт #{account.id} создан. Загружаю детали...",
        reply_markup=ReplyKeyboardRemove(),
    )
    await _send_account(message, session, account.id, lang)
