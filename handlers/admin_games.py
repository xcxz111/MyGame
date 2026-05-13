"""Создание и просмотр игр (Admin → 🎯 Игры)."""

from __future__ import annotations

import asyncio
import html
import logging
import re
from datetime import date, datetime, time as dt_time
from decimal import Decimal, InvalidOperation

from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.models.game import Game, GameStatus, GameType
from database.repositories import app_chat_allowed_topics as allowed_topics_repo
from database.repositories import app_chats as app_chats_repo
from database.repositories import forum_topics as forum_topics_repo
from database.repositories import games as games_repo
from database.repositories import prizes as prizes_repo
from keyboards import (
    admin_game_cancel_keyboard,
    admin_game_chat_pick_keyboard,
    admin_game_confirm_keyboard,
    admin_game_detail_keyboard,
    admin_game_forum_topic_keyboard,
    admin_games_keyboard,
    admin_games_list_keyboard,
)
from locales.texts import get_lang, t
from permissions import is_admin
from services.forum_topic_allowlist import filter_topic_rows, general_play_allowed
from services.games.forum_thread import (
    format_forum_topic_display_label,
    pin_chat_message_in_forum,
    thread_kw,
)
from settings import get_settings
from states import AdminCreateGameState

logger = logging.getLogger(__name__)
router = Router(name="admin_games")


# ── helpers: locale / access ──────────────────────────────────────────────────


def _resolve_lang(user: User, callback_or_message) -> str:
    fallback = (
        callback_or_message.from_user.language_code
        if getattr(callback_or_message, "from_user", None)
        else None
    )
    return user.language_code or get_lang(fallback)


async def _deny_if_not_admin(
    callback: CallbackQuery, user: User, lang: str
) -> bool:
    if is_admin(user, get_settings()):
        return False
    await callback.answer(t("admin_no_access", lang), show_alert=True)
    return True


async def _resolve_title(bot: Bot, chat_id: int) -> str | None:
    try:
        chat = await bot.get_chat(chat_id)
    except Exception as exc:
        logger.debug("get_chat(%s) failed: %s", chat_id, exc)
        return None
    return chat.title or chat.full_name or None


async def _resolve_chat_label(
    bot: Bot, session: AsyncSession, chat_id: int, lang: str
) -> str | None:
    row = await app_chats_repo.get_by_chat_id(session, chat_id)
    if row is not None:
        s = row.button_title_for(lang)
        if s:
            return s
    return await _resolve_title(bot, chat_id)


async def _present_after_chat_selected(
    *,
    callback: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    bot: Bot,
    lang: str,
    chat_id: int,
) -> None:
    """После выбора чата: если форум — выбор темы, иначе сразу участники."""
    try:
        chat = await bot.get_chat(chat_id)
        is_forum = bool(getattr(chat, "is_forum", None))
    except Exception:
        is_forum = False
    if not is_forum:
        await state.set_state(AdminCreateGameState.waiting_participants)
        await state.update_data(
            chat_id=chat_id,
            message_thread_id=None,
            forum_topic_title=None,
        )
        await callback.message.edit_text(
            t("admin_game_enter_participants", lang),
            reply_markup=admin_game_cancel_keyboard(lang),
        )
        return
    topics = await forum_topics_repo.list_for_chat(session, chat_id)
    rows = [(t.message_thread_id, t.name) for t in topics]
    allowed = await allowed_topics_repo.effective_allowed_public_threads(session, chat_id)
    rows = filter_topic_rows(rows, allowed)
    show_general = general_play_allowed(allowed)
    await state.set_state(AdminCreateGameState.waiting_forum_topic)
    await state.update_data(chat_id=chat_id)
    body = (
        t("admin_game_pick_forum_topic", lang)
        if rows
        else t("admin_game_pick_forum_topic_empty", lang)
    )
    await callback.message.edit_text(
        body,
        reply_markup=admin_game_forum_topic_keyboard(
            lang, rows, show_general_option=show_general
        ),
    )


