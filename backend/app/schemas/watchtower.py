from datetime import datetime

from app.models.enums import SignalType
from app.schemas.common import AppBaseModel


class WatchtowerHeroCardResponse(AppBaseModel):
    title: str
    token_symbol: str
    signal_type: SignalType
    signal_score: float
    confidence: float
    current_price: float
    change_24h: float
    why_now: str


class WatchtowerAssetResponse(AppBaseModel):
    id: str
    symbol: str
    name: str
    market_type: str
    current_price: float
    change_1h: float
    change_24h: float
    signal_type: SignalType
    signal_score: float
    confidence: float
    last_updated: datetime
    why_now: str


class WatchtowerResponse(AppBaseModel):
    last_refresh: datetime
    tracked_assets_count: int
    active_signals_count: int
    recently_changed_count: int
    hero_cards: list[WatchtowerHeroCardResponse]
    assets: list[WatchtowerAssetResponse]
