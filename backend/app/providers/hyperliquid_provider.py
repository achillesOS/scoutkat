import asyncio
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import get_settings
from app.providers.base import HyperliquidProvider


class HyperliquidHttpProvider(HyperliquidProvider):
    def __init__(self) -> None:
        self.settings = get_settings()

    async def _fetch_asset_context(self, symbol: str) -> tuple[dict[str, Any], dict[str, Any]]:
        payload = await self._post_info({"type": "metaAndAssetCtxs"})

        meta, asset_contexts = payload
        for asset_meta, asset_ctx in zip(meta.get("universe", []), asset_contexts, strict=False):
            if asset_meta.get("name") == symbol.upper():
                return asset_meta, asset_ctx
        raise ValueError(f"Hyperliquid asset context not found for {symbol}")

    async def _post_info(self, payload: dict[str, Any]) -> Any:
        last_error: Exception | None = None
        delay = 1.0
        for attempt in range(3):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(
                        self.settings.hyperliquid_api_url + "/info",
                        json=payload,
                    )
                    response.raise_for_status()
                    return response.json()
            except Exception as exc:
                last_error = exc
                if attempt == 2:
                    break
                await asyncio.sleep(delay)
                delay *= 2
        assert last_error is not None
        raise last_error

    async def fetch_market_snapshot(self, symbol: str) -> dict[str, Any]:
        asset_meta, asset_ctx = await self._fetch_asset_context(symbol)
        mark_price = float(asset_ctx.get("markPx", asset_ctx.get("oraclePx", 0.0)) or 0.0)
        mid_price = float(asset_ctx.get("midPx", mark_price) or mark_price)
        prev_day_price = float(asset_ctx.get("prevDayPx", mark_price) or mark_price or 1.0)
        volume_24h = float(asset_ctx.get("dayNtlVlm", 0.0) or 0.0)
        return_24h = 0.0 if prev_day_price == 0 else (mark_price - prev_day_price) / prev_day_price
        premium = 0.0 if mid_price == 0 else (mark_price - mid_price) / mid_price
        absorption_score = max(0.0, min(1.0, 1 - abs(premium) * 100))
        price_efficiency = max(0.0, min(1.0, abs(return_24h) / max(abs(premium) * 20, 0.01)))

        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.now(timezone.utc),
            "mark_price": mark_price,
            "mid_price": mid_price,
            "return_1h": return_24h / 24,
            "return_4h": return_24h / 6,
            "volume_1h": volume_24h / 24,
            "volume_24h": volume_24h,
            "trade_imbalance_15m": max(-1.0, min(1.0, return_24h * 8)),
            "book_imbalance_top5": max(-1.0, min(1.0, premium * 100)),
            "absorption_score": absorption_score,
            "price_efficiency": price_efficiency,
            "raw": {"meta": asset_meta, "asset_ctx": asset_ctx},
        }

    async def fetch_positioning_snapshot(self, symbol: str) -> dict[str, Any]:
        _, asset_ctx = await self._fetch_asset_context(symbol)
        funding = float(asset_ctx.get("funding", 0.0) or 0.0)
        open_interest = float(asset_ctx.get("openInterest", 0.0) or 0.0)
        volume_24h = float(asset_ctx.get("dayNtlVlm", 0.0) or 0.0)
        oi_volume_ratio = 0.0 if volume_24h == 0 else min(open_interest / volume_24h, 5.0)
        overheat_score = max(0.0, min(1.0, abs(funding) * 1000 + (oi_volume_ratio / 5)))

        return {
            "symbol": symbol.upper(),
            "timestamp": datetime.now(timezone.utc),
            "funding": funding,
            "funding_zscore": 0.0,
            "open_interest": open_interest,
            "oi_change_1h": 0.0,
            "oi_volume_ratio": oi_volume_ratio,
            "overheat_score": overheat_score,
            "raw": {"asset_ctx": asset_ctx},
        }


class UnavailableHyperliquidProvider(HyperliquidProvider):
    async def fetch_market_snapshot(self, symbol: str) -> dict[str, Any]:
        raise RuntimeError(
            f"Hyperliquid provider is unavailable for {symbol}. "
            "Configure HYPERLIQUID_API_URL to enable live market snapshots."
        )

    async def fetch_positioning_snapshot(self, symbol: str) -> dict[str, Any]:
        raise RuntimeError(
            f"Hyperliquid provider is unavailable for {symbol}. "
            "Configure HYPERLIQUID_API_URL to enable live positioning snapshots."
        )