# ── helpers: format ───────────────────────────────────────────────────────────


def _fmt_money(value: Decimal | float | int) -> str:
    d = Decimal(value) if not isinstance(value, Decimal) else value
    s = f"{d:.2f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


def _type_label(game_type: str, lang: str) -> str:
    if game_type == GameType.ANY:
        return t("admin_game_type_any", lang)
    if game_type == GameType.DICE:
        return t("admin_game_type_dice", lang)
    if game_type == GameType.BOWLING:
        return t("admin_game_type_bowling", lang)
    if game_type == GameType.DARTS:
        return t("admin_game_type_darts", lang)
    return game_type


def _status_label(status: str, lang: str) -> str:
    return t(f"admin_game_status_{status}", lang)


# ── helpers: parsing ──────────────────────────────────────────────────────────


def _parse_participants(text: str) -> tuple[int, int] | None:
    line = (text or "").strip().replace("-", "/")
    parts = [p.strip() for p in line.split("/") if p.strip()]
    if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
        return None
    lo, hi = int(parts[0]), int(parts[1])
    if lo < 1 or hi < 1 or lo > hi:
        return None
    return lo, hi


def _parse_prizes(text: str) -> list[Decimal] | None:
    parts = [p.strip().replace(",", ".") for p in (text or "").splitlines() if p.strip()]
    if not parts:
        return None
    result: list[Decimal] = []
    for raw in parts:
        try:
            value = Decimal(raw).quantize(Decimal("0.01"))
        except InvalidOperation:
            return None
        if value <= 0:
            return None
        result.append(value)
    return result


def _parse_dmy(text: str) -> date | None:
    raw = (text or "").strip()
    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d.%m.%y", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def _parse_min_topup(text: str) -> tuple[Decimal, date | None] | None:
    raw = (text or "").strip()
    if not raw:
        return None
    if ":" in raw:
        left, right = raw.split(":", 1)
        amount_raw = left.strip().replace(",", ".")
        since = _parse_dmy(right.strip())
        if since is None:
            return None
    else:
        amount_raw = raw.replace(",", ".")
        since = None
    try:
        value = Decimal(amount_raw).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None
    if value < 0:
        return None
    if value == 0:
        return Decimal("0.00"), None
    return value, since


def _parse_entry_fee(text: str) -> Decimal | None:
    raw = (text or "").strip().replace(",", ".")
    try:
        value = Decimal(raw).quantize(Decimal("0.01"))
    except InvalidOperation:
        return None
    if value < 0:
        return None
    return value


