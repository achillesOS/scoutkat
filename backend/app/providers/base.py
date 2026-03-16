from abc import ABC, abstractmethod
from typing import Any


class HyperliquidProvider(ABC):
    @abstractmethod
    async def fetch_market_snapshot(self, symbol: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def fetch_positioning_snapshot(self, symbol: str) -> dict[str, Any]:
        raise NotImplementedError


class GrokProvider(ABC):
    @abstractmethod
    async def fetch_social_summary(self, token_symbol: str, time_window: str) -> dict[str, Any]:
        raise NotImplementedError


class TelegramProvider(ABC):
    @abstractmethod
    async def send_signal_alert(self, chat_id: str, message: str) -> dict[str, Any]:
        raise NotImplementedError
