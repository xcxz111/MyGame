"""Запись на игры (ЛС): меню «Записаться», просмотр и join/leave."""

from __future__ import annotations

import html
from datetime import date, datetime
from decimal import Decimal

from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.models.game import Game, GameStatus
from database.models.payment_log import PaymentLogMethod
from database.repositories import app_chats as app_chats_repo
from database.repositories import game_participants as gp_repo
from database.repositories import games as games_repo
from database.repositories import payment_logs as payment_logs_repo
from database.repositories import prizes as prizes_repo
from keyboards.main_menu import main_menu_keyboard
from locales.texts import get_lang, t
from settings import get_settings

router = Router(name="game_signup")


def _user_lang(user: User, callback: CallbackQuery) -> str:
    return user.language_code or get_lang(callback.from_user.language_code)


def _fmt_money(value: Decimal) -> str:
    d = value if isinstance(value, Decimal) else Decimal(str(value))
    s = f"{d:.2f}"
    return s.rstrip("0").rstrip(".") if "." in s else s


async def _chat_display_name(
    bot: Bot, session: AsyncSession, chat_id: int, lang: str
) -> str:
    row = await app_chats_repo.get_by_chat_id(session, chat_id)
    if row is not None:
        s = row.button_title_for(lang)
        if s:
            return s
    try:
        chat = await bot.get_chat(chat_id)
        return (chat.title or chat.full_name or str(chat_id)) or str(chat_id)
    except Exception:
        return str(chat_id)


def _game_view_markup(
    lang: str, game_id: int, registered: bool
) -> InlineKeyboardBuilder:
    b = InlineKeyboardBuilder()
    if registered:
        b.row(
            InlineKeyboardButton(
                text=t("game_signup_btn_leave", lang),
                callback_data=f"game:leave:{game_id}",
            )
        )
    else:
        b.row(
            InlineKeyboardButton(
                text=t("game_signup_btn_join", lang),
                callback_data=f"game:join:{game_id}",
            )
        )
    b.row(
        InlineKeyboardButton(
            text=t("btn_back", lang), callback_data="menu:signup"
        )
    )
    return b


async def _render_game_card(
    bot: Bot,
    session: AsyncSession,
    *,
    game: Game,
    lang: str,
    user_id: int,
) -> tuple[str, InlineKeyboardBuilder]:
    registered = await gp_repo.is_registered(session, game_id=game.id, user_id=user_id)
    n = await games_repo.count_participants(session, game.id)
    prizes = await prizes_repo.for_game(session, game.id)
    chat_title = html.escape(
        await _chat_display_name(bot, session, int(game.chat_id), lang)
    )
    prize_lines = "\n".join(
        f"{i}. {_fmt_money(p.amount)} PLN" for i, p in enumerate(prizes, 1)
    )
    min_top = game.min_topup or Decimal("0")
    since = game.min_topup_since
    is_paid = bool(int(game.is_paid or 0))
    fee = game.entry_fee or Decimal("0")
    start_s = game.start_time.strftime("%d.%m.%Y %H:%M")
    cond: list[str] = []
    if min_top > Decimal("0"):
        if since is not None:
            since_lbl = (
                since.strftime("%d.%m.%Y")
                if hasattr(since, "strftime")
                else str(since)
            )
            cond.append(
                t("game_signup_cond_topup_period", lang).format(
                    n=_fmt_money(min_top), since=since_lbl
                )
            )
        else:
            cond.append(
                t("game_signup_cond_topup_alltime", lang).format(n=_fmt_money(min_top))
            )
    if is_paid and fee > Decimal("0"):
        cond.append(t("game_signup_cond_paid", lang).format(fee=_fmt_money(fee)))
    else:
        cond.append(t("game_signup_cond_free", lang))
    body = t("game_signup_card", lang).format(
        id=game.id,
        chat=chat_title,
        start=start_s,
        count=n,
        max_p=game.max_participants,
        min_p=game.min_participants,
        conditions="\n".join(cond) if cond else t("game_signup_cond_none", lang),
        prizes=html.escape(prize_lines) if prize_lines else "—",
    )
    kb = _game_view_markup(lang, game.id, registered)
    return body, kb


