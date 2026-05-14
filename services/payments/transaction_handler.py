"""Обработка нового письма: raw → AI → транзакция → матчинг ордера → баланс."""

import logging
import re
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.models.payment_log import PaymentLogMethod
from database.models.payments.account import MBankAccount
from database.models.payments.order import MBankOrder, MBankOrderStatus
from database.models.payments.raw_email import MBankRawEmail
from database.models.payments.transaction import MBankTransaction
from database.models.user import User
from database.repositories import payment_logs as payment_logs_repo
from locales.texts import t
from services.payments import limit_service
from services.payments.ai_clients.base import AIClient
from services.payments.ai_validator import validate_and_extract
from settings import Settings

logger = logging.getLogger(__name__)

_REQUIRED_FIELDS = (
    "account_number",
    "amount",
    "title",
    "transaction_date",
    "balance_after",
)
_ORDER_ID_RE = re.compile(r"\b(?:TRN|TFN)\d{6}\b")


class BankTransactionHandler:
    """Принимает письма от IMAP-монитора и доводит их до пополнения баланса юзера."""

    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
        ai_client: AIClient,
        bot: Optional[Bot] = None,
        settings: Optional[Settings] = None,
    ) -> None:
        self._session_maker = session_maker
        self._ai_client = ai_client
        self._bot = bot
        self._settings = settings

    async def on_new_message(
        self, account_email: str, uid: int, message: dict[str, Any]
    ) -> None:
        subject = message.get("subject", "(no subject)")
        logger.debug("[%s] UID=%d subject=%r", account_email, uid, subject)

        raw_email = await self._save_raw_email(account_email, uid, message)
        if raw_email is None:
            logger.debug("[%s] UID=%d already stored, skipping", account_email, uid)
            return

        extracted = await validate_and_extract(message, self._ai_client)
        if extracted is None:
            logger.debug("[%s] UID=%d — not a bank transaction", account_email, uid)
            return

        txn = await self._save_transaction(
            account_email, uid, message, raw_email.id, extracted
        )
        if txn is None:
            return

        if txn.balance_after is not None:
            await self._update_account_balance(account_email, txn.balance_after)

        matched_order = await self._match_order(txn)

        amount = txn.amount or Decimal("0.00")
        if amount > 0:
            async with self._session_maker() as session:
                account = await session.scalar(
                    select(MBankAccount).where(MBankAccount.email == account_email)
                )
                if account and account.daily_limit is not None:
                    should_count = account.limit_type == "all" or (
                        account.limit_type == "matched" and matched_order is not None
                    )
                    if should_count:
                        await limit_service.add_usage_and_check(
                            self._session_maker, account_email, amount
                        )

    # ── Внутренности ──────────────────────────────────────────────────────────

    async def _save_raw_email(
        self, account_email: str, uid: int, message: dict[str, Any]
    ) -> MBankRawEmail | None:
        body_html = message.get("body_html") or ""
        body_plain = message.get("body_plain") or message.get("body") or ""
        if isinstance(body_plain, list):
            body_plain = "\n".join(body_plain)

        record = MBankRawEmail(
            account_email=account_email,
            uid=uid,
            sender=message.get("from"),
            subject=message.get("subject"),
            date=message.get("date"),
            body_plain=body_plain[:16000] if body_plain else None,
            body_html=body_html[:32000] if body_html else None,
        )

        async with self._session_maker() as session:
            try:
                session.add(record)
                await session.commit()
                await session.refresh(record)
                logger.debug(
                    "[%s] UID=%d raw email saved id=%d",
                    account_email,
                    uid,
                    record.id,
                )
                return record
            except IntegrityError:
                await session.rollback()
                return None

    async def _save_transaction(
        self,
        account_email: str,
        uid: int,
        message: dict[str, Any],
        email_id: int,
        extracted: dict[str, Any],
    ) -> MBankTransaction | None:
        subject = message.get("subject", "(no subject)")
        body = message.get("body") or ""
        if isinstance(body, list):
            body = "\n".join(body)

        missing = [f for f in _REQUIRED_FIELDS if extracted.get(f) is None]
        needs_review = bool(missing)

        # amount/balance_after из AI приходят как float — кладём в Numeric как Decimal
        amount = extracted.get("amount")
        balance_after = extracted.get("balance_after")

        tx = MBankTransaction(
            email_id=email_id,
            account_email=account_email,
            uid=uid,
            sender=message.get("from"),
            subject=subject,
            raw_body=body[:8000] if body else None,
            needs_review=needs_review,
            missing_fields=",".join(missing) if missing else None,
            account_number=extracted.get("account_number"),
            amount=Decimal(str(amount)) if amount is not None else None,
            currency=extracted.get("currency"),
            title=extracted.get("title"),
            transaction_date=extracted.get("transaction_date"),
            balance_after=Decimal(str(balance_after)) if balance_after is not None else None,
        )

        async with self._session_maker() as session:
            session.add(tx)
            await session.commit()
            await session.refresh(tx)

        if needs_review:
            logger.warning(
                "[%s] UID=%d TRANSACTION id=%d needs review — missing: %s",
                account_email,
                uid,
                tx.id,
                ", ".join(missing),
            )
        else:
            logger.info(
                "[%s] UID=%d TRANSACTION id=%d  amount=%s %s  account=%s",
                account_email,
                uid,
                tx.id,
                tx.amount,
                tx.currency,
                tx.account_number,
            )
        return tx

    async def _match_order(self, txn: MBankTransaction) -> MBankOrder | None:
        """Если в title есть TRN###### — матчим pending-ордер и пополняем юзера."""
        if not txn.title:
            return None
        match = _ORDER_ID_RE.search(txn.title)
        if not match:
            return None

        order_id = match.group(0)

        async with self._session_maker() as session:
            order = await session.get(MBankOrder, order_id)
            if order is None or order.status != MBankOrderStatus.PENDING:
                return None

            order.status = MBankOrderStatus.MATCHED
            order.bank_transaction_id = txn.id
            order.actual_amount = txn.amount
            order.updated_at = datetime.now(timezone.utc)
            await session.commit()
            await session.refresh(order)

            logger.info("Order %s matched to transaction id=%d", order_id, txn.id)

            # Зачисляем баланс юзеру + completed
            credited_user_id: int | None = None
            credited_amount = txn.amount or order.amount
            user_lang: str | None = None
            credited_user: User | None = None
            if order.user_id is not None and credited_amount and credited_amount > 0:
                credited_user = await session.get(User, order.user_id)
                if credited_user is not None:
                    credited_user.balance = (
                        credited_user.balance or Decimal("0.00")
                    ) + credited_amount
                    await session.flush()
                    await payment_logs_repo.log(
                        session,
                        user_id=order.user_id,
                        method=PaymentLogMethod.TOPUP,
                        amount=credited_amount,
                        balance_after=credited_user.balance,
                    )
                    user_lang = credited_user.language_code
                    credited_user_id = order.user_id

            order.status = MBankOrderStatus.COMPLETED
            order.updated_at = datetime.now(timezone.utc)
            await session.commit()

            logger.info(
                "Order %s completed (user_id=%s, credited=%s)",
                order_id,
                credited_user_id,
                credited_amount,
            )

        if credited_user_id is not None and self._bot is not None and credited_amount:
            kb = InlineKeyboardMarkup(
                inline_keyboard=[[
                    InlineKeyboardButton(
                        text=t("btn_main", user_lang),
                        callback_data="menu:main",
                        style="primary",
                    )
                ]]
            )
            try:
                await self._bot.send_message(
                    credited_user_id,
                    f"✅ Баланс пополнен на <b>{credited_amount} PLN</b>\n"
                    f"Ордер: <code>{order_id}</code>",
                    reply_markup=kb,
                )
            except Exception as exc:
                logger.warning(
                    "Failed to notify user_id=%s about order %s: %s",
                    credited_user_id,
                    order_id,
                    exc,
                )

            # Уведомление в админ-чат
            await self._notify_admin_chat(credited_user, credited_amount, order_id)

        return order

    async def _notify_admin_chat(
        self,
        user: User | None,
        amount: Decimal,
        order_id: str,
    ) -> None:
        if (
            self._bot is None
            or self._settings is None
            or self._settings.admin_chat is None
        ):
            return

        if user is not None:
            mention = f'<a href="tg://user?id={user.user_id}">'
            display_name = user.name or user.user_name or str(user.user_id)
            mention += f"{display_name}</a>"
            username = f" (@{user.user_name})" if user.user_name else ""
            user_line = f"👤 {mention}{username}\n🆔 <code>{user.user_id}</code>"
        else:
            user_line = "👤 —"

        text = (
            "💰 <b>Новое пополнение</b>\n\n"
            f"{user_line}\n"
            f"💵 Сумма: <b>{amount} PLN</b>\n"
            f"🧾 Ордер: <code>{order_id}</code>"
        )

        try:
            await self._bot.send_message(self._settings.admin_chat, text)
        except Exception as exc:
            logger.warning(
                "Failed to notify admin_chat=%s about order %s: %s",
                self._settings.admin_chat,
                order_id,
                exc,
            )

    async def _update_account_balance(
        self, account_email: str, balance: Decimal
    ) -> None:
        async with self._session_maker() as session:
            await session.execute(
                update(MBankAccount)
                .where(MBankAccount.email == account_email)
                .values(
                    balance=balance,
                    balance_updated_at=datetime.now(timezone.utc),
                )
            )
            await session.commit()
