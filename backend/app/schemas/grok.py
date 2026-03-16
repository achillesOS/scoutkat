from typing import Literal

from pydantic import BaseModel, Field


class GrokSignalHint(BaseModel):
    likely_pattern: Literal[
        "hidden_accumulation",
        "narrative_ignition",
        "retail_trap",
        "unclear",
    ]
    reason: str = Field(min_length=4, max_length=400)


class GrokAttentionExtraction(BaseModel):
    token_symbol: str = Field(min_length=1, max_length=20)
    time_window: str = Field(min_length=1, max_length=20)
    mentions_1h_estimate: int = Field(ge=0, le=500000)
    mentions_6h_estimate: int = Field(ge=0, le=2000000)
    unique_authors_1h_estimate: int = Field(ge=0, le=500000)
    attention_level: Literal["low", "medium", "high", "extreme"]
    attention_acceleration: Literal["falling", "flat", "rising", "spiking"]
    discussion_type: Literal[
        "retail_hype",
        "expert_attention",
        "mixed",
        "news_reaction",
        "unclear",
    ]
    new_information_present: bool
    new_information_summary: list[str] = Field(default_factory=list, max_length=5)
    retail_breadth_level: Literal["low", "medium", "high"]
    expert_presence_level: Literal["low", "medium", "high"]
    narrative_novelty: float = Field(ge=0.0, le=1.0)
    top_narratives: list[str] = Field(default_factory=list, max_length=5)
    signal_hint: GrokSignalHint
    confidence: float = Field(ge=0.0, le=1.0)


class GrokNormalizedAttention(BaseModel):
    token_symbol: str
    time_window: str
    mentions_1h: int = Field(ge=0)
    mentions_6h: int = Field(ge=0)
    unique_authors_1h: int = Field(ge=0)
    mention_acceleration: float = Field(ge=0.0, le=1.0)
    retail_breadth: float = Field(ge=0.0, le=1.0)
    expert_presence: float = Field(ge=0.0, le=1.0)
    narrative_novelty: float = Field(ge=0.0, le=1.0)
    signal_hint: str
    confidence: float = Field(ge=0.0, le=1.0)
    snapshot_incomplete: bool = False
    raw_provider_response: dict
    validated_payload: dict | None = None
    validation_error: str | None = None
