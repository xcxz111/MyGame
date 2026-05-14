"""Админка КНБ."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import fees as fees_repo
from database.repositories import kmb as kmb_repo
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
            text=t("admin_kmb_btn_rules", lang),
            callback_data="admin:kmb:rules",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:admin"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


def _rules_kb(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_kmb_btn_rules", lang),
            callback_data="admin:kmb:rules:edit",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:kmb"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
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
