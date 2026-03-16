from pydantic import BaseModel, Field


class ExplanationOutput(BaseModel):
    why_now: str = Field(min_length=12, max_length=400)
    risks: list[str] = Field(min_length=1, max_length=4)
    suggested_action: str = Field(min_length=8, max_length=240)
    invalidation_conditions: list[str] = Field(min_length=1, max_length=4)
    evidence: list[str] = Field(min_length=2, max_length=6)

