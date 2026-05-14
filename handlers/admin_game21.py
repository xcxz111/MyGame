"""Админка: режимы «21» (бот + PvP по чатам)."""

from __future__ import annotations

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import app_chat_allowed_topics as allowed_topics_repo
from database.repositories import app_chats as app_chats_repo
from database.repositories import forum_topics as forum_topics_repo
from database.repositories import game21_history as g21_history_repo
from database.repositories import game21_settings as g21_repo
from handlers.admin_chats import _render_topics_screen
from locales.texts import get_lang, t
from permissions import is_admin
from services.game21.rules_translation import translate_rules_from_ru
from settings import get_settings
from states.game21 import Game21RulesState

router = Router(name="admin_game21")


def _lang(user: User, cb: CallbackQuery) -> str:
    return user.language_code or get_lang(cb.from_user.language_code)


async def _deny(cb: CallbackQuery, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await cb.answer(t("admin_no_access", lang), show_alert=True)
    return True


async def _deny_msg(message: Message, user: User, lang: str) -> bool:
    if is_admin(user, get_settings()):
        return False
    await message.answer(t("admin_no_access", lang))
    return True


async def _title(bot: Bot, chat_id: int) -> str:
    try:
        c = await bot.get_chat(chat_id)
        return (c.title or c.full_name or str(chat_id))[:40]
    except Exception:
        return str(chat_id)


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


def _fmt_money(v) -> str:
    return f"{float(v or 0):.2f}"


def _fmt_percent(v) -> str:
    return f"{float(v or 0):.2f}"


def _main_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text=t("admin_21_btn_enable", lang), callback_data="admin:21:enable"))
    b.row(InlineKeyboardButton(text=t("admin_21_btn_rules", lang), callback_data="admin:21:rules"))
    b.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="menu:admin", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return b.as_markup()


def _enable_kb(
    lang: str,
    *,
    bot_on: bool,
    chats: list[tuple[int, str, bool]],
) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(
            text=t("admin_21_btn_bot_on" if bot_on else "admin_21_btn_bot_off", lang),
            callback_data="admin:21:toggle:bot",
        )
    )
    for cid, title, pvp in chats:
        label = t("admin_21_chat_pvp_on" if pvp else "admin_21_chat_pvp_off", lang).format(
            title=title[:28]
        )
        b.row(
            InlineKeyboardButton(
                text=label,
                callback_data=f"admin:21:chatpvp:{cid}",
            )
        )
    b.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:21", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return b.as_markup()


