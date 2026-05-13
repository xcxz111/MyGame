"""Управление подключёнными чатами (Bot settings → Chats)."""

from __future__ import annotations

import html
import logging

from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.models.app_chat_allowed_topic import GENERAL_THREAD_DB
from database.repositories import app_chat_allowed_topics as allowed_topics_repo
from database.repositories import app_chats as app_chats_repo
from database.repositories import forum_topics as forum_topics_repo
from aiogram.exceptions import TelegramBadRequest

from keyboards import (
    admin_chats_delete_confirm_keyboard,
    admin_chats_delete_list_keyboard,
    admin_chats_fsm_nav_keyboard,
    admin_chats_keyboard,
    admin_chats_topic_whitelist_keyboard,
    admin_chats_topics_chat_list_keyboard,
)
from services.games.forum_thread import format_forum_topic_display_label
from locales.texts import get_lang, t
from permissions import is_admin
from settings import get_settings
from states import AdminChatsState

logger = logging.getLogger(__name__)
router = Router(name="admin_chats")


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


async def _list_line_title(bot: Bot, chat, lang: str) -> str:
    stored = chat.button_title_for(lang)
    if stored:
        return stored
    return (await _resolve_title(bot, chat.chat_id)) or "—"


async def _try_create_invite_link(bot: Bot, chat_id: int) -> tuple[str | None, bool]:
    """Создать invite-ссылку. Возвращает (url, ok). При ok=False ссылку сохранить не удалось."""
    try:
        inv = await bot.create_chat_invite_link(chat_id=chat_id)
        return inv.invite_link, True
    except TelegramBadRequest as exc:
        logger.info("create_chat_invite_link %s: %s", chat_id, exc)
        try:
            url = await bot.export_chat_invite_link(chat_id=chat_id)
            return url, True
        except TelegramBadRequest as exc2:
            logger.warning("export_chat_invite_link %s: %s", chat_id, exc2)
            return None, False


async def _build_chats_text_and_kb(
    bot: Bot, session: AsyncSession, lang: str
) -> tuple[str, object]:
    chats = await app_chats_repo.get_all(session)
    if not chats:
        return t("admin_chats_title", lang) + "\n\n" + t(
            "admin_chats_empty", lang
        ), admin_chats_keyboard(lang)
    lines = [t("admin_chats_title", lang), ""]
    for chat in chats:
        title = await _list_line_title(bot, chat, lang)
        safe_title = html.escape(title) if title else "—"
        lines.append(
            t("admin_chats_list_line", lang).format(
                chat_id=chat.chat_id, title=safe_title
            )
        )
    return "\n".join(lines), admin_chats_keyboard(lang)


