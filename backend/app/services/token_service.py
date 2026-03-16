from datetime import datetime, timedelta, timezone
from typing import Any

from app.models.enums import SignalType
from app.repositories.score_repository import ScoreRepository
from app.repositories.signal_repository import SignalRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.token_repository import TokenRepository
from app.repositories.watchlist_repository import WatchlistRepository
from app.repositories.x_attention_repository import XAttentionRepository


class TokenService:
    def __init__(
        self,
        token_repository: TokenRepository,
        signal_repository: SignalRepository,
        snapshot_repository: SnapshotRepository,
        x_attention_repository: XAttentionRepository,
        score_repository: ScoreRepository,
        watchlist_repository: WatchlistRepository,
    ) -> None:
        self.token_repository = token_repository
        self.signal_repository = signal_repository
        self.snapshot_repository = snapshot_repository
        self.x_attention_repository = x_attention_repository
        self.score_repository = score_repository
        self.watchlist_repository = watchlist_repository

    def list_tokens(self) -> list[dict]:
        return self.token_repository.list_tokens()

    def get_token_detail(self, symbol: str) -> dict | None:
        token = self.token_repository.get_by_symbol(symbol)
        if not token:
            return None
        token["recent_signals"] = self.signal_repository.list_signals_for_token(token["id"])
        return token

    def get_token_context(self, symbol: str) -> dict | None:
        token = self.token_repository.get_by_symbol(symbol)
        if token is None:
            return None

        market = self.snapshot_repository.latest_market_snapshot(token["id"])
        positioning = self.snapshot_repository.latest_positioning_snapshot(token["id"])
        score = self.score_repository.latest_score_snapshot(token["id"])
        attention = self.x_attention_repository.latest_snapshot(token["id"])
        if market is None or positioning is None or score is None:
            return None

        recent_signals = self.signal_repository.list_signals_for_token(token["id"])
        latest_signal = recent_signals[0] if recent_signals else None

        return {
            "header": {
                "id": token["id"],
                "symbol": token["symbol"],
                "name": token["name"],
                "market_type": token["market_type"],
                "current_price": float(market.get("mark_price", 0.0)),
                "change_1h": float(market.get("return_1h", 0.0)) * 100,
                "change_4h": float(market.get("return_4h", 0.0)) * 100,
                "change_24h": self._market_change_24h(market),
                "last_updated": market["timestamp"],
            },
            "current_signal_state": {
                "signal_type": score["signal_type"],
                "signal_score": float(score["signal_score"]),
                "confidence": float(score["confidence"]),
                "why_now": self._build_why_now(latest_signal, score, market, positioning),
                "risks": self._build_risks(latest_signal, positioning),
                "invalidation": self._build_invalidation(latest_signal, score, market),
            },
            "social_summary": self._build_social_summary(attention),
            "divergence_chart": {
                "default_timeframe": "72h",
                "series": {
                    "24h": self._build_divergence_series(token["id"], hours=24),
                    "72h": self._build_divergence_series(token["id"], hours=72),
                    "7d": self._build_divergence_series(token["id"], hours=168),
                },
            },
            "recent_state_changes": self._build_recent_state_changes(token["id"]),
            "recent_signal_history": recent_signals,
        }

    def get_watchtower(self, symbols: list[str] | None = None, user_email: str | None = None) -> dict:
        if user_email:
            token_ids = self.watchlist_repository.list_token_ids(user_email)
            tokens = self.token_repository.get_by_ids(token_ids)
        elif symbols:
            tokens = self.token_repository.get_by_symbols(symbols)
        else:
            tokens = self._top_watchtower_tokens()

        assets = [asset for token in tokens if (asset := self._build_watchtower_asset(token)) is not None]
        assets.sort(key=lambda asset: (asset["signal_score"], asset["last_updated"]), reverse=True)

        if not assets:
            return {
                "last_refresh": datetime.now(timezone.utc).isoformat(),
                "tracked_assets_count": 0,
                "active_signals_count": 0,
                "recently_changed_count": 0,
                "hero_cards": [],
                "assets": [],
            }

        top_signal = next((asset for asset in assets if asset["signal_type"] != SignalType.RETAIL_TRAP), assets[0])
        top_trap = next((asset for asset in assets if asset["signal_type"] == SignalType.RETAIL_TRAP), assets[0])
        recent_change = sorted(assets, key=lambda asset: asset["last_updated"], reverse=True)[0]

        return {
            "last_refresh": max(asset["last_updated"] for asset in assets),
            "tracked_assets_count": len(assets),
            "active_signals_count": len([asset for asset in assets if asset["signal_type"] != SignalType.NEUTRAL]),
            "recently_changed_count": len(self._recently_changed_assets(assets)),
            "hero_cards": [
                self._hero_card("Top Signal Now", top_signal),
                self._hero_card("Top Trap Now", top_trap),
                self._hero_card("Recently Changed", recent_change),
            ],
            "assets": assets,
        }

    def _top_watchtower_tokens(self) -> list[dict]:
        recent_scores = self.score_repository.list_recent_scores(limit=300)
        latest_by_token: dict[str, dict] = {}
        for row in recent_scores:
            token_id = row["token_id"]
            if token_id not in latest_by_token:
                latest_by_token[token_id] = row

        ranked_token_ids = [
            row["token_id"]
            for row in sorted(
                latest_by_token.values(),
                key=lambda item: float(item.get("signal_score", 0.0)),
                reverse=True,
            )[:6]
        ]
        return self.token_repository.get_by_ids(ranked_token_ids)

    def _build_watchtower_asset(self, token: dict) -> dict | None:
        market = self.snapshot_repository.latest_market_snapshot(token["id"])
        score = self.score_repository.latest_score_snapshot(token["id"])
        if market is None or score is None:
            return None

        latest_signal = self.signal_repository.list_signals_for_token(token["id"])
        signal = latest_signal[0] if latest_signal else None

        return {
            "id": token["id"],
            "symbol": token["symbol"],
            "name": token["name"],
            "market_type": token["market_type"],
            "current_price": float(market.get("mark_price", 0.0)),
            "change_1h": float(market.get("return_1h", 0.0)) * 100,
            "change_24h": self._market_change_24h(market),
            "signal_type": score["signal_type"],
            "signal_score": float(score.get("signal_score", 0.0)),
            "confidence": float(score.get("confidence", 0.0)),
            "last_updated": market["timestamp"],
            "why_now": self._build_why_now(signal, score, market, None),
        }

    def _hero_card(self, title: str, asset: dict) -> dict:
        return {
            "title": title,
            "token_symbol": asset["symbol"],
            "signal_type": asset["signal_type"],
            "signal_score": asset["signal_score"],
            "confidence": asset["confidence"],
            "current_price": asset["current_price"],
            "change_24h": asset["change_24h"],
            "why_now": asset["why_now"],
        }

    def _recently_changed_assets(self, assets: list[dict]) -> list[dict]:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=4)
        return [
            asset
            for asset in assets
            if datetime.fromisoformat(str(asset["last_updated"]).replace("Z", "+00:00")) >= cutoff
        ]

    def _build_divergence_series(self, token_id: str, hours: int) -> list[dict]:
        since_iso = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        rows = self.score_repository.recent_score_snapshots(token_id, limit=240)
        filtered = [
            row
            for row in rows
            if datetime.fromisoformat(str(row["timestamp"]).replace("Z", "+00:00"))
            >= datetime.fromisoformat(since_iso.replace("Z", "+00:00"))
        ]
        filtered.sort(key=lambda row: row["timestamp"])
        return [
            {
                "timestamp": row["timestamp"],
                "attention_score": float(row["attention_score"]),
                "structure_score": float(row["structure_score"]),
                "positioning_score": float(row["positioning_score"]),
            }
            for row in filtered
        ]

    def _build_recent_state_changes(self, token_id: str) -> list[dict]:
        score_rows = self.score_repository.recent_score_snapshots(token_id, limit=12)
        signal_rows = self.signal_repository.list_signals_for_token(token_id)[:5]
        score_rows.sort(key=lambda row: row["timestamp"], reverse=True)

        changes: list[dict] = []
        previous_signal_type: str | None = None
        previous_signal_score: float | None = None
        for row in score_rows:
            signal_type = str(row["signal_type"])
            signal_score = float(row["signal_score"])
            if previous_signal_type is None or signal_type != previous_signal_type or abs(signal_score - (previous_signal_score or 0.0)) >= 8:
                changes.append(
                    {
                        "timestamp": row["timestamp"],
                        "title": f"State moved to {signal_type.replace('_', ' ')}",
                        "detail": f"Signal score printed {signal_score:.0f} with confidence {float(row['confidence']) * 100:.0f}%.",
                        "signal_type": signal_type,
                    }
                )
            previous_signal_type = signal_type
            previous_signal_score = signal_score

        for signal in signal_rows:
            changes.append(
                {
                    "timestamp": signal["triggered_at"],
                    "title": "Signal event triggered",
                    "detail": signal["explanation"]["why_now"],
                    "signal_type": signal["signal_type"],
                }
            )

        changes.sort(key=lambda row: row["timestamp"], reverse=True)
        return changes[:6]

    def _build_why_now(
        self,
        latest_signal: dict | None,
        score: dict,
        market: dict,
        positioning: dict | None,
    ) -> str:
        if latest_signal and latest_signal.get("explanation", {}).get("why_now"):
            return latest_signal["explanation"]["why_now"]
        structure = float(score.get("structure_score", 0.0))
        attention = float(score.get("attention_score", 0.0))
        positioning_score = float(score.get("positioning_score", 0.0))
        price_change = float(market.get("return_1h", 0.0)) * 100
        if attention > structure + 8:
            return f"X attention is outrunning structure by {attention - structure:.0f} points while price is moving {price_change:.1f}% over 1h."
        if structure > attention + 8:
            return f"Structure is leading attention by {structure - attention:.0f} points while positioning remains at {positioning_score:.0f}."
        if positioning is not None:
            return f"Attention, structure, and positioning are clustered, with open interest now at {float(positioning.get('open_interest', 0.0)):.0f}."
        return "Attention, structure, and positioning are close together, so Scoutkat is watching for a cleaner divergence."

    def _build_risks(self, latest_signal: dict | None, positioning: dict) -> list[str]:
        if latest_signal and latest_signal.get("explanation", {}).get("risks"):
            return latest_signal["explanation"]["risks"]
        funding = float(positioning.get("funding", 0.0))
        oi_ratio = float(positioning.get("oi_volume_ratio", 0.0))
        return [
            f"Funding is printing {funding:.4f}, so crowding can build quickly if the move extends.",
            f"Open interest to volume ratio is {oi_ratio:.2f}, which can worsen trap risk if flow turns.",
        ]

    def _build_invalidation(self, latest_signal: dict | None, score: dict, market: dict) -> list[str]:
        if latest_signal and latest_signal.get("explanation", {}).get("invalidation_conditions"):
            return latest_signal["explanation"]["invalidation_conditions"]
        return [
            f"Structure score loses support below {max(float(score.get('structure_score', 0.0)) - 8, 0):.0f}.",
            f"1h return reverses from {float(market.get('return_1h', 0.0)) * 100:.1f}% into negative territory.",
        ]

    def _build_social_summary(self, attention: dict[str, Any] | None) -> dict[str, Any]:
        if attention is None:
            return {
                "snapshot_incomplete": True,
                "attention_label": "Unavailable",
                "discussion_type": "unclear",
                "signal_hint": "unclear",
                "confidence": 0.0,
                "summary_points": ["No recent X summary is available for this asset yet."],
                "top_narratives": [],
                "expert_presence": 0.0,
                "retail_breadth": 0.0,
                "narrative_novelty": 0.0,
            }

        raw = attention.get("raw_grok_json") or {}
        provider_payload = raw.get("provider_payload", {}) if isinstance(raw, dict) else {}
        validated_payload = provider_payload.get("validated_payload") if isinstance(provider_payload, dict) else None
        summary_points: list[str] = []
        top_narratives: list[str] = []
        discussion_type = "unclear"
        signal_hint = "unclear"
        attention_label = _attention_level_label(float(attention.get("mentions_1h", 0.0)))
        confidence = 0.0

        if isinstance(validated_payload, dict):
            summary_points = [str(item) for item in validated_payload.get("new_information_summary", []) if str(item).strip()]
            top_narratives = [str(item) for item in validated_payload.get("top_narratives", []) if str(item).strip()]
            discussion_type = str(validated_payload.get("discussion_type", "unclear"))
            signal_hint = str(validated_payload.get("signal_hint", {}).get("likely_pattern", "unclear"))
            attention_label = str(validated_payload.get("attention_level", attention_label)).replace("_", " ").title()
            confidence = float(validated_payload.get("confidence", 0.0))

        if not summary_points:
            summary_points = [
                f"Estimated {int(float(attention.get('mentions_1h', 0.0)))} mentions over the last hour.",
                f"Retail breadth {float(attention.get('retail_breadth', 0.0)):.2f} and expert presence {float(attention.get('expert_presence', 0.0)):.2f}.",
            ]

        return {
            "snapshot_incomplete": bool(provider_payload.get("snapshot_incomplete", False)),
            "attention_label": attention_label,
            "discussion_type": discussion_type,
            "signal_hint": signal_hint,
            "confidence": confidence,
            "summary_points": summary_points[:4],
            "top_narratives": top_narratives[:4],
            "expert_presence": float(attention.get("expert_presence", 0.0)),
            "retail_breadth": float(attention.get("retail_breadth", 0.0)),
            "narrative_novelty": float(attention.get("narrative_novelty", 0.0)),
        }

    def _market_change_24h(self, market: dict[str, Any]) -> float:
        raw = market.get("raw_hl_json") or {}
        asset_ctx = raw.get("asset_ctx", {}) if isinstance(raw, dict) else {}
        prev_day_price = float(asset_ctx.get("prevDayPx", 0.0) or 0.0)
        mark_price = float(market.get("mark_price", 0.0) or 0.0)
        if prev_day_price <= 0:
            return 0.0
        return ((mark_price - prev_day_price) / prev_day_price) * 100


def _attention_level_label(mentions_1h: float) -> str:
    if mentions_1h >= 250:
        return "Extreme"
    if mentions_1h >= 120:
        return "High"
    if mentions_1h >= 40:
        return "Medium"
    return "Low"
