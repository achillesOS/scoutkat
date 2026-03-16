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
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json={"chat_id": chat_id, "text": message})
            response.raise_for_status()
            return response.json()


class MockTelegramProvider(TelegramProvider):
    async def send_signal_alert(self, chat_id: str, message: str) -> dict[str, Any]:
        return {"status": "queued", "chat_id": chat_id, "message_preview": message[:80]}

