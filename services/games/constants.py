"""Константы игры в чате (как в Game_bot)."""

from database.models.game import GameType

ELIMINATED_MARKER = "__eliminated__"

MAIN_GAME_ALLOWED_EMOJIS = ("🎯", "🎳", "🎲")
MAIN_GAME_EMOJI_HINT = "🎯🎳🎲"

GAME_TYPE_DICE_EMOJI: dict[str, str] = {
    GameType.DICE: "🎲",
    GameType.BOWLING: "🎳",
    GameType.DARTS: "🎯",
    GameType.ANY: "🎲",
}
