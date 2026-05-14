"""Минимальная логика шашек 8x8 для PvP."""

from __future__ import annotations

Board = dict[str, str]


def key(r: int, c: int) -> str:
    return f"{r},{c}"


def parse(pos: str) -> tuple[int, int]:
    r, c = pos.split(",", 1)
    return int(r), int(c)


def initial_board() -> Board:
    board: Board = {}
    for r in range(3):
        for c in range(8):
            if (r + c) % 2 == 1:
                board[key(r, c)] = "b"
    for r in range(5, 8):
        for c in range(8):
            if (r + c) % 2 == 1:
                board[key(r, c)] = "w"
    return board


def color(piece: str) -> str:
    return "w" if piece.lower() == "w" else "b"


def opponent(side: str) -> str:
    return "b" if side == "w" else "w"


def _inside(r: int, c: int) -> bool:
    return 0 <= r < 8 and 0 <= c < 8


def _dirs(piece: str, *, capture: bool) -> list[tuple[int, int]]:
    if piece.isupper() or capture:
        return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    return [(-1, -1), (-1, 1)] if piece == "w" else [(1, -1), (1, 1)]


def _king_captures(board: Board, pos: str, piece: str) -> list[dict]:
    r, c = parse(pos)
    captures: list[dict] = []
    for dr, dc in _dirs(piece, capture=True):
        seen_enemy: str | None = None
        step = 1
        while True:
            tr, tc = r + dr * step, c + dc * step
            if not _inside(tr, tc):
                break
            cur = key(tr, tc)
            cur_piece = board.get(cur)
            if cur_piece:
                if color(cur_piece) == color(piece):
                    break
                if seen_enemy is not None:
                    break
                seen_enemy = cur
            elif seen_enemy is not None:
                captures.append({"from": pos, "to": cur, "capture": seen_enemy})
            step += 1
    return captures


def _king_moves(board: Board, pos: str, piece: str) -> list[dict]:
    r, c = parse(pos)
    moves: list[dict] = []
    for dr, dc in _dirs(piece, capture=False):
        step = 1
        while True:
            tr, tc = r + dr * step, c + dc * step
            if not _inside(tr, tc):
                break
            target = key(tr, tc)
            if target in board:
                break
            moves.append({"from": pos, "to": target, "capture": None})
            step += 1
    return moves


def legal_moves_for(board: Board, pos: str, *, mandatory_capture: bool = True) -> list[dict]:
    piece = board.get(pos)
    if not piece:
        return []
    r, c = parse(pos)
    moves: list[dict] = []
    captures: list[dict] = []
    if piece.isupper():
        captures = _king_captures(board, pos, piece)
        if captures:
            return captures
        if mandatory_capture and any_captures(board, color(piece)):
            return []
        return _king_moves(board, pos, piece)
    for dr, dc in _dirs(piece, capture=True):
        mr, mc = r + dr, c + dc
        tr, tc = r + dr * 2, c + dc * 2
        mid = key(mr, mc)
        target = key(tr, tc)
        if (
            _inside(tr, tc)
            and mid in board
            and color(board[mid]) == opponent(color(piece))
            and target not in board
        ):
            captures.append({"from": pos, "to": target, "capture": mid})
    if captures:
        return captures
    if mandatory_capture and any_captures(board, color(piece)):
        return []
    for dr, dc in _dirs(piece, capture=False):
        tr, tc = r + dr, c + dc
        target = key(tr, tc)
        if _inside(tr, tc) and target not in board:
            moves.append({"from": pos, "to": target, "capture": None})
    return moves


def any_captures(board: Board, side: str) -> bool:
    for pos, piece in board.items():
        if color(piece) != side:
            continue
        if legal_moves_for(board, pos, mandatory_capture=False):
            # `mandatory_capture=False` returns captures first when available.
            if any(m.get("capture") for m in legal_moves_for(board, pos, mandatory_capture=False)):
                return True
    return False


def legal_moves(board: Board, side: str) -> list[dict]:
    out: list[dict] = []
    must_capture = any_captures(board, side)
    for pos, piece in board.items():
        if color(piece) == side:
            out.extend(legal_moves_for(board, pos, mandatory_capture=must_capture))
    return out


def apply_move(board: Board, move: dict) -> tuple[Board, str, bool]:
    new = dict(board)
    src = str(move["from"])
    dst = str(move["to"])
    piece = new.pop(src)
    cap = move.get("capture")
    if cap:
        new.pop(str(cap), None)
    r, _ = parse(dst)
    if piece == "w" and r == 0:
        piece = "W"
    elif piece == "b" and r == 7:
        piece = "B"
    new[dst] = piece
    more = bool(cap) and any(m.get("capture") for m in legal_moves_for(new, dst, mandatory_capture=False))
    return new, dst, more


def capture_sequences_for(board: Board, pos: str) -> list[list[dict]]:
    piece = board.get(pos)
    if not piece:
        return []
    first_moves = [m for m in legal_moves_for(board, pos, mandatory_capture=False) if m.get("capture")]
    if not first_moves:
        return []
    sequences: list[list[dict]] = []
    for move in first_moves:
        next_board, next_pos, more = apply_move(board, move)
        if not more:
            sequences.append([move])
            continue
        tails = capture_sequences_for(next_board, next_pos)
        if tails:
            sequences.extend([[move, *tail] for tail in tails])
        else:
            sequences.append([move])
    return sequences


def best_capture_path_targets(board: Board, pos: str) -> set[str]:
    sequences = capture_sequences_for(board, pos)
    if not sequences:
        return set()
    max_len = max(len(seq) for seq in sequences)
    out: set[str] = set()
    for seq in sequences:
        if len(seq) == max_len:
            out.update(str(move["to"]) for move in seq)
    return out


def winner_side(board: Board, next_side: str) -> str | None:
    sides = {color(p) for p in board.values()}
    if "w" not in sides:
        return "b"
    if "b" not in sides:
        return "w"
    if not legal_moves(board, next_side):
        return opponent(next_side)
    return None
