from __future__ import annotations

from decimal import Decimal, ROUND_DOWN
from typing import Any

from eth_account import Account
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info

from app.core.config import get_settings
from app.providers.base import TradeExecutionProvider


class HyperliquidTradeProvider(TradeExecutionProvider):
    MIN_ORDER_VALUE_USD = 10.0

    def __init__(self) -> None:
        self.settings = get_settings()
        self.info = Info(self.settings.hyperliquid_api_url, skip_ws=True)
        self.exchange = None
        if self._configured():
            self.exchange = Exchange(
                wallet=Account.from_key(self.settings.hl_agent_private_key),
                base_url=self.settings.hyperliquid_api_url,
                account_address=self.settings.hl_master_wallet_address,
            )

    async def configure_leverage(self, symbol: str, leverage: float) -> dict[str, Any]:
        if not self.exchange:
            return self._skipped("configure_leverage", symbol)
        is_cross = self.settings.trade_margin_mode == "cross"
        response = self.exchange.update_leverage(int(leverage), symbol.upper(), is_cross=is_cross)
        return {
            "status": "success" if response.get("status") == "ok" else "failed",
            "symbol": symbol.upper(),
            "leverage": leverage,
            "margin_mode": self.settings.trade_margin_mode,
            "response": response,
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
        if not self.exchange:
            return self._skipped("open_position", symbol)

        is_buy = side == "long"
        price = float(self.info.all_mids().get(symbol.upper(), 0.0) or 0.0)
        if price <= 0:
            return {"status": "failed", "reason": "missing_mid_price", "symbol": symbol.upper()}

        size = self._size_for_notional(symbol.upper(), notional_usd, price)
        order_value_usd = size * price
        if size <= 0 or order_value_usd < self.MIN_ORDER_VALUE_USD:
            return {
                "status": "failed",
                "reason": "order_below_exchange_minimum",
                "symbol": symbol.upper(),
                "size": size,
                "entry_price_reference": price,
                "order_value_usd": round(order_value_usd, 4),
                "minimum_order_value_usd": self.MIN_ORDER_VALUE_USD,
            }

        leverage_response = self.exchange.update_leverage(
            int(leverage),
            symbol.upper(),
            is_cross=(margin_mode == "cross"),
        )
        order_response = self.exchange.market_open(symbol.upper(), is_buy=is_buy, sz=size)
        order_error = _extract_order_error(order_response)
        if order_response.get("status") != "ok" or order_error:
            return {
                "status": "failed",
                "symbol": symbol.upper(),
                "side": side,
                "size": size,
                "entry_price_reference": price,
                "leverage_response": leverage_response,
                "order_response": order_response,
                "reason": order_error or "order_rejected",
            }

        stop_response = self._place_stop_loss(
            symbol=symbol.upper(),
            side=side,
            size=size,
            entry_price=price,
            stop_loss_pct=stop_loss_pct,
        )
        stop_error = _extract_order_error(stop_response.get("response", {}))
        status = "opened_stop_failed" if stop_error else "opened"
        return {
            "status": status,
            "symbol": symbol.upper(),
            "side": side,
            "size": size,
            "entry_price_reference": price,
            "order_value_usd": round(order_value_usd, 4),
            "leverage_response": leverage_response,
            "order_response": order_response,
            "stop_response": stop_response,
            "reason": stop_error,
        }

    async def close_position(self, *, symbol: str, side: str) -> dict[str, Any]:
        if not self.exchange:
            return self._skipped("close_position", symbol)
        response = self.exchange.market_close(symbol.upper())
        return {
            "status": "closed" if response.get("status") == "ok" and not _extract_order_error(response) else "failed",
            "symbol": symbol.upper(),
            "side": side,
            "reason": _extract_order_error(response),
            "response": response,
        }

    async def get_open_positions(self, symbols: list[str] | None = None) -> list[dict[str, Any]]:
        if not self._configured():
            return []
        state = self.info.user_state(self.settings.hl_master_wallet_address or "")
        positions = []
        allowed = {symbol.upper() for symbol in symbols} if symbols else None
        for row in state.get("assetPositions", []):
            position = row.get("position", {})
            symbol = str(position.get("coin", "")).upper()
            if allowed and symbol not in allowed:
                continue
            size = float(position.get("szi", 0.0) or 0.0)
            if size == 0:
                continue
            positions.append(
                {
                    "symbol": symbol,
                    "side": "long" if size > 0 else "short",
                    "size": abs(size),
                    "entry_price": float(position.get("entryPx", 0.0) or 0.0),
                    "position_value": float(position.get("positionValue", 0.0) or 0.0),
                    "unrealized_pnl": float(position.get("unrealizedPnl", 0.0) or 0.0),
                    "roe": float(position.get("returnOnEquity", 0.0) or 0.0),
                    "liquidation_price": float(position.get("liquidationPx", 0.0) or 0.0),
                    "margin_mode": str(position.get("leverage", {}).get("type", "")),
                    "leverage": float(position.get("leverage", {}).get("value", 0.0) or 0.0),
                }
            )
        return positions

    async def get_account_summary(self) -> dict[str, Any]:
        if not self._configured():
            return {"account_value": 0.0, "withdrawable": 0.0, "positions": []}
        state = self.info.user_state(self.settings.hl_master_wallet_address or "")
        margin_summary = state.get("marginSummary", {})
        return {
            "account_value": float(margin_summary.get("accountValue", 0.0) or 0.0),
            "withdrawable": float(state.get("withdrawable", 0.0) or 0.0),
            "positions": await self.get_open_positions(),
        }

    def _place_stop_loss(self, *, symbol: str, side: str, size: float, entry_price: float, stop_loss_pct: float) -> dict[str, Any]:
        if not self.exchange:
            return self._skipped("place_stop_loss", symbol)
        raw_trigger_price = entry_price * (1 - stop_loss_pct) if side == "long" else entry_price * (1 + stop_loss_pct)
        is_buy = side == "short"
        trigger_price = self._normalize_price(symbol, raw_trigger_price)
        raw_limit_price = trigger_price * (1.03 if is_buy else 0.97)
        limit_price = self._normalize_price(symbol, raw_limit_price)
        response = self.exchange.order(
            symbol,
            is_buy=is_buy,
            sz=size,
            limit_px=limit_price,
            order_type={"trigger": {"triggerPx": trigger_price, "isMarket": True, "tpsl": "sl"}},
            reduce_only=True,
        )
        return {
            "status": "submitted" if response.get("status") == "ok" and not _extract_order_error(response) else "failed",
            "trigger_price": trigger_price,
            "limit_price": limit_price,
            "response": response,
        }

    def _normalize_price(self, symbol: str, price: float) -> float:
        asset = self.exchange.info.coin_to_asset[symbol.upper()]
        is_spot = asset >= 10_000
        decimals = (8 if is_spot else 6) - self.exchange.info.asset_to_sz_decimals[asset]
        return round(float(f"{price:.5g}"), decimals)

    def _size_for_notional(self, symbol: str, notional_usd: float, price: float) -> float:
        decimals = self._sz_decimals(symbol)
        raw_size = Decimal(str(notional_usd)) / Decimal(str(price))
        quantum = Decimal("1").scaleb(-decimals)
        return float(raw_size.quantize(quantum, rounding=ROUND_DOWN))

    def _sz_decimals(self, symbol: str) -> int:
        meta = self.info.meta()
        for item in meta.get("universe", []):
            if item.get("name") == symbol.upper():
                return int(item.get("szDecimals", 0))
        return 0

    def _configured(self) -> bool:
        return bool(self.settings.hl_master_wallet_address and self.settings.hl_agent_private_key)

    def _skipped(self, action: str, symbol: str) -> dict[str, Any]:
        return {
            "status": "skipped",
            "reason": "missing_hl_trade_credentials",
            "action": action,
            "symbol": symbol.upper(),
        }


def _extract_order_error(response: dict[str, Any] | None) -> str | None:
    if not response:
        return None
    payload = response.get("response", {})
    data = payload.get("data", {})
    statuses = data.get("statuses", [])
    for status in statuses:
        if isinstance(status, dict) and status.get("error"):
            return str(status["error"])
    return None