def _rules_kb(lang: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(
        InlineKeyboardButton(
            text=t("admin_21_rules_btn_bot", lang),
            callback_data="admin:21:rules:bot",
        )
    )
    b.row(
        InlineKeyboardButton(
            text=t("admin_21_rules_btn_users", lang),
            callback_data="admin:21:rules:users",
        )
    )
    b.row(
        InlineKeyboardButton(text=t("btn_back", lang), callback_data="admin:21", style="primary"),
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main", style="primary"),
    )
    return b.as_markup()


async def _collect_chat_rows(bot: Bot, session: AsyncSession) -> list[tuple[int, str, bool]]:
    rows = await app_chats_repo.get_all(session)
    chat_rows: list[tuple[int, str, bool]] = []
    for c in rows:
        title = await _title(bot, c.chat_id)
        chat_rows.append((c.chat_id, title, bool(c.game21_users_enabled)))
    return chat_rows


async def _enable_status_text(
    bot: Bot,
    session: AsyncSession,
    *,
    bot_on: bool,
) -> str:
    on = "🟢 вкл"
    off = "🔴 выкл"
    lines = [
        f"Против бота: {on if bot_on else off}",
        "Между пользователями:",
    ]
    rows = await app_chats_repo.get_all(session)
    for c in rows:
        title = await _title(bot, c.chat_id)
        pvp_enabled = bool(c.game21_users_enabled)
        lines.append(f"{title}: {on if pvp_enabled else off}")
        if not pvp_enabled:
            continue

        topics = await forum_topics_repo.list_for_chat(session, c.chat_id)
        if not topics:
            continue

        allowed = await allowed_topics_repo.effective_allowed_public_threads(session, c.chat_id)
        lines.append(f"- Chat: {on if allowed is None or None in allowed else off}")
        for topic in topics:
            thread_id = int(topic.message_thread_id)
            topic_enabled = allowed is None or thread_id in allowed
            lines.append(f"- {topic.name}: {on if topic_enabled else off}")
    return "\n".join(lines)


async def _render_admin_21_main(
    callback: CallbackQuery,
    session: AsyncSession,
    user: User,
    lang: str,
) -> None:
    s = await g21_repo.get_settings(session)
    stats = await g21_history_repo.get_admin_stats(session)
    total_profit = stats["bot_profit_sum"] + stats["pvp_commission_sum"]
    text = t("admin_21_summary", lang).format(
        bot_fee=_fmt_percent(s.commission_bot_percent),
        users_fee=_fmt_percent(s.commission_users_percent),
        bot_total=stats["bot_total"],
        bot_won_count=stats["bot_won_count"],
        bot_won_sum=_fmt_money(stats["bot_won_sum"]),
        bot_lost_count=stats["bot_lost_count"],
        bot_lost_sum=_fmt_money(stats["bot_lost_sum"]),
        bot_draw_count=stats["bot_draw_count"],
        bot_profit_sum=_fmt_money(stats["bot_profit_sum"]),
        pvp_total=stats["pvp_total"],
        pvp_commission_sum=_fmt_money(stats["pvp_commission_sum"]),
        total_profit_sum=_fmt_money(total_profit),
    )
    await _safe_edit_text(callback.message, text, reply_markup=_main_kb(lang))


async def _render_enable_menu(
    callback: CallbackQuery,
    session: AsyncSession,
    bot: Bot,
    lang: str,
) -> None:
    s = await g21_repo.get_settings(session)
    await _safe_edit_text(
        callback.message,
        await _enable_status_text(bot, session, bot_on=bool(s.enabled_bot)),
        reply_markup=_enable_kb(
            lang,
            bot_on=bool(s.enabled_bot),
            chats=await _collect_chat_rows(bot, session),
        ),
    )


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
    await _render_admin_21_main(callback, session, user, lang)
    await callback.answer()


@router.callback_query(F.data == "admin:21:enable", F.message.chat.type == "private")
async def on_admin_21_enable(
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
    await _render_enable_menu(callback, session, bot, lang)
    await callback.answer()


@router.callback_query(F.data == "admin:21:rules", F.message.chat.type == "private")
async def on_admin_21_rules(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    await state.clear()
    s = await g21_repo.get_settings(session)
    await _safe_edit_text(
        callback.message,
        t("admin_21_rules_title", lang).format(
            bot="✅" if s.rules_bot_text else "—",
            users="✅" if s.rules_users_text else "—",
        ),
        reply_markup=_rules_kb(lang),
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
    await _render_enable_menu(callback, session, bot, lang)
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
            await state.update_data(topics_whitelist_back="admin:21:enable")
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
    await _render_enable_menu(callback, session, bot, lang)
    await callback.answer()


@router.callback_query(
    F.data.in_({"admin:21:rules:bot", "admin:21:rules:users"}),
    F.message.chat.type == "private",
)
async def on_admin_21_rules_pick(
    callback: CallbackQuery, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = _lang(user, callback)
    if await _deny(callback, user, lang):
        return
    target = "bot" if callback.data.endswith(":bot") else "users"
    await state.set_state(Game21RulesState.waiting_text)
    await state.update_data(game21_rules_target=target)
    key = "admin_21_rules_prompt_bot" if target == "bot" else "admin_21_rules_prompt_users"
    await _safe_edit_text(
        callback.message,
        t(key, lang),
        reply_markup=None,
    )
    await callback.answer()


@router.message(StateFilter(Game21RulesState.waiting_text), F.chat.type == "private")
async def on_admin_21_rules_text(
    message: Message, session: AsyncSession, user: User, state: FSMContext
) -> None:
    lang = user.language_code or get_lang(message.from_user.language_code)
    if await _deny_msg(message, user, lang):
        await state.clear()
        return
    data = await state.get_data()
    target = data.get("game21_rules_target")
    text = (message.text or "").strip()
    if not text:
        await message.answer(t("admin_21_rules_empty", lang))
        return
    translations = await translate_rules_from_ru(text)
    if target == "bot":
        await g21_repo.set_rules_bot(session, text, translations=translations)
    elif target == "users":
        await g21_repo.set_rules_users(session, text, translations=translations)
    else:
        await state.clear()
        return
    await session.commit()
    await state.clear()
    saved_key = (
        "admin_21_rules_saved"
        if all(code in translations for code in ("en", "uk", "pl"))
        else "admin_21_rules_saved_no_translate"
    )
    await message.answer(t(saved_key, lang), reply_markup=_rules_kb(lang))
