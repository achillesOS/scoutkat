from datetime import datetime, timedelta, timezone

from app.scoring.normalization import zscore

from app.providers.base import HyperliquidProvider
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.token_repository import TokenRepository


class MarketIngestionService:
    def __init__(
        self,
        token_repository: TokenRepository,
        snapshot_repository: SnapshotRepository,
        hyperliquid_provider: HyperliquidProvider,
    ) -> None:
        self.token_repository = token_repository
        self.snapshot_repository = snapshot_repository
        self.hyperliquid_provider = hyperliquid_provider

    async def ingest_tracked_tokens(self, symbols: list[str]) -> list[dict]:
        tokens = self.token_repository.get_by_symbols(symbols)
        results: list[dict] = []
        for token in tokens:
            market_snapshot = await self.hyperliquid_provider.fetch_market_snapshot(token["symbol"])
            positioning_snapshot = await self.hyperliquid_provider.fetch_positioning_snapshot(token["symbol"])
            market_history = self.snapshot_repository.recent_market_snapshots(token["id"], limit=96)
            positioning_history = self.snapshot_repository.recent_positioning_snapshots(token["id"], limit=96)

            snapshot_timestamp = _as_utc_datetime(market_snapshot["timestamp"])
            market_snapshot["return_1h"] = _return_over_window(
                current_price=float(market_snapshot["mark_price"]),
                history=market_history,
                snapshot_timestamp=snapshot_timestamp,
                window=timedelta(hours=1),
                fallback=float(market_snapshot.get("return_1h", 0.0)),
            )
            market_snapshot["return_4h"] = _return_over_window(
                current_price=float(market_snapshot["mark_price"]),
                history=market_history,
                snapshot_timestamp=snapshot_timestamp,
                window=timedelta(hours=4),
                fallback=float(market_snapshot.get("return_4h", 0.0)),
            )

            positioning_snapshot["oi_change_1h"] = _open_interest_change_over_window(
                current_open_interest=float(positioning_snapshot["open_interest"]),
                history=positioning_history,
                snapshot_timestamp=_as_utc_datetime(positioning_snapshot["timestamp"]),
                window=timedelta(hours=1),
                fallback=float(positioning_snapshot.get("oi_change_1h", 0.0)),
            )
            funding_history = [float(row.get("funding", 0.0)) for row in positioning_history if row.get("funding") is not None]
            positioning_snapshot["funding_zscore"] = zscore(
                float(positioning_snapshot["funding"]),
                funding_history,
            )
            positioning_snapshot["overheat_score"] = _derive_overheat_score(
                funding=float(positioning_snapshot["funding"]),
                funding_zscore=float(positioning_snapshot["funding_zscore"]),
                oi_volume_ratio=float(positioning_snapshot["oi_volume_ratio"]),
            )

            persisted_market = self.snapshot_repository.insert_market_snapshot(
                {
                    "token_id": token["id"],
                    "timestamp": _iso_timestamp(market_snapshot["timestamp"]),
                    "mark_price": market_snapshot["mark_price"],
                    "mid_price": market_snapshot["mid_price"],
                    "return_1h": market_snapshot["return_1h"],
                    "return_4h": market_snapshot["return_4h"],
                    "volume_1h": market_snapshot["volume_1h"],
                    "volume_24h": market_snapshot["volume_24h"],
                    "trade_imbalance_15m": market_snapshot["trade_imbalance_15m"],
                    "book_imbalance_top5": market_snapshot["book_imbalance_top5"],
                    "absorption_score": market_snapshot["absorption_score"],
                    "price_efficiency": market_snapshot["price_efficiency"],
                    "raw_hl_json": market_snapshot["raw"],
                }
            )
            persisted_positioning = self.snapshot_repository.insert_positioning_snapshot(
                {
                    "token_id": token["id"],
                    "timestamp": _iso_timestamp(positioning_snapshot["timestamp"]),
                    "funding": positioning_snapshot["funding"],
                    "funding_zscore": positioning_snapshot["funding_zscore"],
                    "open_interest": positioning_snapshot["open_interest"],
                    "oi_change_1h": positioning_snapshot["oi_change_1h"],
                    "oi_volume_ratio": positioning_snapshot["oi_volume_ratio"],
                    "overheat_score": positioning_snapshot["overheat_score"],
                    "raw_hl_json": positioning_snapshot["raw"],
                }
            )
            results.append(
                {
                    "token": token["symbol"],
                    "market": persisted_market,
                    "positioning": persisted_positioning,
                }
            )
        return results


def _iso_timestamp(value: datetime | str) -> str:
    if isinstance(value, str):
        return value
    return value.isoformat()


def _as_utc_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _reference_row_before_window(
    history: list[dict],
    *,
    snapshot_timestamp: datetime,
    window: timedelta,
) -> dict | None:
    cutoff = snapshot_timestamp - window
    eligible_rows = []
    for row in history:
        row_timestamp = row.get("timestamp")
        if not row_timestamp:
            continue
        parsed = _as_utc_datetime(row_timestamp)
        if parsed <= cutoff:
            eligible_rows.append((parsed, row))
    if not eligible_rows:
        return None
    eligible_rows.sort(key=lambda item: item[0], reverse=True)
    return eligible_rows[0][1]


def _return_over_window(
    *,
    current_price: float,
    history: list[dict],
    snapshot_timestamp: datetime,
    window: timedelta,
    fallback: float,
) -> float:
    reference = _reference_row_before_window(
        history,
        snapshot_timestamp=snapshot_timestamp,
        window=window,
    )
    if reference is None:
        return fallback
    reference_price = float(reference.get("mark_price", 0.0) or 0.0)
    if reference_price <= 0:
        return fallback
    return (current_price - reference_price) / reference_price


def _open_interest_change_over_window(
    *,
    current_open_interest: float,
    history: list[dict],
    snapshot_timestamp: datetime,
    window: timedelta,
    fallback: float,
) -> float:
    reference = _reference_row_before_window(
        history,
        snapshot_timestamp=snapshot_timestamp,
        window=window,
    )
    if reference is None:
        return fallback
    reference_oi = float(reference.get("open_interest", 0.0) or 0.0)
    if reference_oi <= 0:
        return fallback
    return (current_open_interest - reference_oi) / reference_oi


def _derive_overheat_score(*, funding: float, funding_zscore: float, oi_volume_ratio: float) -> float:
    funding_component = min(abs(funding) * 1000, 1.0)
    zscore_component = min(abs(funding_zscore) / 3, 1.0)
    oi_component = min(oi_volume_ratio / 5, 1.0)
    return max(0.0, min((0.25 * funding_component) + (0.35 * zscore_component) + (0.4 * oi_component), 1.0))
