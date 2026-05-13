"""Админка: режимы «21» (бот + PvP по чатам)."""

from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import app_chats as app_chats_repo
from database.repositories import forum_topics as forum_topics_repo
from database.repositories import game21_settings as g21_repo
from handlers.admin_chats import _render_topics_screen
from locales.texts import get_lang, t
from permissions import is_admin
from settings import get_settings

router = Router(name="admin_game21")


def _lang(user: User, cb: CallbackQuery) -> str:
    return user.language_code or get_lang(cb.from_user.language_code)


async def _deny(cb: CallbackQuery, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await cb.answer(t("admin_no_access", lang), show_alert=True)
    return True


async def _title(bot: Bot, chat_id: int) -> str:
    try:
        c = await bot.get_chat(chat_id)
        return (c.title or c.full_name or str(chat_id))[:40]
    except Exception:
        return str(chat_id)


def _kb(
    lang: str,
    *,
    bot_on: bool,
    chats: list[tuple[int, str, bool]],
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(
            text=t("admin_21_btn_bot_off" if bot_on else "admin_21_btn_bot_on", lang),
            callback_data="admin:21:toggle:bot",
        )
    )
    for cid, title, pvp in chats:
        label = t("admin_21_chat_pvp_off" if pvp else "admin_21_chat_pvp_on", lang).format(
            title=title[:28]
        )
        b.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f"admin:21:chatpvp:{cid}",
            )
        )
    b.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:admin"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main"),
    )
    return b.as_markup()


@router.callback_query(F.data == "admin:21", F.message.chat.type == "private")
async def on_admin_21_open(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.clear()
    s = await g21_repo.get_settings(session)
    rows = await app_chats_repo.get_all(session)
    chat_rows: list[tuple[int, str, bool]] = []
    for c in rows:
        title = await _title(bot, c.chat_id)
        chat_rows.append((c.chat_id, title, bool(c.game21_users_enabled)))
    text = t("admin_21_title", lang).format(
        bot=t("admin_21_on" if s.enabled_bot else "admin_21_off", lang),
        bot_fee=s.commission_bot_percent,
        users_fee=s.commission_users_percent,
    )
    await callback.message.edit_text(
        text,
        reply_markup=_kb(
            lang,
            bot_on=bool(s.enabled_bot),
            chats=chat_rows,
        ),
    )
    await callback.answer()


@router.callback_query(F.data == "admin:21:toggle:bot", F.message.chat.type == "private")
async def on_toggle_bot(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    s = await g21_repo.get_settings(session)
    await g21_repo.set_enabled_bot(session, not bool(s.enabled_bot))
    await session.commit()
    await on_admin_21_open(callback, session, user, bot, state)
    await callback.answer()


@router.callback_query(
    F.data.startswith("admin:21:chatpvp:"), F.message.chat.type == "private"
)
async def on_toggle_chat_pvp(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    bot: Bot,
    state: FSMContext,
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
    enabling = not bool(row.game21_users_enabled)
    await app_chats_repo.set_game21_users_enabled(session, cid, enabled=enabling)
    await session.commit()
    if enabling:
        topics = await forum_topics_repo.list_for_chat(session, cid)
        if topics:
            await state.update_data(topics_whitelist_back="admin:21")
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
    await on_admin_21_open(callback, session, user, bot, state)
    await callback.answer()
