from __future__ import annotations

from typing import Any

from app.core.config import get_settings
from app.providers.base import TradeExecutionProvider


class HyperliquidTradeProvider(TradeExecutionProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    async def configure_leverage(self, symbol: str, leverage: float) -> dict[str, Any]:
        if not self._configured():
            return {
                "status": "skipped",
                "reason": "missing_hl_trade_credentials",
                "symbol": symbol.upper(),
                "leverage": leverage,
            }
        return {
            "status": "pending_provider_integration",
            "symbol": symbol.upper(),
            "leverage": leverage,
        }

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
        if not self._configured():
            return {
                "status": "skipped",
                "reason": "missing_hl_trade_credentials",
                "symbol": symbol.upper(),
                "side": side,
            }
        return {
            "status": "pending_provider_integration",
            "symbol": symbol.upper(),
            "side": side,
            "notional_usd": notional_usd,
            "leverage": leverage,
            "margin_mode": margin_mode,
            "stop_loss_pct": stop_loss_pct,
        }

    async def close_position(self, *, symbol: str, side: str) -> dict[str, Any]:
        if not self._configured():
            return {
                "status": "skipped",
                "reason": "missing_hl_trade_credentials",
                "symbol": symbol.upper(),
                "side": side,
            }
        return {
            "status": "pending_provider_integration",
            "symbol": symbol.upper(),
            "side": side,
        }

    def _configured(self) -> bool:
        return bool(self.settings.hl_master_wallet_address and self.settings.hl_agent_private_key)
