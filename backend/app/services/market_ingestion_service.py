from datetime import datetime

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
            latest_positioning = self.snapshot_repository.latest_positioning_snapshot(token["id"])
            positioning_snapshot = await self.hyperliquid_provider.fetch_positioning_snapshot(token["symbol"])

            previous_open_interest = float(latest_positioning["open_interest"]) if latest_positioning else 0.0
            current_open_interest = float(positioning_snapshot["open_interest"])
            if previous_open_interest > 0:
                positioning_snapshot["oi_change_1h"] = (
                    current_open_interest - previous_open_interest
                ) / previous_open_interest

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
