from datetime import datetime, timedelta, timezone

from app.models.enums import SignalStatus, SignalType


TOKENS = [
    {"id": "btc", "symbol": "BTC", "name": "Bitcoin", "market_type": "perp", "is_active": True},
    {"id": "eth", "symbol": "ETH", "name": "Ethereum", "market_type": "perp", "is_active": True},
    {"id": "sol", "symbol": "SOL", "name": "Solana", "market_type": "perp", "is_active": True},
    {"id": "xrp", "symbol": "XRP", "name": "XRP", "market_type": "perp", "is_active": True},
    {"id": "doge", "symbol": "DOGE", "name": "Dogecoin", "market_type": "perp", "is_active": True},
]

SIGNALS = [
    {
        "id": "sig_btc_hidden_1",
        "token_id": "btc",
        "token_symbol": "BTC",
        "triggered_at": datetime.now(timezone.utc) - timedelta(minutes=18),
        "signal_type": SignalType.HIDDEN_ACCUMULATION,
        "signal_score": 78.0,
        "confidence": 0.81,
        "status": SignalStatus.ACTIVE,
        "explanation": {
            "why_now": "Structure is firming while public attention remains muted and perp positioning is not crowded.",
            "risks": ["Breakout may fail if volume fades.", "Funding can reheat quickly after a sharp squeeze."],
            "suggested_action": "Keep BTC on high alert and look for continuation only if structure stays efficient.",
            "invalidation_conditions": ["1h return loses momentum", "absorption score falls below recent baseline"],
            "evidence": ["Positive structure divergence", "Attention still below breakout threshold"],
        },
        "invalidation_json": {"price_break": "below local support", "funding_shift": "funding_zscore > 1.5"},
    },
    {
        "id": "sig_sol_narrative_1",
        "token_id": "sol",
        "token_symbol": "SOL",
        "triggered_at": datetime.now(timezone.utc) - timedelta(minutes=42),
        "signal_type": SignalType.NARRATIVE_IGNITION,
        "signal_score": 84.0,
        "confidence": 0.77,
        "status": SignalStatus.ACTIVE,
        "explanation": {
            "why_now": "Attention and structure are both accelerating, but positioning is still early enough to avoid outright overheating.",
            "risks": ["Narrative can overshoot and reverse.", "Crowding risk rises if OI expands too fast."],
            "suggested_action": "Treat SOL as an emerging trend candidate and wait for follow-through instead of chasing spikes.",
            "invalidation_conditions": ["mention acceleration stalls", "trade imbalance rolls over"],
            "evidence": ["Social acceleration rising", "Market structure confirming"],
        },
        "invalidation_json": {"social_stall": True, "structure_rollover": True},
    },
]

WATCHLIST_TOKEN_IDS = ["btc", "sol", "eth"]
