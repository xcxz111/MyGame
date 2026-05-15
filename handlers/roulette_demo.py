"""Демо-рулетка без БД: только память, без списания баланса.

Команды (только админ бота, в группе/теме):
  /roulette_demo_start — запуск цикла (раунд ~2 мин)
  /roulette_demo_stop  — остановка

Удаление: этот файл + 2 строки в handlers/__init__.py
"""

from __future__ import annotations

import asyncio
import html
import logging
import random
from collections import defaultdict
from dataclasses import dataclass, field
from aiogram import Bot, F, Router
from aiogram.enums import ChatType, ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.models import User
from permissions import is_admin
from services.games.forum_thread import thread_kw
from settings import get_settings

logger = logging.getLogger(__name__)

router = Router(name="roulette_demo")

ROUND_SECONDS = 120
BETTING_SECONDS = 95
SPIN_WAIT_SECONDS = 6
BET_PLN = 1

# Стол (ожидание ставок) и «крутится» (можно заменить на свои file_id / URL)
TABLE_GIF_URL = "https://media.giphy.com/media/3o7btPCcdNniyf0ArK/giphy.gif"
_SPIN_GIF_BASE = "https://media.giphy.com/media/l0MYC0Lajbo8nefXG/giphy.gif"
SPIN_GIF_URLS: list[str] = [_SPIN_GIF_BASE] * 37

