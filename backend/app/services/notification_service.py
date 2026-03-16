from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import get_settings
from app.providers.base import TelegramProvider
from app.repositories.notification_repository import NotificationRepository
from app.repositories.user_repository import UserRepository


class NotificationService:
    def __init__(
        self,
        telegram_provider: TelegramProvider,
        notification_repository: NotificationRepository,
        user_repository: UserRepository,
    ) -> None:
        self.settings = get_settings()
        self.telegram_provider = telegram_provider
        self.notification_repository = notification_repository
        self.user_repository = user_repository

    async def notify_signal(self, signal_event: dict, token_symbol: str, explanation: dict) -> dict | None:
        default_user = self.user_repository.get_or_create_default_user()
        if not default_user:
            return None

        chat_id = default_user.get("telegram_chat_id") or self.settings.telegram_default_chat_id
        status = "skipped"
        provider_result: dict | None = None

        if chat_id:
            message = self._format_message(token_symbol, signal_event, explanation)
            provider_result = await self.telegram_provider.send_signal_alert(chat_id, message)
            status = str(provider_result.get("status", "sent"))
        else:
            status = "skipped_missing_chat_id"

        return self.notification_repository.insert_log(
            {
                "user_id": default_user["id"],
                "signal_event_id": signal_event["id"],
                "channel": "telegram",
                "sent_at": datetime.now(timezone.utc).isoformat(),
                "delivery_status": status,
            }
        )

    def _format_message(self, token_symbol: str, signal_event: dict, explanation: dict) -> str:
        return "\n".join(
            [
                f"Scoutkat alert: {token_symbol}",
                f"Type: {signal_event['signal_type']}",
                f"Score: {signal_event['signal_score']}",
                f"Confidence: {round(float(signal_event['confidence']) * 100)}%",
                f"Why now: {explanation.get('why_now', '')}",
                f"Action: {explanation.get('suggested_action', '')}",
            ]
        )
