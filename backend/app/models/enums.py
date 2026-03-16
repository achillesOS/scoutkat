from enum import StrEnum


class SignalType(StrEnum):
    HIDDEN_ACCUMULATION = "hidden_accumulation"
    NARRATIVE_IGNITION = "narrative_ignition"
    RETAIL_TRAP = "retail_trap"
    NEUTRAL = "neutral"


class SignalStatus(StrEnum):
    ACTIVE = "active"
    COOLDOWN = "cooldown"
    INVALIDATED = "invalidated"
    RESOLVED = "resolved"

