from datetime import datetime, timedelta, timezone

from app.providers.base import GrokProvider, HyperliquidProvider
from app.scoring.config import load_thresholds
from app.scoring.engine import ScoringEngine
from app.services.signal_detection_service import SignalDetectionService


class SignalPipelineService:
    def __init__(
        self,
        hyperliquid_provider: HyperliquidProvider,
        grok_provider: GrokProvider,
    ) -> None:
        self.hyperliquid_provider = hyperliquid_provider
        self.grok_provider = grok_provider
        self.scoring_engine = ScoringEngine()
        self.detection_service = SignalDetectionService()
        self.thresholds = load_thresholds()

    def should_refresh_social(
        self,
        *,
        is_watchlist: bool,
        last_social_timestamp: datetime | None,
        market_snapshot: dict,
        candidate_bias: float,
    ) -> bool:
        stale_cutoff = datetime.now(timezone.utc) - timedelta(
            minutes=self.thresholds["social_stale_minutes"]
        )
        stale = last_social_timestamp is None or last_social_timestamp < stale_cutoff
        unusual_structure = abs(market_snapshot.get("trade_imbalance_15m", 0.0)) >= 0.15
        entering_candidate_zone = candidate_bias >= 0.5
        return is_watchlist or stale or unusual_structure or entering_candidate_zone

    async def evaluate_token(
        self,
        symbol: str,
        *,
        is_watchlist: bool,
        last_social_timestamp: datetime | None = None,
    ) -> dict:
        market = await self.hyperliquid_provider.fetch_market_snapshot(symbol)
        positioning = await self.hyperliquid_provider.fetch_positioning_snapshot(symbol)
        candidate_bias = abs(market.get("return_1h", 0.0)) + abs(positioning.get("oi_change_1h", 0.0))

        if self.should_refresh_social(
            is_watchlist=is_watchlist,
            last_social_timestamp=last_social_timestamp,
            market_snapshot=market,
            candidate_bias=candidate_bias,
        ):
            attention = await self.grok_provider.fetch_social_summary(symbol, "6h")
        else:
            attention = {
                "mentions_1h": 0.0,
                "unique_authors_1h": 0.0,
                "mention_acceleration": 0.0,
                "retail_breadth": 0.0,
                "narrative_novelty": 0.0,
            }

        market_for_scoring = {
            **market,
            "volume_anomaly": min(market.get("volume_1h", 0.0) / max(market.get("volume_24h", 1.0), 1.0) * 24, 1.0),
        }
        attention_score, structure_score, positioning_score = self.scoring_engine.compute_component_scores(
            attention=attention,
            market=market_for_scoring,
            positioning=positioning,
        )
        scores = self.scoring_engine.compute_signal_scores(
            attention_score=attention_score,
            structure_score=structure_score,
            positioning_score=positioning_score,
            delta_attention=attention.get("mention_acceleration", 0.0),
            delta_structure=market.get("trade_imbalance_15m", 0.0),
            completeness=1.0 if attention else 0.66,
        )
        detection = self.detection_service.detect(scores)

        return {
            "symbol": symbol,
            "market_snapshot": market,
            "positioning_snapshot": positioning,
            "attention_snapshot": attention,
            "scores": scores.__dict__,
            "detection": detection,
        }
