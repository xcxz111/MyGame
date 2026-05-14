"""Перевод админских правил 21 с русского на языки интерфейса."""

from __future__ import annotations

import json
import logging

from services.payments.ai_clients.factory import create_ai_client
from settings import get_settings

logger = logging.getLogger(__name__)

TARGET_LANGS = ("en", "uk", "pl")

_LANG_NAMES = {
    "en": "English",
    "uk": "Ukrainian",
    "pl": "Polish",
}

_SYSTEM_PROMPT = (
    "You translate Telegram bot game rules from Russian. "
    "Return only a JSON object. Preserve line breaks, numbers, placeholders in braces, "
    "Telegram HTML tags, emoji, currency names, and meaning. Do not add explanations."
)


async def translate_rules_from_ru(text: str) -> dict[str, str]:
    text = (text or "").strip()
    settings = get_settings()
    if not text or not settings.ai_api_key:
        return {}

    client = create_ai_client(settings)
    user_content = json.dumps(
        {
            "source_language": "Russian",
            "target_languages": {code: _LANG_NAMES[code] for code in TARGET_LANGS},
            "text": text,
            "return_schema": {"en": "string", "uk": "string", "pl": "string"},
        },
        ensure_ascii=False,
    )

    try:
        raw = await client.chat(_SYSTEM_PROMPT, user_content)
        data = json.loads(raw)
    except Exception as exc:
        logger.warning("game21 rules translation failed: %s", exc)
        return {}

    out: dict[str, str] = {}
    for code in TARGET_LANGS:
        value = data.get(code)
        if isinstance(value, str) and value.strip():
            out[code] = value.strip()
    return out
