from typing import Any

import httpx

from app.core.config import get_settings
from app.providers.base import TelegramProvider


class TelegramBotProvider(TelegramProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    async def send_signal_alert(self, chat_id: str, message: str) -> dict[str, Any]:
        if not self.settings.telegram_bot_token:
            return {"status": "skipped", "reason": "missing_bot_token"}

        url = (
            f"https://api.telegram.org/bot{self.settings.telegram_bot_token}/sendMessage"
        )
        last_error: str | None = None
        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(3):
                try:
                    response = await client.post(url, json={"chat_id": chat_id, "text": message})
                    response.raise_for_status()
                    return response.json()
                except (httpx.ConnectError, httpx.ReadTimeout, httpx.RemoteProtocolError) as exc:
                    last_error = f"{type(exc).__name__}: {exc}".strip()
                    if attempt == 2:
                        break
            return {"status": "failed", "reason": last_error or "telegram_send_failed"}


class NoopTelegramProvider(TelegramProvider):
    async def send_signal_alert(self, chat_id: str, message: str) -> dict[str, Any]:
        return {
            "status": "skipped",
            "reason": "missing_bot_token",
            "chat_id": chat_id,
            "message_preview": message[:80],
        }
