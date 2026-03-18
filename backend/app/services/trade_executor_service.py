from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.config import get_settings
from app.providers.base import TradeExecutionProvider
from app.repositories.hourly_digest_repository import HourlyDigestRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.trade_repository import TradeRepository


@dataclass
class TradeDecision:
    symbol: str
    action: str
    side: str | None = None
    signal_type: str | None = None
    reason: str | None = None
    digest_row: dict | None = None


class TradeExecutorService:
    def __init__(
        self,
        token_repository: TokenRepository,
        hourly_digest_repository: HourlyDigestRepository,
        trade_repository: TradeRepository,
        trade_provider: TradeExecutionProvider,
    ) -> None:
        self.settings = get_settings()
        self.token_repository = token_repository
        self.hourly_digest_repository = hourly_digest_repository
        self.trade_repository = trade_repository
        self.trade_provider = trade_provider

    async def run(self) -> dict:
        latest_run = self.hourly_digest_repository.latest_run_within_window(self.settings.trade_execution_grace_minutes)
        if latest_run is None:
            return {"status": "skipped", "reason": "missing_recent_digest"}

        run_rows = self.hourly_digest_repository.rows_for_run(latest_run["id"])
        rows_by_symbol = {row["symbol"]: row for row in run_rows}
        results: list[dict] = []

        for symbol in self.settings.trade_executor_symbol_list:
            latest_row = rows_by_symbol.get(symbol)
            decision = self._decide(symbol, latest_row)
            if decision.action == "skip":
                results.append({"symbol": symbol, "action": "skip", "reason": decision.reason})
                continue
            if decision.action == "close":
                results.append(await self._close_position(symbol, decision.reason or "expired"))
                continue
            results.append(await self._open_position(decision))

        return {"status": "completed", "run_id": latest_run["id"], "results": results}

    def _decide(self, symbol: str, latest_row: dict | None) -> TradeDecision:
        open_position = self.trade_repository.latest_open_position_for_symbol(symbol)
        if open_position is not None and self._position_expired(open_position):
            side = str(open_position["side"])
            return TradeDecision(symbol=symbol, action="close", side=side, reason="hold_window_expired")
        if open_position is not None:
            return TradeDecision(symbol=symbol, action="skip", reason="existing_open_position")
        if latest_row is None:
            return TradeDecision(symbol=symbol, action="skip", reason="missing_digest_row")
        if latest_row.get("status") != "ok":
            return TradeDecision(symbol=symbol, action="skip", reason=f"digest_status_{latest_row.get('status')}")
        if not latest_row.get("verified") or latest_row.get("mode") != "live":
            return TradeDecision(symbol=symbol, action="skip", reason="digest_not_live")

        recent_rows = self.hourly_digest_repository.recent_rows_for_symbol(
            symbol,
            limit=max(self.settings.trade_signal_confirmations + 2, 6),
        )
        confirmed_row = self._confirmed_row(recent_rows)
        if confirmed_row is None:
            return TradeDecision(symbol=symbol, action="skip", reason="confirmation_not_met")

        side = _signal_to_side(str(confirmed_row["signal_type"]))
        if side is None:
            return TradeDecision(symbol=symbol, action="skip", reason="non_trade_signal")
        return TradeDecision(
            symbol=symbol,
            action="open",
            side=side,
            signal_type=str(confirmed_row["signal_type"]),
            digest_row=confirmed_row,
        )

    async def _open_position(self, decision: TradeDecision) -> dict:
        assert decision.side is not None
        assert decision.signal_type is not None
        assert decision.digest_row is not None
        token = self.token_repository.get_by_symbol(decision.symbol)
        if token is None:
            return {"symbol": decision.symbol, "action": "skip", "reason": "missing_token"}

        leverage = self.settings.trade_leverage_by_symbol.get(decision.symbol, self.settings.trade_default_leverage)
        notional_usd = self.settings.trade_notional_usd_by_symbol.get(
            decision.symbol,
            self.settings.trade_default_notional_usd,
        )

        leverage_result = await self.trade_provider.configure_leverage(decision.symbol, leverage)
        open_result = await self.trade_provider.open_position(
            symbol=decision.symbol,
            side=decision.side,
            notional_usd=notional_usd,
            leverage=leverage,
            stop_loss_pct=self.settings.trade_stop_loss_pct,
        )

        position = None
        provider_status = str(open_result.get("status", "unknown"))
        if _provider_open_committed(provider_status):
            position = self.trade_repository.create_position(
                {
                    "id": str(uuid4()),
                    "token_id": token["id"],
                    "symbol": decision.symbol,
                    "side": decision.side,
                    "signal_type": decision.signal_type,
                    "source_digest_row_id": decision.digest_row.get("id"),
                    "entry_price": float(decision.digest_row.get("price", 0.0) or 0.0),
                    "entry_notional_usd": notional_usd,
                    "leverage": leverage,
                    "status": "open",
                    "opened_at": datetime.now(timezone.utc).isoformat(),
                }
            )
        self.trade_repository.insert_execution_log(
            {
                "position_id": position["id"] if position else None,
                "symbol": decision.symbol,
                "action": "open",
                "status": provider_status,
                "provider_order_id": str(open_result.get("order_id", "")) or None,
                "request_json": {
                    "symbol": decision.symbol,
                    "side": decision.side,
                    "notional_usd": notional_usd,
                    "leverage": leverage,
                    "stop_loss_pct": self.settings.trade_stop_loss_pct,
                },
                "response_json": {
                    "configure_leverage": leverage_result,
                    "open_position": open_result,
                },
            }
        )
        return {
            "symbol": decision.symbol,
            "action": "open" if position else "preview",
            "side": decision.side,
            "leverage": leverage,
            "notional_usd": notional_usd,
            "provider_status": provider_status,
        }

    async def _close_position(self, symbol: str, reason: str) -> dict:
        open_position = self.trade_repository.latest_open_position_for_symbol(symbol)
        if open_position is None:
            return {"symbol": symbol, "action": "skip", "reason": "missing_open_position"}

        close_result = await self.trade_provider.close_position(symbol=symbol, side=str(open_position["side"]))
        provider_status = str(close_result.get("status", "unknown"))
        if _provider_close_committed(provider_status):
            self.trade_repository.close_position(
                str(open_position["id"]),
                {
                    "status": "closed",
                    "close_reason": reason,
                    "closed_at": datetime.now(timezone.utc).isoformat(),
                },
            )
        self.trade_repository.insert_execution_log(
            {
                "position_id": open_position["id"],
                "symbol": symbol,
                "action": "close",
                "status": provider_status,
                "provider_order_id": str(close_result.get("order_id", "")) or None,
                "request_json": {"symbol": symbol, "reason": reason},
                "response_json": close_result,
            }
        )
        return {
            "symbol": symbol,
            "action": "close" if _provider_close_committed(provider_status) else "preview_close",
            "reason": reason,
            "provider_status": provider_status,
        }

    def _confirmed_row(self, recent_rows: list[dict]) -> dict | None:
        eligible = [
            row
            for row in recent_rows
            if row.get("status") == "ok" and row.get("verified") and row.get("mode") == "live"
        ]
        if len(eligible) < self.settings.trade_signal_confirmations:
            return None
        target = eligible[0]
        signal_type = str(target.get("signal_type", ""))
        if _signal_to_side(signal_type) is None:
            return None
        confirmations = 1
        for row in eligible[1:]:
            if str(row.get("signal_type", "")) == signal_type:
                confirmations += 1
                if confirmations >= self.settings.trade_signal_confirmations:
                    return target
            else:
                break
        return None

    def _position_expired(self, position: dict) -> bool:
        opened_at = datetime.fromisoformat(str(position["opened_at"]).replace("Z", "+00:00")).astimezone(timezone.utc)
        expires_at = opened_at + timedelta(hours=self.settings.trade_hold_hours)
        return datetime.now(timezone.utc) >= expires_at


def _signal_to_side(signal_type: str) -> str | None:
    mapping = {
        "hidden_accumulation": "long",
        "narrative_ignition": "long",
        "retail_trap": "short",
    }
    return mapping.get(signal_type)


def _provider_open_committed(status: str) -> bool:
    return status in {"opened", "submitted", "filled", "success"}


def _provider_close_committed(status: str) -> bool:
    return status in {"closed", "submitted", "filled", "success"}
