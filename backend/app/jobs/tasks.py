import asyncio

from app.core.config import get_settings
from app.core.container import (
    get_hourly_digest_service,
    get_market_ingestion_service,
    get_scoring_pipeline_service,
)


def fetch_market_snapshots_job() -> None:
    settings = get_settings()
    results = asyncio.run(
        get_market_ingestion_service().ingest_tracked_tokens(settings.tracked_symbol_list)
    )
    print(f"fetch_market_snapshots_job: ingested {len(results)} tokens")


def fetch_positioning_snapshots_job() -> None:
    print("fetch_positioning_snapshots_job: handled inside fetch_market_snapshots_job for MVP")


def fetch_grok_shortlist_job() -> None:
    print("fetch_grok_shortlist_job: shortlisted-token refresh")


def compute_scores_job() -> None:
    settings = get_settings()
    results = asyncio.run(
        get_scoring_pipeline_service().run_for_tracked_tokens(settings.tracked_symbol_list)
    )
    print(f"compute_scores_job: wrote {len(results)} score snapshots")


def detect_signals_job() -> None:
    print("detect_signals_job: handled inside compute_scores_job for MVP")


def send_hourly_digest_job() -> None:
    settings = get_settings()
    try:
        result = asyncio.run(get_hourly_digest_service().run(settings.hourly_digest_symbol_list))
        print(
            "send_hourly_digest_job: sent digest for "
            f"{','.join(result['symbols'])} with status {result.get('provider_result', {}).get('status', 'unknown')}"
        )
    except Exception as exc:
        print(f"send_hourly_digest_job: failed with {type(exc).__name__}: {exc}")
