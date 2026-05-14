"""Админка КНБ."""

from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import app_chats as app_chats_repo
from database.repositories import fees as fees_repo
from database.repositories import forum_topics as forum_topics_repo
from database.repositories import kmb as kmb_repo
from handlers.admin_chats import _render_topics_screen
from locales.texts import get_lang, t
from permissions import is_admin
from settings import get_settings
from states.kmb import KmbAdminRulesState

router = Router(name="admin_kmb")


def _lang(user: User, event) -> str:
    return user.language_code or get_lang(getattr(event.from_user, "language_code", None))


async def _deny(callback: CallbackQuery, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await callback.answer(t("admin_no_access", lang), show_alert=True)
    return True


async def _deny_msg(message: Message, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await message.answer(t("admin_no_access", lang))
    return True


async def _safe_edit_text(
    message: Message,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    try:
        await message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        raise


def _fmt_money(value) -> str:
    return f"{float(value or 0):.2f}"


def _fmt_percent(value) -> str:
    return f"{float(value or 0):.2f}"


def _kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_kmb_btn_enable", lang),
            callback_data="admin:kmb:enable",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=t("admin_kmb_btn_rules", lang),
            callback_data="admin:kmb:rules",
            style="danger",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:admin", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


def _enable_kb(lang: str, chats: list[tuple[int, str, bool]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cid, title, enabled in chats:
        label = t(
            "admin_kmb_chat_on" if enabled else "admin_kmb_chat_off",
            lang,
        ).format(title=title[:28])
        builder.row(InlineKeyboardButton(text=label, callback_data=f"admin:kmb:chat:{cid}"))
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:kmb", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


async def _title(bot: Bot, chat_id: int) -> str:
    try:
        chat = await bot.get_chat(chat_id)
        return (chat.title or chat.full_name or str(chat_id))[:40]
    except Exception:
        return str(chat_id)


async def _collect_chat_rows(bot: Bot, session: AsyncSession) -> list[tuple[int, str, bool]]:
    rows = await app_chats_repo.get_all(session)
    out: list[tuple[int, str, bool]] = []
    for chat in rows:
        out.append((int(chat.chat_id), await _title(bot, chat.chat_id), bool(chat.kmb_enabled)))
    return out


def _rules_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_kmb_btn_rules", lang),
            callback_data="admin:kmb:rules:edit",
            style="danger",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:kmb", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return builder.as_markup()


@router.callback_query(F.data == "admin:kmb", F.message.chat.type == "private")
async def on_admin_kmb(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.clear()
    commission = await fees_repo.get_kmb_percent(session)
    stats = await kmb_repo.get_stats(session)
    await _safe_edit_text(
        callback.message,
        t("admin_kmb_title", lang).format(
            commission=_fmt_percent(commission),
            unique_users=stats["unique_users"],
            total_games=stats["total_games"],
            commission_sum=_fmt_money(stats["commission_sum"]),
        ),
        reply_markup=_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:kmb:enable", F.message.chat.type == "private")
async def on_admin_kmb_enable(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.clear()
    rows = await _collect_chat_rows(bot, session)
    if not rows:
        await callback.answer(t("admin_chats_delete_none", lang), show_alert=True)
        return
    await _safe_edit_text(
        callback.message,
        t("admin_kmb_enable_title", lang),
        reply_markup=_enable_kb(lang, rows),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:kmb:chat:"), F.message.chat.type == "private")
async def on_admin_kmb_chat_toggle(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext, bot: Bot
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    try:
        cid = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer()
        return
    row = await app_chats_repo.get_by_chat_id(session, cid)
    if row is None:
        await callback.answer("—", show_alert=True)
        return
    enabling = not bool(row.kmb_enabled)
    await app_chats_repo.set_kmb_enabled(session, cid, enabled=enabling)
    await session.commit()
    if enabling:
        topics = await forum_topics_repo.list_for_chat(session, cid)
        if topics:
            await state.update_data(topics_whitelist_back="admin:kmb:enable")
            await _render_topics_screen(
                callback.message,
                bot=bot,
                session=session,
                lang=lang,
                telegram_chat_id=cid,
                state=state,
            )
            await callback.answer()
            return
    await on_admin_kmb_enable(callback, session, user, state, bot)


@router.callback_query(F.data == "admin:kmb:rules", F.message.chat.type == "private")
async def on_admin_kmb_rules(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.clear()
    settings = await kmb_repo.get_settings(session)
    rules = (settings.rules_text or "").strip() or t("admin_kmb_rules_empty", lang)
    await _safe_edit_text(
        callback.message,
        t("admin_kmb_rules_title", lang).format(rules=rules),
        reply_markup=_rules_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:kmb:rules:edit", F.message.chat.type == "private")
async def on_admin_kmb_rules_edit(
    callback: CallbackQuery, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.set_state(KmbAdminRulesState.waiting_text)
    await _safe_edit_text(callback.message, t("admin_kmb_rules_prompt", lang), reply_markup=None)
    await callback.answer()


@router.message(StateFilter(KmbAdminRulesState.waiting_text), F.chat.type == "private")
async def on_admin_kmb_rules_text(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, message)
    if await _deny_msg(message, user, lang):
        await state.clear()
        return
    text = (message.text or "").strip()
    if not text:
        await message.answer(t("admin_kmb_rules_empty", lang))
        return
    await kmb_repo.set_rules(session, text)
    await session.commit()
    await state.clear()
    await message.answer(t("admin_kmb_rules_saved", lang))
    commission = await fees_repo.get_kmb_percent(session)
    stats = await kmb_repo.get_stats(session)
    await message.answer(
        t("admin_kmb_title", lang).format(
            commission=_fmt_percent(commission),
            unique_users=stats["unique_users"],
            total_games=stats["total_games"],
            commission_sum=_fmt_money(stats["commission_sum"]),
        ),
        reply_markup=_kb(lang),
    )