def _parse_datetime(text: str) -> datetime | None:
    raw = (text or "").strip()
    if not raw:
        return None
    for fmt in ("%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M", "%d/%m/%Y %H:%M"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    m = re.match(r"^(\d{1,2}):(\d{2})$", raw)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if 0 <= h <= 23 and 0 <= mi <= 59:
            return datetime.combine(datetime.now().date(), dt_time(hour=h, minute=mi))
    return None


# ── render preview ────────────────────────────────────────────────────────────


def _render_preview(data: dict, *, lang: str, chat_title: str | None) -> str:
    game_type = data.get("game_type") or GameType.ANY
    min_p = int(data.get("min_participants") or 2)
    max_p = int(data.get("max_participants") or 50)
    prizes: list[Decimal] = data.get("prizes") or []
    min_topup: Decimal = data.get("min_topup") or Decimal("0.00")
    min_topup_since: date | None = data.get("min_topup_since")
    entry_fee: Decimal = data.get("entry_fee") or Decimal("0.00")
    is_paid: bool = bool(data.get("is_paid"))
    start_time: datetime = data.get("start_time")

    chat_label = html.escape(chat_title) if chat_title else str(
        data.get("chat_id") or "—"
    )

    lines: list[str] = [t("admin_game_preview_title", lang), ""]
    lines.append(t("admin_game_preview_chat", lang).format(chat=chat_label))
    mtid = data.get("message_thread_id")
    if mtid is not None:
        ft = data.get("forum_topic_title")
        topic_label = html.escape(
            format_forum_topic_display_label(lang, message_thread_id=int(mtid), name=ft)
        )
        lines.append(
            t("admin_game_preview_forum_topic", lang).format(topic=topic_label)
        )
    lines.append(
        t("admin_game_preview_type", lang).format(type=_type_label(game_type, lang))
    )
    lines.append(
        t("admin_game_preview_participants", lang).format(min=min_p, max=max_p)
    )
    if is_paid and entry_fee > 0:
        lines.append(
            t("admin_game_preview_pay_paid", lang).format(fee=_fmt_money(entry_fee))
        )
    else:
        lines.append(t("admin_game_preview_pay_free", lang))
    if min_topup > 0:
        if min_topup_since:
            lines.append(
                t("admin_game_preview_min_topup_period", lang).format(
                    n=_fmt_money(min_topup),
                    since=min_topup_since.strftime("%d.%m.%Y"),
                )
            )
        else:
            lines.append(
                t("admin_game_preview_min_topup_alltime", lang).format(
                    n=_fmt_money(min_topup)
                )
            )
    else:
        lines.append(t("admin_game_preview_min_topup_none", lang))
    lines.append("")
    lines.append(t("admin_game_preview_prizes", lang))
    for i, p in enumerate(prizes, 1):
        lines.append(f"  {i}. {_fmt_money(p)} PLN")
    lines.append("")
    lines.append(
        t("admin_game_preview_datetime", lang).format(
            datetime=start_time.strftime("%d.%m.%Y %H:%M") if start_time else "—"
        )
    )
    return "\n".join(lines)


# ── render announcement ───────────────────────────────────────────────────────


def _render_announcement(
    *,
    lang: str,
    chat_title: str | None,
    start_time: datetime,
    min_participants: int,
    max_participants: int,
    is_paid: bool,
    entry_fee: Decimal,
    min_topup: Decimal,
    min_topup_since: date | None,
    prizes: list[Decimal],
    bot_username: str | None,
) -> str:
    safe_chat = html.escape(chat_title or "—")
    lines: list[str] = [
        t("game_announce_title", lang).format(chat=safe_chat),
        t("game_announce_date", lang).format(
            date=start_time.strftime("%d.%m.%Y %H:%M")
        ),
        t("game_announce_participants_range", lang).format(
            min=min_participants, max=max_participants
        ),
        "",
        t("game_announce_conditions", lang),
    ]
    if is_paid and entry_fee > 0:
        lines.append(
            t("game_announce_cond_pay_paid", lang).format(fee=_fmt_money(entry_fee))
        )
    else:
        lines.append(t("game_announce_cond_pay_free", lang))
    if min_topup > 0:
        if min_topup_since:
            lines.append(
                t("game_announce_cond_min_topup_period", lang).format(
                    n=_fmt_money(min_topup),
                    since=min_topup_since.strftime("%d.%m.%Y"),
                )
            )
        else:
            lines.append(
                t("game_announce_cond_min_topup_alltime", lang).format(
                    n=_fmt_money(min_topup)
                )
            )
    elif not (is_paid and entry_fee > 0):
        lines.append(t("game_announce_cond_none", lang))
    lines.append("")
    lines.append(t("game_announce_prizes", lang))
    for i, p in enumerate(prizes, 1):
        lines.append(f"{i}. {_fmt_money(p)} PLN")
    lines.append("")
    if bot_username:
        bot_link = f'<a href="https://t.me/{bot_username}">@{html.escape(bot_username)}</a>'
        lines.append(t("game_announce_signup_link", lang).format(bot_link=bot_link))
    else:
        lines.append(t("game_announce_signup_no_link", lang))
    return "\n".join(lines)


def _signup_keyboard(language_code: str, game_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("game_btn_signup", language_code),
            callback_data=f"game:signup:{game_id}",
        )
    )
    return builder.as_markup()


# ── render games menu (главное меню «🎯 Игры») ────────────────────────────────