@router.callback_query(
    F.data == "admin:settings:chats", F.message.chat.type == "private"
)
async def on_admin_chats(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    await state.clear()
    text, kb = await _build_chats_text_and_kb(bot, session, lang)
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()


# ── Добавление ────────────────────────────────────────────────────────────────


@router.callback_query(F.data == "admin:chats:add", F.message.chat.type == "private")
async def on_admin_chats_add(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    await state.set_state(AdminChatsState.waiting_chat_button_title)
    await callback.message.edit_text(
        t("admin_chats_enter_button_title", lang),
        reply_markup=admin_chats_fsm_nav_keyboard(lang),
    )
    await callback.answer()


@router.message(
    StateFilter(AdminChatsState.waiting_chat_button_title), F.chat.type == "private"
)
async def on_admin_chats_button_title_input(
    message: Message,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _resolve_lang(user, message)
    title = (message.text or "").strip()
    if not title or len(title) > 200:
        await message.answer(
            t("admin_chats_invalid_button_title", lang),
            reply_markup=admin_chats_fsm_nav_keyboard(lang),
        )
        return
    await state.update_data(button_title=title)
    await state.set_state(AdminChatsState.waiting_chat_id)
    await message.answer(
        t("admin_chats_enter_chat_id", lang),
        reply_markup=admin_chats_fsm_nav_keyboard(lang),
    )


@router.message(StateFilter(AdminChatsState.waiting_chat_id), F.chat.type == "private")
async def on_admin_chats_chat_id_input(
    message: Message,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _resolve_lang(user, message)
    raw = (message.text or "").strip()
    try:
        chat_id = int(raw)
    except ValueError:
        await message.answer(
            t("admin_chats_invalid_id", lang),
            reply_markup=admin_chats_fsm_nav_keyboard(lang),
        )
        return
    if chat_id >= 0:
        await message.answer(
            t("admin_chats_invalid_id", lang),
            reply_markup=admin_chats_fsm_nav_keyboard(lang),
        )
        return

    existing = await app_chats_repo.get_by_chat_id(session, chat_id)
    if existing is not None:
        await state.clear()
        await message.answer(t("admin_chats_already_added", lang))
        text, kb = await _build_chats_text_and_kb(bot, session, lang)
        await message.answer(text, reply_markup=kb)
        return

    data = await state.get_data()
    btn = (data.get("button_title") or "").strip()
    if not btn:
        await state.clear()
        await message.answer(t("admin_chats_session_lost", lang))
        text, kb = await _build_chats_text_and_kb(bot, session, lang)
        await message.answer(text, reply_markup=kb)
        return

    invite_url, invite_ok = await _try_create_invite_link(bot, chat_id)
    await app_chats_repo.add_or_update(
        session,
        chat_id=chat_id,
        chat_link=invite_url,
        button_title_ru=btn,
        button_title_en=btn,
        button_title_uk=btn,
        button_title_pl=btn,
    )
    await session.commit()
    await state.clear()

    extra = (
        "\n\n" + t("admin_chats_invite_ok", lang)
        if invite_ok
        else "\n\n" + t("admin_chats_invite_link_failed", lang)
    )
    text, kb = await _build_chats_text_and_kb(bot, session, lang)
    await message.answer(
        t("admin_chats_added", lang).format(chat_id=chat_id) + extra + "\n\n" + text,
        reply_markup=kb,
    )


# ── Удаление ──────────────────────────────────────────────────────────────────


@router.callback_query(F.data == "admin:chats:delete", F.message.chat.type == "private")
async def on_admin_chats_delete_list(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    chats = await app_chats_repo.get_all(session)
    if not chats:
        text, kb = await _build_chats_text_and_kb(bot, session, lang)
        await callback.message.edit_text(text, reply_markup=kb)
        await callback.answer(t("admin_chats_delete_none", lang), show_alert=True)
        return
    items = [(c, await _list_line_title(bot, c, lang)) for c in chats]
    await callback.message.edit_text(
        t("admin_chats_delete_choose", lang),
        reply_markup=admin_chats_delete_list_keyboard(lang, items),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:chats:delete:ask:"), F.message.chat.type == "private"
)
async def on_admin_chats_delete_ask(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    try:
        chat_id = int(callback.data.split(":")[-1])
    except (TypeError, ValueError):
        await callback.answer()
        return
    await callback.message.edit_text(
        t("admin_chats_delete_confirm", lang).format(chat_id=chat_id),
        reply_markup=admin_chats_delete_confirm_keyboard(lang, chat_id),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:chats:delete:yes:"), F.message.chat.type == "private"
)
async def on_admin_chats_delete_yes(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    try:
        chat_id = int(callback.data.split(":")[-1])
    except (TypeError, ValueError):
        await callback.answer()
        return
    await app_chats_repo.delete(session, chat_id)
    await session.commit()
    text, kb = await _build_chats_text_and_kb(bot, session, lang)
    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer(t("admin_chats_deleted", lang), show_alert=True)


# ── Темы для игр (whitelist) ─────────────────────────────────────────────────


async def _topics_pick_line_titles(
    bot: Bot, session: AsyncSession, lang: str
) -> list[tuple]:
    chats = await app_chats_repo.get_all(session)
    return [(c, await _list_line_title(bot, c, lang)) for c in chats]


async def _topics_whitelist_back_callback(state: FSMContext | None) -> str:
    if state is None:
        return "admin:chats:topics"
    data = await state.get_data()
    return str(data.get("topics_whitelist_back") or "admin:chats:topics")


async def _render_topics_screen(
    message: Message,
    *,
    bot: Bot,
    session: AsyncSession,
    lang: str,
    telegram_chat_id: int,
    state: FSMContext | None = None,
) -> None:
    ac = await app_chats_repo.get_by_chat_id(session, telegram_chat_id)
    if ac is None:
        items = await _topics_pick_line_titles(bot, session, lang)
        await message.edit_text(
            t("admin_chats_topics_chat_unavailable", lang),
            reply_markup=(
                admin_chats_topics_chat_list_keyboard(lang, items)
                if items
                else admin_chats_keyboard(lang)
            ),
        )
        return
    try:
        tg_chat = await bot.get_chat(telegram_chat_id)
        is_forum = bool(getattr(tg_chat, "is_forum", False))
        title = tg_chat.title or str(telegram_chat_id)
    except Exception:
        items = await _topics_pick_line_titles(bot, session, lang)
        await message.edit_text(
            t("admin_chats_topics_chat_unavailable", lang),
            reply_markup=admin_chats_topics_chat_list_keyboard(lang, items),
        )
        return
    if not is_forum:
        items = await _topics_pick_line_titles(bot, session, lang)
        await message.edit_text(
            t("admin_chats_topics_not_forum", lang),
            reply_markup=admin_chats_topics_chat_list_keyboard(lang, items),
        )
        return
    active = await allowed_topics_repo.whitelist_active(session, ac.id)
    topics = await forum_topics_repo.list_for_chat(session, telegram_chat_id)
    items_toggle: list[tuple[int | None, str, bool]] = []
    if active:
        allowed_db = await allowed_topics_repo.list_allowed_db_threads(session, ac.id)
        items_toggle.append(
            (
                None,
                t("game21_pvp_topic_general", lang),
                GENERAL_THREAD_DB in allowed_db,
            )
        )
        for top in topics:
            label = format_forum_topic_display_label(
                lang,
                message_thread_id=top.message_thread_id,
                name=top.name or "",
            )
            items_toggle.append(
                (
                    int(top.message_thread_id),
                    label,
                    int(top.message_thread_id) in allowed_db,
                )
            )
    body_key = (
        "admin_chats_topics_body_restricted" if active else "admin_chats_topics_body_open"
    )
    body = t(body_key, lang).format(title=html.escape(title))
    back_cb = await _topics_whitelist_back_callback(state)
    kb = admin_chats_topic_whitelist_keyboard(
        lang,
        telegram_chat_id,
        whitelist_active=active,
        items=items_toggle,
        back_callback_data=back_cb,
    )
    await message.edit_text(body, reply_markup=kb, parse_mode=ParseMode.HTML)


def _parse_topics_chat_id(suffix: str) -> int | None:
    try:
        return int(suffix)
    except ValueError:
        return None


def _parse_topics_toggle(data: str) -> tuple[int, int] | None:
    prefix = "admin:chats:topics:toggle:"
    if not data.startswith(prefix):
        return None
    rest = data[len(prefix) :]
    pos = rest.rfind(":")
    if pos < 0:
        return None
    try:
        chat_id = int(rest[:pos])
        tid = int(rest[pos + 1 :])
    except ValueError:
        return None
    return chat_id, tid


@router.callback_query(F.data == "admin:chats:topics", F.message.chat.type == "private")
async def on_admin_chats_topics_menu(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot, state: FSMContext
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    await state.update_data(topics_whitelist_back=None)
    chats = await app_chats_repo.get_all(session)
    if not chats:
        await callback.answer(t("admin_chats_delete_none", lang), show_alert=True)
        return
    items = await _topics_pick_line_titles(bot, session, lang)
    await callback.message.edit_text(
        t("admin_chats_topics_choose_chat", lang),
        reply_markup=admin_chats_topics_chat_list_keyboard(lang, items),
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:chats:topics:open:"), F.message.chat.type == "private"
)
async def on_admin_chats_topics_open(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    await state.update_data(topics_whitelist_back=None)
    suffix = (callback.data or "").removeprefix("admin:chats:topics:open:")
    cid = _parse_topics_chat_id(suffix)
    if cid is None:
        await callback.answer()
        return
    await _render_topics_screen(
        callback.message,
        bot=bot,
        session=session,
        lang=lang,
        telegram_chat_id=cid,
        state=state,
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:chats:topics:toggle:"), F.message.chat.type == "private"
)
async def on_admin_chats_topics_toggle(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    par = _parse_topics_toggle(callback.data or "")
    if par is None:
        await callback.answer()
        return
    telegram_chat_id, tid_db = par
    thread_public = None if tid_db == 0 else tid_db
    ac = await app_chats_repo.get_by_chat_id(session, telegram_chat_id)
    if ac is None:
        await callback.answer()
        return
    if not await allowed_topics_repo.whitelist_active(session, ac.id):
        await callback.answer()
        return
    await allowed_topics_repo.toggle(session, ac.id, message_thread_id=thread_public)
    await session.commit()
    await _render_topics_screen(
        callback.message,
        bot=bot,
        session=session,
        lang=lang,
        telegram_chat_id=telegram_chat_id,
        state=state,
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:chats:topics:restrict:"), F.message.chat.type == "private"
)
async def on_admin_chats_topics_restrict(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    suffix = (callback.data or "").removeprefix("admin:chats:topics:restrict:")
    cid = _parse_topics_chat_id(suffix)
    if cid is None:
        await callback.answer()
        return
    ac = await app_chats_repo.get_by_chat_id(session, cid)
    if ac is None:
        await callback.answer()
        return
    await allowed_topics_repo.replace_with_full_seed(session, ac.id, cid)
    await session.commit()
    await _render_topics_screen(
        callback.message,
        bot=bot,
        session=session,
        lang=lang,
        telegram_chat_id=cid,
        state=state,
    )
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:chats:topics:clear:"), F.message.chat.type == "private"
)
async def on_admin_chats_topics_clear(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _resolve_lang(user, callback)
    if await _deny_if_not_admin(callback, user, lang):
        return
    suffix = (callback.data or "").removeprefix("admin:chats:topics:clear:")
    cid = _parse_topics_chat_id(suffix)
    if cid is None:
        await callback.answer()
        return
    ac = await app_chats_repo.get_by_chat_id(session, cid)
    if ac is None:
        await callback.answer()
        return
    await allowed_topics_repo.clear_whitelist(session, ac.id)
    await session.commit()
    await _render_topics_screen(
        callback.message,
        bot=bot,
        session=session,
        lang=lang,
        telegram_chat_id=cid,
        state=state,
    )
    await callback.answer()
