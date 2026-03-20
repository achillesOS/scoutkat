from __future__ import annotations

from datetime import datetime, timedelta, timezone
from statistics import median

from app.models.enums import SignalType
from app.repositories.signal_recorder_repository import SignalRecorderRepository
from app.repositories.signal_repository import SignalRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.token_repository import TokenRepository


class SignalRecorderService:
    HORIZONS_MINUTES = (10, 30, 60, 240)

    def __init__(
        self,
        token_repository: TokenRepository,
        signal_repository: SignalRepository,
        snapshot_repository: SnapshotRepository,
        signal_recorder_repository: SignalRecorderRepository,
    ) -> None:
        self.token_repository = token_repository
        self.signal_repository = signal_repository
        self.snapshot_repository = snapshot_repository
        self.signal_recorder_repository = signal_recorder_repository

    def run(self) -> dict:
        signals = self.signal_repository.list_signals()
        recorded = 0
        recommendations = 0

        for signal in signals:
            symbol = str(signal.get("token_symbol", "")).upper()
            if symbol == "" or symbol not in {"BTC", "SOL"}:
                continue
            if signal["signal_type"] == SignalType.NEUTRAL:
                continue
            token = self.token_repository.get_by_symbol(symbol)
            if token is None:
                continue
            recorded += self._record_signal_outcomes(token["id"], symbol, signal)

        for symbol in ("BTC", "SOL"):
            for signal_type in (
                SignalType.HIDDEN_ACCUMULATION.value,
                SignalType.NARRATIVE_IGNITION.value,
                SignalType.RETAIL_TRAP.value,
            ):
                if self._write_optimizer_snapshot(symbol, signal_type):
                    recommendations += 1

        return {"status": "completed", "recorded_outcomes": recorded, "optimizer_updates": recommendations}

    def _record_signal_outcomes(self, token_id: str, symbol: str, signal: dict) -> int:
        triggered_at = _parse_datetime(signal["triggered_at"])
        now = datetime.now(timezone.utc)
        snapshots = self.snapshot_repository.market_snapshots_since(token_id, triggered_at.isoformat(), limit=500)
        if not snapshots:
            return 0

        entry_snapshot = snapshots[0]
        entry_price = float(entry_snapshot.get("mark_price", 0.0) or 0.0)
        if entry_price <= 0:
            return 0

        recorded = 0
        direction = _signal_direction(str(signal["signal_type"]))
        if direction == 0:
            return 0

        for horizon in self.HORIZONS_MINUTES:
            horizon_cutoff = triggered_at + timedelta(minutes=horizon)
            if now < horizon_cutoff:
                continue
            exit_snapshot = _first_snapshot_at_or_after(snapshots, horizon_cutoff) or snapshots[-1]
            exit_price = float(exit_snapshot.get("mark_price", 0.0) or 0.0)
            if exit_price <= 0:
                continue
            window_snapshots = [row for row in snapshots if _parse_datetime(row["timestamp"]) <= horizon_cutoff]
            if not window_snapshots:
                window_snapshots = [entry_snapshot, exit_snapshot]
            prices = [float(row.get("mark_price", 0.0) or 0.0) for row in window_snapshots if float(row.get("mark_price", 0.0) or 0.0) > 0]
            if not prices:
                continue

            raw_return_pct = ((exit_price - entry_price) / entry_price) * 100
            directional_return_pct = raw_return_pct * direction
            max_favorable_excursion_pct = max((((price - entry_price) / entry_price) * 100) * direction for price in prices)
            max_adverse_excursion_pct = min((((price - entry_price) / entry_price) * 100) * direction for price in prices)

            self.signal_recorder_repository.upsert_outcome_snapshot(
                {
                    "signal_event_id": signal["id"],
                    "token_id": token_id,
                    "symbol": symbol,
                    "signal_type": str(signal["signal_type"]),
                    "triggered_at": triggered_at.isoformat(),
                    "horizon_minutes": horizon,
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "raw_return_pct": round(raw_return_pct, 4),
                    "directional_return_pct": round(directional_return_pct, 4),
                    "max_favorable_excursion_pct": round(max_favorable_excursion_pct, 4),
                    "max_adverse_excursion_pct": round(max_adverse_excursion_pct, 4),
                    "outcome_label": _outcome_label(directional_return_pct),
                    "evaluated_at": now.isoformat(),
                }
            )
            recorded += 1
        return recorded

    def _write_optimizer_snapshot(self, symbol: str, signal_type: str) -> bool:
        outcomes = self.signal_recorder_repository.list_recent_outcomes(
            symbol=symbol,
            signal_type=signal_type,
            horizon_minutes=60,
            limit=40,
        )
        if len(outcomes) < 6:
            return False

        directional_returns = [float(row.get("directional_return_pct", 0.0) or 0.0) for row in outcomes]
        sample_size = len(directional_returns)
        wins = sum(1 for value in directional_returns if value > 0)
        win_rate = wins / sample_size
        avg_return = sum(directional_returns) / sample_size
        median_return = median(directional_returns)

        recommended_min_score = 60.0
        recommended_min_confidence = 0.65
        reason = "baseline"

        if win_rate < 0.45 or avg_return < 0:
            recommended_min_score += 5
            recommended_min_confidence += 0.05
            reason = "tighten_after_negative_expectancy"
        if win_rate < 0.35 or avg_return < -0.25:
            recommended_min_score += 5
            recommended_min_confidence += 0.05
            reason = "tighten_hard_after_persistent_losses"
        if win_rate > 0.58 and avg_return > 0.25:
            recommended_min_score -= 3
            recommended_min_confidence -= 0.03
            reason = "loosen_after_positive_expectancy"

        self.signal_recorder_repository.insert_optimizer_snapshot(
            {
                "symbol": symbol,
                "signal_type": signal_type,
                "horizon_minutes": 60,
                "sample_size": sample_size,
                "win_rate": round(win_rate, 4),
                "avg_directional_return_pct": round(avg_return, 4),
                "median_directional_return_pct": round(median_return, 4),
                "recommended_min_score": round(max(recommended_min_score, 55.0), 2),
                "recommended_min_confidence": round(min(max(recommended_min_confidence, 0.55), 0.9), 2),
                "recommendation_reason": reason,
            }
        )
        return True


def _parse_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)


def _first_snapshot_at_or_after(rows: list[dict], target: datetime) -> dict | None:
    for row in rows:
        if _parse_datetime(row["timestamp"]) >= target:
            return row
    return None


def _signal_direction(signal_type: str) -> int:
    if signal_type in {SignalType.HIDDEN_ACCUMULATION.value, SignalType.NARRATIVE_IGNITION.value}:
        return 1
    if signal_type == SignalType.RETAIL_TRAP.value:
        return -1
    return 0


def _outcome_label(directional_return_pct: float) -> str:
    if directional_return_pct > 0.25:
        return "win"
    if directional_return_pct < -0.25:
        return "loss"
    return "flat"
