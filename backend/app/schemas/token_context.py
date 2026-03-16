from datetime import datetime

from app.models.enums import SignalType
from app.schemas.common import AppBaseModel
from app.schemas.signal import SignalResponse


class TokenHeaderResponse(AppBaseModel):
    id: str
    symbol: str
    name: str
    market_type: str
    current_price: float
    change_1h: float
    change_4h: float
    change_24h: float
    last_updated: datetime


class CurrentSignalStateResponse(AppBaseModel):
    signal_type: SignalType
    signal_score: float
    confidence: float
    why_now: str
    risks: list[str]
    invalidation: list[str]


class DivergencePointResponse(AppBaseModel):
    timestamp: datetime
    attention_score: float
    structure_score: float
    positioning_score: float


class DivergenceChartResponse(AppBaseModel):
    default_timeframe: str
    series: dict[str, list[DivergencePointResponse]]


class RecentStateChangeResponse(AppBaseModel):
    timestamp: datetime
    title: str
    detail: str
    signal_type: SignalType


class TokenContextResponse(AppBaseModel):
    header: TokenHeaderResponse
    current_signal_state: CurrentSignalStateResponse
    divergence_chart: DivergenceChartResponse
    recent_state_changes: list[RecentStateChangeResponse]
    recent_signal_history: list[SignalResponse]
