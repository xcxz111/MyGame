from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales.texts import t
from services.checkers import engine


def _return_main_button(lang: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=t("btn_return_main", lang),
        callback_data="menu:main",
        style="primary",
    )


def checkers_confirm_keyboard(lang: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=t("game21_btn_yes", lang), callback_data="menu:checkers:confirm:yes", style="success"),
        InlineKeyboardButton(text=t("game21_btn_no", lang), callback_data="menu:checkers:confirm:no", style="danger"),
    )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def checkers_chat_pick_keyboard(lang: str, chats: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cid, title in chats:
        builder.row(
            InlineKeyboardButton(text=title[:64], callback_data=f"menu:checkers:chat:{cid}")
        )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def checkers_busy_keyboard(lang: str, *, show_cancel_search: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if show_cancel_search:
        builder.row(
            InlineKeyboardButton(
                text=t("game21_btn_abort_session", lang),
                callback_data="menu:checkers:cancel:active",
            )
        )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def checkers_main_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_return_main_button(lang)]
        ]
    )


def checkers_topic_pick_keyboard(
    lang: str,
    *,
    chat_id: int,
    topics: list[tuple[int, str]],
    busy: set[int | None],
    include_general: bool = True,
    back_callback_data: str = "menu:checkers",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if include_general:
        em = "🔴" if None in busy else "🟢"
        builder.row(
            InlineKeyboardButton(
                text=f"{em} Chat",
                callback_data=f"menu:checkers:th:{chat_id}:0",
            )
        )
    for tid, name in topics:
        em = "🔴" if tid in busy else "🟢"
        builder.row(
            InlineKeyboardButton(
                text=f"{em} {name}"[:64],
                callback_data=f"menu:checkers:th:{chat_id}:{tid}",
            )
        )
    builder.row(_return_main_button(lang))
    return builder.as_markup()


def checkers_accept_keyboard(lang: str, owner_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=t("checkers_btn_accept", lang),
                    callback_data=f"menu:checkers:accept:{owner_id}",
                )
            ]
        ]
    )


def _piece_text(piece: str | None) -> str:
    if piece == "w":
        return "⚪️"
    if piece == "W":
        return "⚪️♛"
    if piece == "b":
        return "⚫️"
    if piece == "B":
        return "⚫️♛"
    return ""


def _move_arrow(src: str, dst: str, *, emoji: bool = False) -> str:
    r1, c1 = engine.parse(src)
    r2, c2 = engine.parse(dst)
    if r2 < r1 and c2 > c1:
        return "↗️" if emoji else "↗"
    if r2 > r1 and c2 > c1:
        return "↘️" if emoji else "↘"
    if r2 > r1 and c2 < c1:
        return "↙️" if emoji else "↙"
    return "↖️" if emoji else "↖"


def _move_path_arrows(src: str, dst: str) -> dict[str, str]:
    r1, c1 = engine.parse(src)
    r2, c2 = engine.parse(dst)
    if r1 == r2 or c1 == c2:
        return {}
    dr = 1 if r2 > r1 else -1
    dc = 1 if c2 > c1 else -1
    arrow = _move_arrow(src, dst, emoji=True)
    cells: dict[str, str] = {}
    r, c = r1, c1
    while (r, c) != (r2, c2):
        cells[engine.key(r, c)] = arrow
        r += dr
        c += dc
    return cells


def board_keyboard(st: dict, *, selected: str | None = None) -> InlineKeyboardMarkup:
    board = st.get("board") or {}
    token = int(st.get("token") or 0)
    rows = []
    side = st.get("turn_side") or "w"
    legal_targets: set[str] = set()
    if selected:
        legal_targets = engine.best_capture_path_targets(board, selected)
        if not legal_targets:
            legal_targets = {
                str(m["to"])
                for m in engine.legal_moves(board, side)
                if m.get("from") == selected
            }
    chain = list(st.get("last_move_chain") or [])
    if not chain and st.get("last_move"):
        chain = [st.get("last_move") or {}]
    path_arrows: dict[str, str] = {}
    for seg in chain:
        if seg.get("from") and seg.get("to"):
            path_arrows.update(_move_path_arrows(str(seg.get("from")), str(seg.get("to"))))
    captured_cells = {str(seg.get("capture")) for seg in chain if seg.get("capture")}
    final_seg = chain[-1] if chain else {}
    final_to = str(final_seg.get("to") or "")
    final_arrow = (
        _move_arrow(str(final_seg.get("from")), final_to)
        if final_seg.get("from") and final_to
        else ""
    )
    for r in range(8):
        row = []
        for c in range(8):
            pos = engine.key(r, c)
            piece = board.get(pos)
            if (r + c) % 2 == 0:
                row.append(InlineKeyboardButton(text="·", callback_data="chk:n"))
                continue
            if selected == pos:
                text = "🔵"
            elif pos in legal_targets:
                text = "🟩"
            elif pos in captured_cells:
                text = "🟠"
            elif pos in path_arrows:
                text = path_arrows[pos] or "▫️"
            elif pos == final_to:
                text = f"{_piece_text(piece)}{final_arrow}"
            elif piece:
                text = _piece_text(piece)
            else:
                text = "▫️"
            row.append(
                InlineKeyboardButton(
                    text=text,
                    callback_data=f"chk:m:{token}:{r}:{c}",
                )
            )
        rows.append(row)
    return InlineKeyboardMarkup(inline_keyboard=rows)
