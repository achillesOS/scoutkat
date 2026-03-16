from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
from uuid import uuid4

from app.core.config import get_settings
from app.models.enums import SignalStatus
from app.providers.base import GrokProvider
from app.repositories.score_repository import ScoreRepository, cooldown_cutoff_iso
from app.repositories.signal_repository import SignalRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.watchlist_repository import WatchlistRepository
from app.repositories.x_attention_repository import XAttentionRepository
from app.scoring.normalization import blend_normalized, zscore_to_unit
from app.scoring.engine import ScoringEngine, clamp
from app.services.cache_service import CacheService
from app.services.notification_service import NotificationService
from app.services.signal_detection_service import SignalDetectionService


class ScoringPipelineService:
    def __init__(
        self,
        token_repository: TokenRepository,
        watchlist_repository: WatchlistRepository,
        snapshot_repository: SnapshotRepository,
        x_attention_repository: XAttentionRepository,
        score_repository: ScoreRepository,
        signal_repository: SignalRepository,
        grok_provider: GrokProvider,
        cache_service: CacheService,
        notification_service: NotificationService,
    ) -> None:
        self.settings = get_settings()
        self.token_repository = token_repository
        self.watchlist_repository = watchlist_repository
        self.snapshot_repository = snapshot_repository
        self.x_attention_repository = x_attention_repository
        self.score_repository = score_repository
        self.signal_repository = signal_repository
        self.grok_provider = grok_provider
        self.cache_service = cache_service
        self.notification_service = notification_service
        self.scoring_engine = ScoringEngine()
        self.detection_service = SignalDetectionService()

    async def run_for_tracked_tokens(self, symbols: list[str]) -> list[dict]:
        tokens = self.token_repository.get_by_symbols(symbols)
        watchlist_ids = set(self.watchlist_repository.list_token_ids())
        results: list[dict] = []
        for token in tokens:
            market = self.snapshot_repository.latest_market_snapshot(token["id"])
            positioning = self.snapshot_repository.latest_positioning_snapshot(token["id"])
            if not market or not positioning:
                continue

            previous_score = self.score_repository.latest_score_snapshot(token["id"])
            attention = await self._ensure_attention_snapshot(
                token_id=token["id"],
                symbol=token["symbol"],
                market_snapshot=market,
                positioning_snapshot=positioning,
                is_watchlist=token["id"] in watchlist_ids,
                previous_score=previous_score,
            )
            scores = self._compute_scores(
                token_id=token["id"],
                attention_snapshot=attention,
                market_snapshot=market,
                positioning_snapshot=positioning,
                previous_score=previous_score,
            )

            score_row = self.score_repository.insert_score_snapshot(
                {
                    "token_id": token["id"],
                    "timestamp": _to_iso(market["timestamp"]),
                    "attention_score": scores["attention_score"],
                    "structure_score": scores["structure_score"],
                    "positioning_score": scores["positioning_score"],
                    "hidden_accumulation_score": scores["hidden_accumulation_score"],
                    "narrative_ignition_score": scores["narrative_ignition_score"],
                    "retail_trap_score": scores["retail_trap_score"],
                    "signal_type": str(scores["signal_type"]),
                    "signal_score": scores["signal_score"],
                    "confidence": scores["confidence"],
                }
            )

            detection = self.detection_service.detect(_score_bundle_from_dict(scores))
            signal_event = None
            if detection["is_candidate"] and not self._has_recent_signal(token["id"], detection["signal_type"]):
                explanation = self._build_explanation(token["symbol"], detection["signal_type"], attention, market, positioning)
                signal_event = self.signal_repository.create_signal_event(
                    {
                        "id": str(uuid4()),
                        "token_id": token["id"],
                        "triggered_at": _to_iso(datetime.now(timezone.utc)),
                        "signal_type": str(detection["signal_type"]),
                        "signal_score": scores["signal_score"],
                        "confidence": scores["confidence"],
                        "explanation_json": explanation,
                        "invalidation_json": {
                            "attention_rollover": "mention_acceleration < 0.1",
                            "structure_break": "trade_imbalance_15m flips below -0.1",
                            "positioning_overheat": "overheat_score > 0.75",
                        },
                        "status": str(SignalStatus.ACTIVE),
                    }
                )
                if signal_event is not None:
                    self.cache_service.setex(
                        self._signal_cooldown_key(token["id"], str(detection["signal_type"])),
                        self.settings.alert_cooldown_minutes * 60,
                        str(signal_event["triggered_at"]),
                    )
                    if detection["priority"] == "high":
                        await self.notification_service.notify_signal(
                            signal_event=signal_event,
                            token_symbol=token["symbol"],
                            explanation=explanation,
                        )

            results.append(
                {
                    "token": token["symbol"],
                    "score_snapshot": score_row,
                    "signal_event": signal_event,
                }
            )
        return results

    async def _ensure_attention_snapshot(
        self,
        *,
        token_id: str,
        symbol: str,
        market_snapshot: dict,
        positioning_snapshot: dict,
        is_watchlist: bool,
        previous_score: dict | None,
    ) -> dict:
        latest_attention = self.x_attention_repository.latest_snapshot(token_id)
        latest_timestamp = None
        if latest_attention and latest_attention.get("timestamp"):
            latest_timestamp = datetime.fromisoformat(str(latest_attention["timestamp"]).replace("Z", "+00:00"))

        should_refresh, shortlist_reasons = self._should_refresh_social(
            is_watchlist=is_watchlist,
            latest_attention=latest_attention,
            latest_timestamp=latest_timestamp,
            market_snapshot=market_snapshot,
            positioning_snapshot=positioning_snapshot,
            previous_score=previous_score,
        )
        freshness_key = self._social_freshness_key(symbol)
        if self.cache_service.get(freshness_key):
            should_refresh = False if latest_attention is not None and not is_watchlist else should_refresh
        if not should_refresh and latest_attention is not None:
            return latest_attention

        grok_payload = await self.grok_provider.fetch_social_summary(symbol, "6h")
        snapshot = {
            "token_id": token_id,
            "timestamp": _to_iso(grok_payload["timestamp"]),
            "mentions_1h": grok_payload.get("mentions_1h", 0),
            "mentions_6h": grok_payload.get("mentions_6h", grok_payload.get("mentions_1h", 0)),
            "unique_authors_1h": grok_payload.get("unique_authors_1h", 0),
            "mention_acceleration": grok_payload.get("mention_acceleration", 0.0),
            "retail_breadth": grok_payload.get("retail_breadth", 0.0),
            "expert_presence": grok_payload.get("expert_presence", 0.0),
            "narrative_novelty": grok_payload.get("narrative_novelty", 0.0),
            "raw_grok_json": {
                "provider_payload": grok_payload,
                "snapshot_incomplete": grok_payload.get("snapshot_incomplete", False),
                "validation_error": grok_payload.get("validation_error"),
                "shortlist_reasons": shortlist_reasons,
            },
        }
        self.cache_service.setex(
            freshness_key,
            self.settings.social_refresh_minutes * 60,
            str(snapshot["timestamp"]),
        )
        return self.x_attention_repository.insert_snapshot(snapshot) or snapshot

    def _should_refresh_social(
        self,
        *,
        is_watchlist: bool,
        latest_attention: dict | None,
        latest_timestamp: datetime | None,
        market_snapshot: dict,
        positioning_snapshot: dict,
        previous_score: dict | None,
    ) -> tuple[bool, list[str]]:
        reasons: list[str] = []
        if is_watchlist:
            reasons.append("watchlist_membership")
        if latest_attention is None or self._is_stale(latest_timestamp):
            reasons.append("stale_previous_snapshot")
        structure_shift = abs(float(market_snapshot.get("trade_imbalance_15m", 0.0))) >= 0.15 or abs(
            float(market_snapshot.get("book_imbalance_top5", 0.0))
        ) >= 0.15
        if structure_shift:
            reasons.append("unusual_structure_change")
        previous_signal_score = float(previous_score.get("signal_score", 0.0)) if previous_score else 0.0
        candidate_crossing = (
            previous_signal_score < self.detection_service.thresholds["candidate_signal_floor"]
            and (
                abs(float(market_snapshot.get("return_1h", 0.0))) * 100
                + abs(float(positioning_snapshot.get("oi_change_1h", 0.0))) * 100
            ) >= 4.5
        )
        if candidate_crossing:
            reasons.append("candidate_threshold_crossing")
        return (len(reasons) > 0), reasons

    def _compute_scores(
        self,
        *,
        token_id: str,
        attention_snapshot: dict,
        market_snapshot: dict,
        positioning_snapshot: dict,
        previous_score: dict | None,
    ) -> dict:
        attention_history = self.x_attention_repository.recent_snapshots(token_id, limit=48)
        market_history = self.snapshot_repository.recent_market_snapshots(token_id, limit=48)
        positioning_history = self.snapshot_repository.recent_positioning_snapshots(token_id, limit=48)

        attention_features = {
            "mentions_1h": blend_normalized(
                float(attention_snapshot.get("mentions_1h", 0.0)),
                [row.get("mentions_1h", 0.0) for row in attention_history],
            ),
            "unique_authors_1h": blend_normalized(
                float(attention_snapshot.get("unique_authors_1h", 0.0)),
                [row.get("unique_authors_1h", 0.0) for row in attention_history],
            ),
            "mention_acceleration": blend_normalized(
                float(attention_snapshot.get("mention_acceleration", 0.0)),
                [row.get("mention_acceleration", 0.0) for row in attention_history],
            ),
            "retail_breadth": blend_normalized(
                float(attention_snapshot.get("retail_breadth", 0.0)),
                [row.get("retail_breadth", 0.0) for row in attention_history],
            ),
            "narrative_novelty": blend_normalized(
                float(attention_snapshot.get("narrative_novelty", 0.0)),
                [row.get("narrative_novelty", 0.0) for row in attention_history],
            ),
        }
        volume_anomaly_raw = (float(market_snapshot.get("volume_1h", 0.0)) / max(float(market_snapshot.get("volume_24h", 1.0)), 1.0)) * 24
        market_features = {
            "return_1h": blend_normalized(
                float(market_snapshot.get("return_1h", 0.0)),
                [row.get("return_1h", 0.0) for row in market_history],
            ),
            "return_4h": blend_normalized(
                float(market_snapshot.get("return_4h", 0.0)),
                [row.get("return_4h", 0.0) for row in market_history],
            ),
            "volume_anomaly": blend_normalized(
                volume_anomaly_raw,
                [
                    (float(row.get("volume_1h", 0.0)) / max(float(row.get("volume_24h", 1.0)), 1.0)) * 24
                    for row in market_history
                ],
            ),
            "trade_imbalance_15m": blend_normalized(
                float(market_snapshot.get("trade_imbalance_15m", 0.0)),
                [row.get("trade_imbalance_15m", 0.0) for row in market_history],
            ),
            "book_imbalance_top5": blend_normalized(
                float(market_snapshot.get("book_imbalance_top5", 0.0)),
                [row.get("book_imbalance_top5", 0.0) for row in market_history],
            ),
            "absorption_score": blend_normalized(
                float(market_snapshot.get("absorption_score", 0.0)),
                [row.get("absorption_score", 0.0) for row in market_history],
            ),
            "price_efficiency": blend_normalized(
                float(market_snapshot.get("price_efficiency", 0.0)),
                [row.get("price_efficiency", 0.0) for row in market_history],
            ),
        }
        positioning_features = {
            "funding": blend_normalized(
                float(positioning_snapshot.get("funding", 0.0)),
                [row.get("funding", 0.0) for row in positioning_history],
            ),
            "funding_zscore": zscore_to_unit(
                float(positioning_snapshot.get("funding", 0.0)),
                [row.get("funding", 0.0) for row in positioning_history],
                scale=2.0,
            ),
            "oi_change_1h": blend_normalized(
                float(positioning_snapshot.get("oi_change_1h", 0.0)),
                [row.get("oi_change_1h", 0.0) for row in positioning_history],
            ),
            "oi_volume_ratio": blend_normalized(
                float(positioning_snapshot.get("oi_volume_ratio", 0.0)),
                [row.get("oi_volume_ratio", 0.0) for row in positioning_history],
            ),
            "overheat_score": blend_normalized(
                float(positioning_snapshot.get("overheat_score", 0.0)),
                [row.get("overheat_score", 0.0) for row in positioning_history],
            ),
        }

        attention_score, structure_score, positioning_score = self.scoring_engine.compute_component_scores(
            attention=attention_features,
            market=market_features,
            positioning=positioning_features,
        )
        previous_attention = _percent_to_unit(previous_score.get("attention_score")) if previous_score else 0.0
        previous_structure = _percent_to_unit(previous_score.get("structure_score")) if previous_score else 0.0

        bundle = self.scoring_engine.compute_signal_scores(
            attention_score=attention_score,
            structure_score=structure_score,
            positioning_score=positioning_score,
            delta_attention=attention_score - previous_attention,
            delta_structure=structure_score - previous_structure,
            completeness=1.0 if attention_snapshot else 0.66,
        )
        return asdict(bundle)

    def _has_recent_signal(self, token_id: str, signal_type: str) -> bool:
        cooldown_key = self._signal_cooldown_key(token_id, str(signal_type))
        if self.cache_service.get(cooldown_key):
            return True
        recent_signals = self.signal_repository.list_signals_for_token(token_id)
        cutoff = cooldown_cutoff_iso(self.settings.alert_cooldown_minutes)
        cutoff_dt = _parse_datetime(cutoff)
        for signal in recent_signals:
            triggered_at = _parse_datetime(signal["triggered_at"])
            if signal["signal_type"] == str(signal_type) and triggered_at >= cutoff_dt:
                self.cache_service.setex(
                    cooldown_key,
                    self.settings.alert_cooldown_minutes * 60,
                    str(signal["triggered_at"]),
                )
                return True
        return False

    def _is_stale(self, latest_timestamp: datetime | None) -> bool:
        if latest_timestamp is None:
            return True
        latest_utc = latest_timestamp.astimezone(timezone.utc) if latest_timestamp.tzinfo else latest_timestamp.replace(tzinfo=timezone.utc)
        age_seconds = (datetime.now(timezone.utc) - latest_utc).total_seconds()
        return age_seconds >= self.settings.social_refresh_minutes * 60

    def _build_explanation(
        self,
        symbol: str,
        signal_type: str,
        attention_snapshot: dict,
        market_snapshot: dict,
        positioning_snapshot: dict,
    ) -> dict:
        why_now_map = {
            "hidden_accumulation": f"{symbol} is showing stronger order-flow structure than public attention, while perp crowding is still contained.",
            "narrative_ignition": f"{symbol} is seeing attention and market structure accelerate together before positioning looks fully saturated.",
            "retail_trap": f"{symbol} has hot attention and rising perp crowding, but structure is lagging enough to raise trap risk.",
        }
        return {
            "why_now": why_now_map.get(signal_type, f"{symbol} is entering a meaningful divergence zone."),
            "risks": [
                "Fast regime changes can invalidate the setup.",
                "Perp crowding can flip quickly after momentum spikes.",
            ],
            "suggested_action": "Treat this as a watch-and-confirm signal rather than an auto-trade trigger.",
            "invalidation_conditions": [
                "trade_imbalance_15m loses direction",
                "attention acceleration falls below recent baseline",
            ],
            "evidence": [
                f"mentions_1h={attention_snapshot.get('mentions_1h', 0)}",
                f"trade_imbalance_15m={round(float(market_snapshot.get('trade_imbalance_15m', 0.0)), 3)}",
                f"overheat_score={round(float(positioning_snapshot.get('overheat_score', 0.0)), 3)}",
            ],
        }

    def _social_freshness_key(self, symbol: str) -> str:
        return f"scoutkat:social:fresh:{symbol.upper()}"

    def _signal_cooldown_key(self, token_id: str, signal_type: str) -> str:
        return f"scoutkat:signal:cooldown:{token_id}:{signal_type}"


def _to_iso(value: datetime | str) -> str:
    if isinstance(value, str):
        return value
    return value.isoformat()


def _percent_to_unit(value: float | int | None) -> float:
    if value is None:
        return 0.0
    return clamp((float(value) / 100) * 2 - 1, -1.0, 1.0)


def _parse_datetime(value: datetime | str) -> datetime:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc) if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(timezone.utc)


def _score_bundle_from_dict(payload: dict):
    from app.scoring.engine import ScoreBundle

    return ScoreBundle(**payload)
