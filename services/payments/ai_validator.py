"""AI-валидация писем: распознаёт банковские транзакции и извлекает поля."""

from __future__ import annotations

import html as html_module
import json
import logging
import re
from html.parser import HTMLParser
from typing import Any

from services.payments.ai_clients.base import AIClient

logger = logging.getLogger(__name__)


# ── HTML → plain text ────────────────────────────────────────────────────────


class _HTMLStripper(HTMLParser):
    _SKIP_TAGS = {"script", "style", "head"}

    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1
        elif tag in {"br", "p", "div", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "li"}:
            self._parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._parts.append(data)

    def get_text(self) -> str:
        raw = "".join(self._parts)
        raw = html_module.unescape(raw)
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def _html_to_text(html: str) -> str:
    stripper = _HTMLStripper()
    try:
        stripper.feed(html)
        return stripper.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html)


# ── Prompt ────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """\
You are a financial email analyzer. Your only job is to decide if an email is a bank transaction notification and extract its data.

If it IS a bank transaction (any bank, any country — credit, debit, transfer, payment confirmation, card charge, etc.), respond with JSON:
{"is_bank_transaction": true, "konto": "<account number or IBAN, or null>", "amount": <number, positive=credit negative=debit, or null>, "currency": "<ISO code e.g. PLN USD EUR, or null>", "title": "<full transaction title, see rules below>", "transaction_date": "<YYYY-MM-DD or null>", "balance_after": <number or null>}

If it is NOT a bank transaction, respond with JSON:
{"is_bank_transaction": false}

Rules for the "title" field:
- Extract the full transaction title / description / transfer reason as it appears in the email.
- The title may be split across multiple lines or HTML elements — join them into a single string with a space, do NOT truncate.
- If the title or anywhere in the email body contains a code matching the pattern TRN or TFN followed by exactly 6 digits (e.g. TRN000001, TFN000042), you MUST include that code verbatim in the title string. This is critical — never omit or alter it.
- If no title/description is present, use null.

Respond with ONLY the JSON object. No markdown, no explanation."""

_USER_TEMPLATE = """\
Subject: {subject}
From: {sender}
Date: {date}
Body:
{body}"""


async def validate_and_extract(
    message: dict[str, Any], ai_client: AIClient
) -> dict[str, Any] | None:
    """Вернёт dict с извлечёнными полями, либо None если не транзакция / ошибка."""
    body_html = message.get("body_html") or ""
    body_plain = message.get("body_plain") or message.get("body") or ""
    body = _html_to_text(body_html) if body_html else body_plain
    if isinstance(body, list):
        body = "\n".join(body)
    body = body[:6000]

    user_content = _USER_TEMPLATE.format(
        subject=message.get("subject", ""),
        sender=message.get("from", ""),
        date=message.get("date", ""),
        body=body,
    )

    try:
        provider = type(ai_client).__name__
        logger.debug("AI request — provider=%s prompt_len=%d", provider, len(user_content))
        raw_text = await ai_client.chat(_SYSTEM_PROMPT, user_content)
        if not raw_text:
            logger.warning("AI returned empty response")
            return None
        logger.debug("AI raw response: %s", raw_text)
        data: dict = json.loads(raw_text)
    except Exception as exc:
        logger.error("AI validation failed (%s: %s)", type(exc).__name__, exc, exc_info=True)
        return None

    if not data.get("is_bank_transaction"):
        return None

    return {
        "account_number": data.get("konto"),
        "amount": _to_float(data.get("amount")),
        "currency": data.get("currency"),
        "title": data.get("title"),
        "transaction_date": data.get("transaction_date"),
        "balance_after": _to_float(data.get("balance_after")),
    }


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
