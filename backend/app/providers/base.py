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


class TradeExecutionProvider(ABC):
    @abstractmethod
    async def configure_leverage(self, symbol: str, leverage: float) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def open_position(
        self,
        *,
        symbol: str,
        side: str,
        notional_usd: float,
        leverage: float,
        margin_mode: str,
        stop_loss_pct: float,
    ) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def close_position(self, *, symbol: str, side: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_open_positions(self, symbols: list[str] | None = None) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    async def get_account_summary(self) -> dict[str, Any]:
        raise NotImplementedError