@router.callback_query(F.data == "menu:signup", F.message.chat.type == "private")
async def on_menu_signup(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _user_lang(user, callback)
    now = datetime.now()
    games = await games_repo.list_draft_future_for_signup(session, now)
    if not games:
        menu_chats = await app_chats_repo.list_for_main_menu(session)
        await callback.message.edit_text(
            t("game_signup_no_games", lang),
            reply_markup=main_menu_keyboard(
                lang,
                user.user_id,
                get_settings().admin_id,
                menu_chats=menu_chats,
            ),
        )
        await callback.answer()
        return
    b = InlineKeyboardBuilder()
    for g in games:
        title = await _chat_display_name(bot, session, int(g.chat_id), lang)
        short = (title[:28] + "…") if len(title) > 30 else title
        label = t("game_signup_list_item", lang).format(
            id=g.id, chat=short, when=g.start_time.strftime("%d.%m %H:%M")
        )
        b.row(InlineKeyboardButton(text=label, callback_data=f"game:signup:{g.id}"))
    b.row(
        InlineKeyboardButton(text=t("btn_main", lang), callback_data="menu:main")
    )
    await callback.message.edit_text(
        t("game_signup_list_title", lang), reply_markup=b.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("game:signup:"), F.message.chat.type == "private")
async def on_game_signup_open(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _user_lang(user, callback)
    try:
        game_id = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer(t("game_signup_not_found", lang), show_alert=True)
        return
    game = await games_repo.get(session, game_id)
    if game is None or game.status != GameStatus.DRAFT:
        await callback.answer(t("game_signup_not_draft", lang), show_alert=True)
        return
    if game.start_time <= datetime.now():
        await callback.answer(t("game_signup_started", lang), show_alert=True)
        return
    text, kb = await _render_game_card(bot, session, game=game, lang=lang, user_id=user.user_id)
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb.as_markup())
    await callback.answer()


@router.callback_query(F.data.startswith("game:join:"), F.message.chat.type == "private")
async def on_game_join(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _user_lang(user, callback)
    try:
        game_id = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer(t("game_signup_not_found", lang), show_alert=True)
        return
    game = await games_repo.get(session, game_id)
    if game is None or game.status != GameStatus.DRAFT:
        await callback.answer(t("game_signup_not_draft", lang), show_alert=True)
        return
    if game.start_time <= datetime.now():
        await callback.answer(t("game_signup_started", lang), show_alert=True)
        return
    if await gp_repo.is_registered(session, game_id=game_id, user_id=user.user_id):
        await callback.answer(t("game_signup_already_in", lang), show_alert=True)
        return
    n = await games_repo.count_participants(session, game_id)
    if n >= int(game.max_participants):
        await callback.answer(t("game_signup_full", lang), show_alert=True)
        return
    min_top = game.min_topup or Decimal("0")
    if min_top > Decimal("0"):
        since = game.min_topup_since
        since_day: date | None = None
        if since is not None:
            if isinstance(since, datetime):
                since_day = since.date()
            elif isinstance(since, date):
                since_day = since
        top_sum = await payment_logs_repo.sum_topup_amount(
            session,
            user_id=user.user_id,
            since=since_day,
            until=game.start_time,
        )
        if top_sum < min_top:
            await callback.answer(
                t("game_signup_min_topup", lang).format(
                    need=_fmt_money(min_top), have=_fmt_money(top_sum)
                ),
                show_alert=True,
            )
            return
    fee = game.entry_fee or Decimal("0")
    is_paid = bool(int(game.is_paid or 0)) and fee > Decimal("0")
    if is_paid:
        bal = user.balance or Decimal("0")
        if bal < fee:
            await callback.answer(
                t("game_signup_low_balance", lang).format(
                    fee=_fmt_money(fee), balance=_fmt_money(bal)
                ),
                show_alert=True,
            )
            return
        user.balance = bal - fee
        await session.flush()
        await payment_logs_repo.log(
            session,
            user_id=user.user_id,
            method=PaymentLogMethod.GAME_ENTRY,
            amount=-fee,
            balance_after=user.balance,
        )
    try:
        await gp_repo.register(session, game_id=game_id, user_id=user.user_id)
        await session.flush()
    except IntegrityError:
        await session.rollback()
        await callback.answer(t("game_signup_already_in", lang), show_alert=True)
        return
    await callback.answer(t("game_signup_ok", lang))
    game = await games_repo.get(session, game_id)
    text, kb = await _render_game_card(
        bot, session, game=game, lang=lang, user_id=user.user_id
    )
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith("game:leave:"), F.message.chat.type == "private")
async def on_game_leave(
    callback: CallbackQuery, session: AsyncSession, user: User, bot: Bot
) -> None:
    lang = _user_lang(user, callback)
    try:
        game_id = int(callback.data.split(":")[-1])
    except ValueError:
        await callback.answer(t("game_signup_not_found", lang), show_alert=True)
        return
    game = await games_repo.get(session, game_id)
    if game is None or game.status != GameStatus.DRAFT:
        await callback.answer(t("game_signup_not_draft", lang), show_alert=True)
        return
    if not await gp_repo.is_registered(session, game_id=game_id, user_id=user.user_id):
        await callback.answer(t("game_signup_not_in", lang), show_alert=True)
        return
    fee = game.entry_fee or Decimal("0")
    is_paid = bool(int(game.is_paid or 0)) and fee > Decimal("0")
    if is_paid:
        user.balance = (user.balance or Decimal("0")) + fee
        await session.flush()
        await payment_logs_repo.log(
            session,
            user_id=user.user_id,
            method=PaymentLogMethod.GAME_ENTRY_REFUND,
            amount=fee,
            balance_after=user.balance,
        )
    await gp_repo.unregister(session, game_id=game_id, user_id=user.user_id)
    await callback.answer(t("game_signup_left", lang))
    game = await games_repo.get(session, game_id)
    text, kb = await _render_game_card(
        bot, session, game=game, lang=lang, user_id=user.user_id
    )
    await callback.message.edit_text(text, parse_mode=ParseMode.HTML, reply_markup=kb.as_markup())