@router.callback_query(F.data == "admin:games", F.message.chat.type == "private")
async def on_admin_games_menu(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    await state.clear()
    await callback.message.edit_text(
        t("admin_games_title", lang),
        reply_markup=admin_games_keyboard(lang),
    )
    await callback.answer()


# ── step 0: пользователь нажал «Создать игру» ─────────────────────────────────


@router.callback_query(
    F.data == "admin:games:create", F.message.chat.type == "private"
)
async def on_admin_games_create(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return

    chats = await app_chats_repo.get_all(session)
    if not chats:
        await callback.answer(t("admin_game_no_chats", lang), show_alert=True)
        return

    if len(chats) == 1:
        await _present_after_chat_selected(
            callback=callback,
            session=session,
            state=state,
            bot=bot,
            lang=lang,
            chat_id=int(chats[0].chat_id),
        )
        await callback.answer()
        return

    items = [
        (c, (await _resolve_chat_label(bot, session, c.chat_id, lang)) or str(c.chat_id))
        for c in chats
    ]
    await state.set_state(AdminCreateGameState.waiting_chat)
    await callback.message.edit_text(
        t("admin_game_pick_chat", lang),
        reply_markup=admin_game_chat_pick_keyboard(lang, items),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:games:create:chat:"),
    F.message.chat.type == "private",
)
async def on_admin_games_create_chat_picked(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    try:
        chat_id = int(callback.data.split(":")[-1])
    except (TypeError, ValueError):
        await callback.answer()
        return
    await _present_after_chat_selected(
        callback=callback,
        session=session,
        state=state,
        bot=bot,
        lang=lang,
        chat_id=chat_id,
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:games:create:forum:"),
    StateFilter(AdminCreateGameState.waiting_forum_topic),
    F.message.chat.type == "private",
)
async def on_admin_games_create_forum_topic(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    raw = callback.data or ""
    if not raw.startswith("admin:games:create:forum:"):
        await callback.answer()
        return
    suffix = raw.removeprefix("admin:games:create:forum:")
    data = await state.get_data()
    chat_id = int(data.get("chat_id") or 0)
    if suffix == "reload":
        if chat_id <= 0:
            await callback.answer(t("admin_game_forum_reload_lost", lang), show_alert=True)
            return
        await _present_after_chat_selected(
            callback=callback,
            session=session,
            state=state,
            bot=callback.bot,
            lang=lang,
            chat_id=chat_id,
        )
        await callback.answer(t("admin_game_forum_reload_toast", lang))
        return
    if suffix == "skip":
        if not await allowed_topics_repo.is_allowed_public(session, chat_id, None):
            await callback.answer(t("admin_game_topic_forbidden", lang), show_alert=True)
            return
        await state.update_data(message_thread_id=None, forum_topic_title=None)
    else:
        try:
            tid = int(suffix)
        except ValueError:
            await callback.answer()
            return
        if not await allowed_topics_repo.is_allowed_public(session, chat_id, tid):
            await callback.answer(t("admin_game_topic_forbidden", lang), show_alert=True)
            return
        title = None
        for row in await forum_topics_repo.list_for_chat(session, chat_id):
            if row.message_thread_id == tid:
                title = row.name
                break
        if not title:
            title = f"#{tid}"
        await state.update_data(message_thread_id=tid, forum_topic_title=title)
    await state.set_state(AdminCreateGameState.waiting_participants)
    await callback.message.edit_text(
        t("admin_game_enter_participants", lang),
        reply_markup=admin_game_cancel_keyboard(lang),
    )
    await callback.answer()


# ── steps 1-5: text input handlers ────────────────────────────────────────────


@router.message(
    StateFilter(AdminCreateGameState.waiting_participants), F.chat.type == "private"
)
async def on_step_participants(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)
    parsed = _parse_participants(message.text or "")
    if not parsed:
        await message.answer(t("admin_game_invalid_participants", lang))
        return
    lo, hi = parsed
    await state.update_data(min_participants=lo, max_participants=hi)
    await state.set_state(AdminCreateGameState.waiting_prizes)
    await message.answer(
        t("admin_game_enter_prizes", lang),
        reply_markup=admin_game_cancel_keyboard(lang),
    )


@router.message(
    StateFilter(AdminCreateGameState.waiting_prizes), F.chat.type == "private"
)
async def on_step_prizes(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)
    prizes = _parse_prizes(message.text or "")
    if prizes is None:
        await message.answer(t("admin_game_invalid_prizes", lang))
        return
    data = await state.get_data()
    max_p = int(data.get("max_participants") or 0)
    if max_p and len(prizes) > max_p:
        await message.answer(
            t("admin_game_prizes_more_than_max", lang).format(n=len(prizes), max=max_p)
        )
        return
    # Decimal не сериализуется в JSON-стейтах — храним строкой
    await state.update_data(prizes=[str(p) for p in prizes])
    await state.set_state(AdminCreateGameState.waiting_min_topup)
    await message.answer(
        t("admin_game_enter_min_topup", lang),
        reply_markup=admin_game_cancel_keyboard(lang),
    )


@router.message(
    StateFilter(AdminCreateGameState.waiting_min_topup), F.chat.type == "private"
)
async def on_step_min_topup(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)
    parsed = _parse_min_topup(message.text or "")
    if parsed is None:
        await message.answer(t("admin_game_invalid_min_topup", lang))
        return
    amount, since = parsed
    await state.update_data(
        min_topup=str(amount),
        min_topup_since=since.isoformat() if since else None,
    )
    await state.set_state(AdminCreateGameState.waiting_entry_fee)
    await message.answer(
        t("admin_game_enter_entry_fee", lang),
        reply_markup=admin_game_cancel_keyboard(lang),
    )


@router.message(
    StateFilter(AdminCreateGameState.waiting_entry_fee), F.chat.type == "private"
)
async def on_step_entry_fee(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, message)
    fee = _parse_entry_fee(message.text or "")
    if fee is None:
        await message.answer(t("admin_game_invalid_entry_fee", lang))
        return
    await state.update_data(entry_fee=str(fee), is_paid=bool(fee > 0))
    await state.set_state(AdminCreateGameState.waiting_datetime)
    await message.answer(
        t("admin_game_enter_datetime", lang),
        reply_markup=admin_game_cancel_keyboard(lang),
    )


@router.message(
    StateFilter(AdminCreateGameState.waiting_datetime), F.chat.type == "private"
)
async def on_step_datetime(
    message: Message, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _resolve_lang(user, message)
    start = _parse_datetime(message.text or "")
    if start is None:
        await message.answer(t("admin_game_invalid_datetime", lang))
        return
    if start <= datetime.now():
        await message.answer(t("admin_game_datetime_in_past", lang))
        return

    data = await state.get_data()
    min_topup_since_iso = data.get("min_topup_since")
    if min_topup_since_iso:
        since = date.fromisoformat(min_topup_since_iso)
        if since > start.date():
            await message.answer(t("admin_game_topup_since_after_start", lang))
            return

    # сохраняем дату в state и показываем превью
    await state.update_data(start_time=start.isoformat())
    await state.set_state(AdminCreateGameState.waiting_confirm)

    preview_data = await _materialize_state(state)
    chat_title = await _resolve_chat_label(
        bot, session, int(preview_data.get("chat_id") or 0), lang
    )
    preview = _render_preview(preview_data, lang=lang, chat_title=chat_title)
    await message.answer(
        preview, reply_markup=admin_game_confirm_keyboard(lang)
    )


async def _materialize_state(state: FSMContext) -> dict:
    """Превратить плоские JSON-значения из FSM обратно в Decimal/date/datetime."""
    raw = await state.get_data()
    out = dict(raw)
    if raw.get("prizes") is not None:
        out["prizes"] = [Decimal(p) for p in raw["prizes"]]
    if raw.get("min_topup") is not None:
        out["min_topup"] = Decimal(raw["min_topup"])
    if raw.get("min_topup_since"):
        out["min_topup_since"] = date.fromisoformat(raw["min_topup_since"])
    else:
        out["min_topup_since"] = None
    if raw.get("entry_fee") is not None:
        out["entry_fee"] = Decimal(raw["entry_fee"])
    if raw.get("start_time"):
        out["start_time"] = datetime.fromisoformat(raw["start_time"])
    mt = raw.get("message_thread_id")
    if mt is not None:
        try:
            out["message_thread_id"] = int(mt)
        except (TypeError, ValueError):
            out["message_thread_id"] = None
    else:
        out["message_thread_id"] = None
    return out


# ── confirm / cancel ──────────────────────────────────────────────────────────


@router.callback_query(
    F.data == "admin:games:create:cancel", F.message.chat.type == "private"
)
async def on_admin_games_create_cancel(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    await state.clear()
    await callback.message.edit_text(
        t("admin_games_title", lang) + "\n\n" + t("admin_game_create_cancelled", lang),
        reply_markup=admin_games_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(
    F.data == "admin:games:create:confirm",
    StateFilter(AdminCreateGameState.waiting_confirm),
    F.message.chat.type == "private",
)
async def on_admin_games_create_confirm(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    state: FSMContext,
    bot: Bot,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return

    # сразу убираем кнопки, чтобы исключить двойное создание
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    data = await _materialize_state(state)
    game_type = GameType.ANY
    chat_id = int(data.get("chat_id") or 0)
    start_time: datetime = data.get("start_time")
    prizes: list[Decimal] = data.get("prizes") or []
    min_p = int(data.get("min_participants") or 2)
    max_p = int(data.get("max_participants") or 50)
    entry_fee: Decimal = data.get("entry_fee") or Decimal("0.00")
    is_paid: bool = bool(data.get("is_paid"))
    min_topup: Decimal = data.get("min_topup") or Decimal("0.00")
    min_topup_since: date | None = data.get("min_topup_since")
    message_thread_id: int | None = data.get("message_thread_id")

    prefix = t("admin_game_name_prefix", lang)
    if prefix == "admin_game_name_prefix":
        prefix = "Game"
    name = f"{prefix} {start_time.strftime('%d.%m.%Y %H:%M')}"

    game = await games_repo.create(
        session,
        name=name,
        game_type=game_type,
        chat_id=chat_id,
        start_time=start_time,
        min_participants=min_p,
        max_participants=max_p,
        prize_places=len(prizes),
        is_paid=is_paid,
        entry_fee=entry_fee,
        min_topup=min_topup,
        min_topup_since=min_topup_since,
        message_thread_id=message_thread_id,
    )
    await prizes_repo.bulk_add(session, game_id=game.id, amounts=prizes)
    await session.commit()

    # Анонс в целевой чат
    chat_title = await _resolve_chat_label(bot, session, chat_id, lang)
    try:
        me = await bot.get_me()
        bot_username = (getattr(me, "username", None) or "").strip() or None
    except Exception:
        bot_username = None

    announce_text = _render_announcement(
        lang=lang,
        chat_title=chat_title,
        start_time=start_time,
        min_participants=min_p,
        max_participants=max_p,
        is_paid=is_paid,
        entry_fee=entry_fee,
        min_topup=min_topup,
        min_topup_since=min_topup_since,
        prizes=prizes,
        bot_username=bot_username,
    )

    tw = thread_kw(message_thread_id)
    sent_topic = None
    sent_general = None
    try:
        sent_topic = await bot.send_message(
            chat_id=chat_id,
            text=announce_text,
            parse_mode=ParseMode.HTML,
            **tw,
        )
    except TelegramBadRequest as exc:
        logger.warning("announce: HTML failed (%s), retrying plain", exc)
        try:
            sent_topic = await bot.send_message(
                chat_id=chat_id, text=announce_text, **tw
            )
        except Exception as exc2:
            logger.exception("announce: send_message failed: %s", exc2)
    except Exception as exc:
        logger.exception("announce: send_message failed: %s", exc)

    if sent_topic is not None and message_thread_id is not None:
        try:
            sent_general = await bot.send_message(
                chat_id=chat_id,
                text=announce_text,
                parse_mode=ParseMode.HTML,
            )
        except TelegramBadRequest as exc:
            logger.warning("announce general: HTML failed (%s), retrying plain", exc)
            try:
                sent_general = await bot.send_message(
                    chat_id=chat_id, text=announce_text
                )
            except Exception as exc2:
                logger.exception("announce general send: %s", exc2)
        except Exception as exc:
            logger.exception("announce general send: %s", exc)
        if sent_general is not None:
            try:
                await pin_chat_message_in_forum(
                    bot,
                    chat_id=chat_id,
                    message_id=sent_general.message_id,
                    message_thread_id=None,
                )
            except Exception as exc:
                logger.warning("announce general: pin failed: %s", exc)

    if sent_topic is not None:
        if message_thread_id is not None:
            await games_repo.set_announcement_messages(
                session,
                game.id,
                topic_message_id=sent_topic.message_id,
                general_message_id=sent_general.message_id if sent_general else None,
            )
        else:
            await games_repo.set_announcement_message(
                session, game.id, sent_topic.message_id
            )
        await session.commit()
        try:
            await pin_chat_message_in_forum(
                bot,
                chat_id=chat_id,
                message_id=sent_topic.message_id,
                message_thread_id=message_thread_id,
            )
        except Exception as exc:
            logger.warning("announce: pin failed: %s", exc)

    # Рассылка в ЛС (фоновая задача, не блокирует ответ админу)
    asyncio.create_task(
        _broadcast_announcement(bot=bot, text=announce_text, game_id=game.id)
    )

    await state.clear()
    await callback.message.answer(
        t("admin_game_created", lang).format(id=game.id),
        reply_markup=admin_games_keyboard(lang),
    )
    await callback.answer()


async def _broadcast_announcement(
    *, bot: Bot, text: str, game_id: int
) -> None:
    """Рассылка анонса в ЛС всем пользователям бота с кнопкой «Записаться»."""
    from database import get_session_maker

    sm = get_session_maker()
    try:
        async with sm() as s:
            res = await s.execute(select(User.user_id, User.language_code))
            users = list(res.all())
    except Exception as exc:
        logger.exception("broadcast: fetch users failed: %s", exc)
        return

    ok = fail = 0
    for uid, ulang in users:
        lang_for_user = ulang or "ru"
        try:
            await bot.send_message(
                chat_id=int(uid),
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=_signup_keyboard(lang_for_user, game_id),
            )
            ok += 1
        except Exception:
            fail += 1
        # лёгкий троттлинг (Telegram limit ~30 msg/s, держим 20)
        await asyncio.sleep(0.05)
    logger.info("Game #%s announcement: DM ok=%s fail=%s total=%s",
                game_id, ok, fail, len(users))


# ── lists ─────────────────────────────────────────────────────────────────────


@router.callback_query(
    F.data == "admin:games:active", F.message.chat.type == "private"
)
async def on_admin_games_active(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    games = await games_repo.get_current(session)
    if not games:
        await callback.message.edit_text(
            t("admin_games_active_title", lang)
            + "\n\n"
            + t("admin_games_empty_active", lang),
            reply_markup=admin_games_keyboard(lang),
        )
        await callback.answer()
        return
    await callback.message.edit_text(
        t("admin_games_active_title", lang),
        reply_markup=admin_games_list_keyboard(
            lang, games, back_to="admin:games:active:back"
        ),
    )
    await callback.answer()


@router.callback_query(
    F.data == "admin:games:past", F.message.chat.type == "private"
)
async def on_admin_games_past(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    games = await games_repo.get_finished(session)
    if not games:
        await callback.message.edit_text(
            t("admin_games_past_title", lang)
            + "\n\n"
            + t("admin_games_empty_past", lang),
            reply_markup=admin_games_keyboard(lang),
        )
        await callback.answer()
        return
    await callback.message.edit_text(
        t("admin_games_past_title", lang),
        reply_markup=admin_games_list_keyboard(
            lang, games, back_to="admin:games:past:back"
        ),
    )
    await callback.answer()


# «← Назад» из списка возвращает в меню игр
@router.callback_query(
    F.data.in_({"admin:games:active:back", "admin:games:past:back"}),
    F.message.chat.type == "private",
)
async def on_admin_games_list_back(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    await callback.message.edit_text(
        t("admin_games_title", lang),
        reply_markup=admin_games_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:games:view:"), F.message.chat.type == "private"
)
async def on_admin_games_view(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    try:
        game_id = int(callback.data.split(":")[-1])
    except (TypeError, ValueError):
        await callback.answer()
        return
    game: Game | None = await games_repo.get(session, game_id)
    if game is None:
        await callback.answer()
        return
    prizes = await prizes_repo.for_game(session, game_id)
    participants_count = await games_repo.count_participants(session, game_id)
    chat_title = await _resolve_chat_label(bot, session, game.chat_id, lang)

    lines = [t("admin_game_detail_title", lang).format(id=game.id), ""]
    lines.append(
        t("admin_game_preview_chat", lang).format(chat=html.escape(chat_title or str(game.chat_id)))
    )
    if game.message_thread_id is not None:
        topic_title = None
        for row in await forum_topics_repo.list_for_chat(session, game.chat_id):
            if row.message_thread_id == game.message_thread_id:
                topic_title = row.name
                break
        topic_label = html.escape(
            format_forum_topic_display_label(
                lang,
                message_thread_id=int(game.message_thread_id),
                name=topic_title,
            )
        )
        lines.append(
            t("admin_game_preview_forum_topic", lang).format(topic=topic_label)
        )
    lines.append(
        t("admin_game_preview_type", lang).format(type=_type_label(game.game_type, lang))
    )
    lines.append(
        t("admin_game_detail_status", lang).format(
            status=_status_label(game.status, lang)
        )
    )
    lines.append(
        t("admin_game_preview_participants", lang).format(
            min=int(game.min_participants), max=int(game.max_participants)
        )
    )
    lines.append(
        t("admin_game_detail_participants_count", lang).format(
            count=participants_count,
            max=int(game.max_participants),
            min=int(game.min_participants),
        )
    )
    if bool(game.is_paid) and game.entry_fee > 0:
        lines.append(
            t("admin_game_preview_pay_paid", lang).format(fee=_fmt_money(game.entry_fee))
        )
    else:
        lines.append(t("admin_game_preview_pay_free", lang))
    if game.min_topup > 0:
        if game.min_topup_since:
            lines.append(
                t("admin_game_preview_min_topup_period", lang).format(
                    n=_fmt_money(game.min_topup),
                    since=game.min_topup_since.strftime("%d.%m.%Y"),
                )
            )
        else:
            lines.append(
                t("admin_game_preview_min_topup_alltime", lang).format(
                    n=_fmt_money(game.min_topup)
                )
            )
    else:
        lines.append(t("admin_game_preview_min_topup_none", lang))
    lines.append("")
    lines.append(t("admin_game_preview_prizes", lang))
    for p in prizes:
        lines.append(f"  {p.place_number}. {_fmt_money(p.amount)} PLN")
    lines.append("")
    lines.append(
        t("admin_game_preview_datetime", lang).format(
            datetime=game.start_time.strftime("%d.%m.%Y %H:%M")
        )
    )

    back_target = (
        "admin:games:past"
        if game.status in (GameStatus.FINISHED, GameStatus.CANCELLED)
        else "admin:games:active"
    )
    await callback.message.edit_text(
        "\n".join(lines),
        reply_markup=admin_game_detail_keyboard(lang, game, back_to=back_target),
    )
    await callback.answer()