RED_NUMBERS = frozenset(
    {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
)

SECTIONS: dict[str, list[list[int]]] = {
    "1-12": [
        [3, 6, 9, 12],
        [2, 5, 8, 11],
        [1, 4, 7, 10],
    ],
    "13-24": [
        [15, 18, 21, 24],
        [14, 17, 20, 23],
        [13, 16, 19, 22],
    ],
    "25-36": [
        [27, 30, 33, 36],
        [26, 29, 32, 35],
        [25, 28, 31, 34],
    ],
}


class TopicClosedError(Exception):
    pass


@dataclass
class DemoSlot:
    chat_id: int
    message_thread_id: int | None
    task: asyncio.Task[None]
    table_message_id: int | None = None
    round_no: int = 0
    bets_open: bool = False
    view: str = "main"  # main | 1-12 | 13-24 | 25-36
    # (user_id, display_name) -> list of bet keys: int 0-36 or "red"/"black"
    bets: dict[tuple[int, str], list[int | str]] = field(default_factory=dict)


_slots: dict[tuple[int, int], DemoSlot] = {}


def _slot_key(chat_id: int, message_thread_id: int | None) -> tuple[int, int]:
    return int(chat_id), int(message_thread_id or 0)


def _topic_closed(exc: BaseException) -> bool:
    return "TOPIC_CLOSED" in str(exc).upper()


def _num_style(n: int) -> str | None:
    if n == 0:
        return "success"
    if n in RED_NUMBERS:
        return "danger"
    return "primary"


def _num_button(n: int) -> InlineKeyboardButton:
    style = _num_style(n)
    if style:
        return InlineKeyboardButton(text=str(n), callback_data=f"rdemo:n:{n}", style=style)
    return InlineKeyboardButton(text=str(n), callback_data=f"rdemo:n:{n}")


def _main_keyboard() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.row(InlineKeyboardButton(text="0", callback_data="rdemo:n:0", style="success"))
    b.row(
        InlineKeyboardButton(text="Красное", callback_data="rdemo:c:red", style="danger"),
        InlineKeyboardButton(text="Синее", callback_data="rdemo:c:black", style="primary"),
    )
    b.row(
        InlineKeyboardButton(text="1-12", callback_data="rdemo:sec:1-12"),
        InlineKeyboardButton(text="13-24", callback_data="rdemo:sec:13-24"),
        InlineKeyboardButton(text="25-36", callback_data="rdemo:sec:25-36"),
    )
    return b.as_markup()


def _section_keyboard(section: str) -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    for row in SECTIONS[section]:
        b.row(*[_num_button(n) for n in row])
    b.row(InlineKeyboardButton(text="← Назад к секциям", callback_data="rdemo:sec:main"))
    return b.as_markup()


def _keyboard_for_view(view: str) -> InlineKeyboardMarkup:
    if view == "main":
        return _main_keyboard()
    return _section_keyboard(view)


def _bet_summary(slot: DemoSlot) -> str:
    if not slot.bets:
        return "Ставки: пока нет."
    per_user: dict[str, list[str]] = defaultdict(list)
    for (_uid, name), picks in slot.bets.items():
        counts: dict[str, int] = defaultdict(int)
        for p in picks:
            if p == "red":
                counts["🔴"] += 1
            elif p == "black":
                counts["🔵"] += 1
            else:
                counts[str(p)] += 1
        parts = []
        for key in sorted(counts, key=lambda x: (x not in ("🔴", "🔵"), x)):
            c = counts[key]
            parts.append(f"{key}×{c}" if c > 1 else key)
        per_user[name].append(", ".join(parts))
    lines = ["<b>Ставки</b> (по 1 PLN за нажатие):"]
    for name, chunk in per_user.items():
        lines.append(f"• {html.escape(name)}: {html.escape(', '.join(chunk))}")
    return "\n".join(lines)


def _caption_open(slot: DemoSlot) -> str:
    return (
        f"🎰 <b>Демо-рулетка</b> · раунд #{slot.round_no}\n"
        f"Приём ставок · осталось ~{BETTING_SECONDS} с\n\n"
        f"{_bet_summary(slot)}"
    )


def _caption_closed() -> str:
    return "🎰 <b>Демо-рулетка</b>\n\n⛔ <b>Ставок больше нет</b>. Крутим…"


def _winning_color(n: int) -> str | None:
    if n == 0:
        return None
    return "red" if n in RED_NUMBERS else "black"


def _resolve_winners(slot: DemoSlot, result: int) -> list[str]:
    color = _winning_color(result)
    winners: list[str] = []
    for (_uid, name), picks in slot.bets.items():
        won = False
        for p in picks:
            if isinstance(p, int) and p == result:
                won = True
                break
            if p == color:
                won = True
                break
        if won:
            winners.append(name)
    return winners


async def _edit_table(
    bot: Bot,
    slot: DemoSlot,
    *,
    caption: str,
    reply_markup: InlineKeyboardMarkup | None,
) -> None:
    if slot.table_message_id is None:
        return
    try:
        await bot.edit_message_caption(
            chat_id=slot.chat_id,
            message_id=slot.table_message_id,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup,
            **thread_kw(slot.message_thread_id),
        )
    except TelegramBadRequest as exc:
        if _topic_closed(exc):
            raise TopicClosedError from exc
        if "message is not modified" not in str(exc).lower():
            logger.warning("roulette_demo edit_table: %s", exc)


async def _send_table(bot: Bot, slot: DemoSlot) -> None:
    msg = await bot.send_animation(
        slot.chat_id,
        animation=TABLE_GIF_URL,
        caption=_caption_open(slot),
        parse_mode=ParseMode.HTML,
        reply_markup=_keyboard_for_view(slot.view),
        **thread_kw(slot.message_thread_id),
    )
    slot.table_message_id = msg.message_id


async def _send_spin(bot: Bot, slot: DemoSlot) -> None:
    url = random.choice(SPIN_GIF_URLS)
    await bot.send_animation(
        slot.chat_id,
        animation=url,
        caption="🎡 Крутится…",
        **thread_kw(slot.message_thread_id),
    )


async def _send_result(bot: Bot, slot: DemoSlot, result: int) -> None:
    color = _winning_color(result)
    if result == 0:
        color_line = "🟢 зеро"
    elif color == "red":
        color_line = "🔴 красное"
    else:
        color_line = "🔵 синее"
    winners = _resolve_winners(slot, result)
    if winners:
        w_lines = "\n".join(f"• {html.escape(n)}" for n in winners)
        win_block = f"\n\n<b>Угадали:</b>\n{w_lines}"
    else:
        win_block = "\n\nНикто не угадал (демо, без выплат)."
    text = (
        f"🎯 <b>Результат: {result}</b> ({color_line})\n"
        f"Всего ставок: {sum(len(v) for v in slot.bets.values())}{win_block}"
    )
    await bot.send_message(
        slot.chat_id,
        text,
        parse_mode=ParseMode.HTML,
        **thread_kw(slot.message_thread_id),
    )


async def _run_one_round(bot: Bot, sk: tuple[int, int]) -> None:
    slot = _slots.get(sk)
    if slot is None:
        return

    slot.round_no += 1
    slot.bets.clear()
    slot.bets_open = True
    slot.view = "main"

    if slot.table_message_id is None:
        await _send_table(bot, slot)
    else:
        await _edit_table(
            bot,
            slot,
            caption=_caption_open(slot),
            reply_markup=_keyboard_for_view(slot.view),
        )

    await asyncio.sleep(BETTING_SECONDS)

    slot = _slots.get(sk)
    if slot is None:
        return
    slot.bets_open = False
    await _edit_table(bot, slot, caption=_caption_closed(), reply_markup=None)

    await _send_spin(bot, slot)
    await asyncio.sleep(SPIN_WAIT_SECONDS)

    result = random.randint(0, 36)
    await _send_result(bot, slot, result)

  # до конца 2 минут — пауза перед новым раундом
    elapsed = BETTING_SECONDS + SPIN_WAIT_SECONDS
    rest = max(5, ROUND_SECONDS - elapsed)
    await asyncio.sleep(rest)


async def _loop(bot: Bot, sk: tuple[int, int]) -> None:
    try:
        while sk in _slots:
            await _run_one_round(bot, sk)
    except TopicClosedError:
        logger.info("roulette_demo: topic closed chat=%s thread=%s", sk[0], sk[1])
    except asyncio.CancelledError:
        pass
    except Exception:
        logger.exception("roulette_demo loop failed sk=%s", sk)
    finally:
        _slots.pop(sk, None)


def _stop_slot(sk: tuple[int, int]) -> None:
    slot = _slots.pop(sk, None)
    if slot is None:
        return
    slot.task.cancel()


@router.message(
    Command("roulette_demo_start"),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def cmd_start(message: Message, user: User, bot: Bot) -> None:
    if not is_admin(user, get_settings()):
        await message.answer("⛔ Только для админа бота.")
        return

    sk = _slot_key(message.chat.id, message.message_thread_id)
    if sk in _slots:
        await message.answer("Демо-рулетка уже запущена в этой теме.")
        return

    thread_id = message.message_thread_id
    slot = DemoSlot(
        chat_id=int(message.chat.id),
        message_thread_id=int(thread_id) if thread_id is not None else None,
        task=asyncio.create_task(_loop(bot, sk)),
    )
    _slots[sk] = slot
    where = f"тема <code>{thread_id}</code>" if thread_id else "общий чат"
    await message.answer(
        f"✅ Демо-рулетка запущена ({where}).\n"
        f"Раунд ~{ROUND_SECONDS} с, ставка {BET_PLN} PLN (без списания).\n"
        f"Остановить: /roulette_demo_stop"
    )


@router.message(
    Command("roulette_demo_stop"),
    F.chat.type.in_({ChatType.GROUP, ChatType.SUPERGROUP}),
)
async def cmd_stop(message: Message, user: User) -> None:
    if not is_admin(user, get_settings()):
        await message.answer("⛔ Только для админа бота.")
        return

    sk = _slot_key(message.chat.id, message.message_thread_id)
    if sk not in _slots:
        await message.answer("Демо-рулетка здесь не запущена.")
        return
    _stop_slot(sk)
    await message.answer("🛑 Демо-рулетка остановлена.")


def _slot_for_callback(cb: CallbackQuery) -> DemoSlot | None:
    if cb.message is None:
        return None
    sk = _slot_key(cb.message.chat.id, cb.message.message_thread_id)
    return _slots.get(sk)


@router.callback_query(F.data.startswith("rdemo:"))
async def on_bet(cb: CallbackQuery) -> None:
    slot = _slot_for_callback(cb)
    if slot is None or cb.from_user is None:
        await cb.answer("Демо не запущено.", show_alert=True)
        return

    data = cb.data or ""
    parts = data.split(":")

    if len(parts) >= 3 and parts[1] == "sec":
        section = parts[2]
        if section == "main":
            slot.view = "main"
        elif section in SECTIONS:
            slot.view = section
        else:
            await cb.answer()
            return
        if slot.bets_open and slot.table_message_id:
            try:
                await _edit_table(
                    cb.bot,
                    slot,
                    caption=_caption_open(slot),
                    reply_markup=_keyboard_for_view(slot.view),
                )
            except TopicClosedError:
                _stop_slot(_slot_key(slot.chat_id, slot.message_thread_id))
        await cb.answer()
        return

    if not slot.bets_open:
        await cb.answer("Ставки закрыты.", show_alert=True)
        return

    uid = int(cb.from_user.id)
    name = (cb.from_user.full_name or cb.from_user.username or str(uid)).strip()
    key = (uid, name)

    if len(parts) >= 3 and parts[1] == "n":
        try:
            num = int(parts[2])
        except ValueError:
            await cb.answer()
            return
        if not 0 <= num <= 36:
            await cb.answer()
            return
        slot.bets.setdefault(key, []).append(num)
        await cb.answer(f"Ставка {BET_PLN} PLN на {num}")
    elif len(parts) >= 3 and parts[1] == "c":
        color = parts[2]
        if color not in ("red", "black"):
            await cb.answer()
            return
        slot.bets.setdefault(key, []).append(color)
        label = "красное" if color == "red" else "синее"
        await cb.answer(f"Ставка {BET_PLN} PLN на {label}")
    else:
        await cb.answer()
        return

    if slot.table_message_id:
        try:
            await _edit_table(
                cb.bot,
                slot,
                caption=_caption_open(slot),
                reply_markup=_keyboard_for_view(slot.view),
            )
        except TopicClosedError:
            _stop_slot(_slot_key(slot.chat_id, slot.message_thread_id))
            await cb.answer("Тема закрыта — демо остановлено.", show_alert=True)
