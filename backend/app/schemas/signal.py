from datetime import datetime
from typing import Any

from app.models.enums import SignalStatus, SignalType
from app.schemas.common import AppBaseModel


class ExplanationCard(AppBaseModel):
    why_now: str
    risks: list[str]
    suggested_action: str
    invalidation_conditions: list[str]
    evidence: list[str]


class SignalResponse(AppBaseModel):
    id: str
    token_id: str
    token_symbol: str
    triggered_at: datetime
    signal_type: SignalType
    signal_score: float
    confidence: float
    status: SignalStatus
    explanation: ExplanationCard
    invalidation_json: dict[str, Any]

