"""Публикация объявления о поиске соперника (тема + общий чат), закреп."""

from __future__ import annotations

import logging
from decimal import Decimal

from aiogram import Bot
from aiogram.enums import ParseMode

from locales.texts import t
from services.game21.formatting import fmt_money, name_link, possible_win_pvp
from services.game21.pvp_runtime import _bot_link_html
from services.games.forum_thread import pin_chat_message_in_forum, thread_kw

logger = logging.getLogger(__name__)


async def post_dual_search(
    bot: Bot,
    *,
    chat_id: int,
    message_thread_id: int | None,
    lang: str,
    owner_id: int,
    owner_name: str,
    bet: Decimal,
    commission_percent: Decimal,
    accept_markup,
) -> tuple[int | None, int | None]:
    """Возвращает (message_id в теме или общем первом посте, message_id дубля в общем)."""
    win = possible_win_pvp(bet, commission_percent)
    bl = await _bot_link_html(bot, lang)
    text = t("game21_pvp_search_post", lang).format(
        user=name_link(owner_id, owner_name),
        amount=fmt_money(bet),
        win=fmt_money(win),
        bot_link=bl,
    )
    tw = thread_kw(message_thread_id)
    sent_topic = None
    try:
        sent_topic = await bot.send_message(
            chat_id,
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=accept_markup,
            **tw,
        )
    except Exception as exc:
        logger.exception("pvp search post topic: %s", exc)
        return None, None
    if sent_topic is None:
        return None, None
    try:
        await pin_chat_message_in_forum(
            bot,
            chat_id=chat_id,
            message_id=sent_topic.message_id,
            message_thread_id=message_thread_id,
        )
    except Exception as exc:
        logger.debug("pvp pin topic: %s", exc)

    sent_general = None
    if message_thread_id is not None:
        try:
            sent_general = await bot.send_message(
                chat_id,
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=accept_markup,
            )
        except Exception as exc:
            logger.warning("pvp search post general: %s", exc)
        if sent_general is not None:
            try:
                await pin_chat_message_in_forum(
                    bot,
                    chat_id=chat_id,
                    message_id=sent_general.message_id,
                    message_thread_id=None,
                )
            except Exception as exc:
                logger.debug("pvp pin general: %s", exc)
    return sent_topic.message_id, (
        sent_general.message_id if sent_general is not None else None
    )


async def unpin_general_message(
    bot: Bot, *, chat_id: int, message_id: int | None
) -> None:
    if not message_id:
        return
    from services.games.forum_thread import unpin_chat_message_in_forum

    try:
        await unpin_chat_message_in_forum(
            bot,
            chat_id=chat_id,
            message_id=int(message_id),
            message_thread_id=None,
        )
    except Exception as exc:
        logger.debug("pvp unpin general: %s", exc)
