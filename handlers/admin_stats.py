"""Админская статистика."""

from __future__ import annotations

from decimal import Decimal

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.models.user import UserStatus
from locales.texts import get_lang, t
from permissions import is_admin
from settings import get_settings

router = Router(name="admin_stats")


def _lang(user: User, callback: CallbackQuery) -> str:
    return user.language_code or get_lang(callback.from_user.language_code)


async def _deny(callback: CallbackQuery, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await callback.answer(t("admin_no_access", lang), show_alert=True)
    return True


async def _safe_edit_text(
    callback: CallbackQuery, text: str, *, reply_markup: InlineKeyboardMarkup
) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=reply_markup)
    except TelegramBadRequest as exc:
        if "message is not modified" in str(exc):
            return
        raise


def _fmt_money(value: Decimal | int | None) -> str:
    return f"{Decimal(str(value or '0')):.2f}"


def _stats_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=t("admin_stats_btn_users", lang),
            callback_data="admin:stats:users",
        )
    )
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:admin"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


def _back_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:stats"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return builder.as_markup()


@router.callback_query(F.data == "admin:stats", F.message.chat.type == "private")
async def on_admin_stats(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.clear()
    await _safe_edit_text(
        callback,
        t("admin_stats_title", lang),
        reply_markup=_stats_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:stats:users", F.message.chat.type == "private")
async def on_admin_stats_users(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.clear()
    row = (
        await session.execute(
            select(
                func.count(User.user_id).label("total"),
                func.coalesce(func.sum(case((User.status == UserStatus.ACTIVE, 1), else_=0)), 0).label("active"),
                func.coalesce(func.sum(case((User.status == UserStatus.BANNED, 1), else_=0)), 0).label("banned"),
                func.coalesce(func.sum(case((User.balance > 0, 1), else_=0)), 0).label("with_balance"),
                func.coalesce(func.sum(User.balance), 0).label("balance_sum"),
            )
        )
    ).one()
    await _safe_edit_text(
        callback,
        t("admin_stats_users_title", lang).format(
            total=int(row.total or 0),
            active=int(row.active or 0),
            banned=int(row.banned or 0),
            with_balance=int(row.with_balance or 0),
            balance_sum=_fmt_money(row.balance_sum),
        ),
        reply_markup=_back_keyboard(lang),
    )
    await callback.answer()
