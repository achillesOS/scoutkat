from __future__ import annotations

from app.repositories.score_repository import ScoreRepository
from app.repositories.snapshot_repository import SnapshotRepository
from app.repositories.token_repository import TokenRepository
from app.services.market_ingestion_service import MarketIngestionService
from app.services.notification_service import NotificationService
from app.services.scoring_pipeline_service import ScoringPipelineService


class HourlyDigestService:
    def __init__(
        self,
        token_repository: TokenRepository,
        snapshot_repository: SnapshotRepository,
        score_repository: ScoreRepository,
        market_ingestion_service: MarketIngestionService,
        scoring_pipeline_service: ScoringPipelineService,
        notification_service: NotificationService,
    ) -> None:
        self.token_repository = token_repository
        self.snapshot_repository = snapshot_repository
        self.score_repository = score_repository
        self.market_ingestion_service = market_ingestion_service
        self.scoring_pipeline_service = scoring_pipeline_service
        self.notification_service = notification_service

    async def run(self, symbols: list[str]) -> dict:
        normalized_symbols = [symbol.upper() for symbol in symbols]
        digest_rows: list[dict] = []
        for symbol in normalized_symbols:
            digest_rows.append(await self._build_symbol_digest_row(symbol))

        provider_result = await self.notification_service.send_hourly_digest(digest_rows)
        return {
            "symbols": normalized_symbols,
            "rows": digest_rows,
            "provider_result": provider_result,
        }

    async def _build_symbol_digest_row(self, symbol: str) -> dict:
        try:
            token = self.token_repository.get_by_symbol(symbol)
        except Exception as exc:
            return {"symbol": symbol, "status": "unavailable", "reason": _format_error(exc)}
        if token is None:
            return {"symbol": symbol, "status": "missing_token", "reason": "token_not_seeded"}

        refresh_error: str | None = None
        try:
            await self.market_ingestion_service.ingest_tracked_tokens([symbol])
        except Exception as exc:
            refresh_error = _format_error(exc)

        try:
            latest_market = self.snapshot_repository.latest_market_snapshot(token["id"])
            latest_score_before_run = self.score_repository.latest_score_snapshot(token["id"])
        except Exception as exc:
            return {"symbol": symbol, "status": "unavailable", "reason": _format_error(exc)}

        if latest_market is None:
            return {
                "symbol": symbol,
                "status": "unavailable",
                "reason": refresh_error or "missing_market_snapshot",
            }

        scoring_error: str | None = None
        try:
            scoring_results = await self.scoring_pipeline_service.run_for_tracked_tokens([symbol])
            result = scoring_results[0] if scoring_results else None
            score_snapshot = result.get("score_snapshot") if result else None
            signal_event = result.get("signal_event") if result else None
        except Exception as exc:
            scoring_error = _format_error(exc)
            score_snapshot = latest_score_before_run
            signal_event = None

        if score_snapshot is None:
            return {
                "symbol": symbol,
                "status": "missing_score",
                "reason": scoring_error or refresh_error or "score_not_available",
            }

        explanation = (signal_event or {}).get("explanation") or _fallback_explanation(
            symbol,
            str(score_snapshot["signal_type"]),
        )
        return {
            "symbol": symbol,
            "status": "ok",
            "signal_type": str(score_snapshot["signal_type"]),
            "signal_score": float(score_snapshot["signal_score"]),
            "confidence": float(score_snapshot["confidence"]),
            "price": float(latest_market["mark_price"]),
            "market_timestamp": str(latest_market["timestamp"]),
            "why_now": explanation.get("why_now", ""),
            "mode": "fallback" if refresh_error or scoring_error else "live",
            "warning": refresh_error or scoring_error,
            "verified": refresh_error is None and scoring_error is None,
        }


def _fallback_explanation(symbol: str, signal_type: str) -> dict:
    why_now_map = {
        "hidden_accumulation": f"{symbol} structure is stronger than public attention while crowding stays contained.",
        "narrative_ignition": f"{symbol} attention and structure are accelerating together before positioning looks crowded.",
        "retail_trap": f"{symbol} attention is hot and crowding is rising, but structure is lagging enough to flag trap risk.",
        "neutral": f"{symbol} does not have a strong divergence edge right now.",
    }
    return {"why_now": why_now_map.get(signal_type, f"{symbol} is in a transition zone and needs another read.")}


def _format_error(exc: Exception) -> str:
    name = type(exc).__name__
    detail = str(exc).strip()
    return f"{name}: {detail}" if detail else name
