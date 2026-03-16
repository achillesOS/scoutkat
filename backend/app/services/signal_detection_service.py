from app.models.enums import SignalType
from app.scoring.config import load_thresholds
from app.scoring.engine import ScoreBundle


class SignalDetectionService:
    def __init__(self) -> None:
        self.thresholds = load_thresholds()

    def detect(self, scores: ScoreBundle) -> dict:
        if (
            scores.signal_score < self.thresholds["candidate_signal_floor"]
            or scores.confidence < self.thresholds["confidence_floor"]
        ):
            return {
                "is_candidate": False,
                "signal_type": SignalType.NEUTRAL,
                "priority": "none",
            }

        priority = (
            "high"
            if scores.signal_score >= self.thresholds["high_priority_signal_floor"]
            else "normal"
        )
        return {
            "is_candidate": True,
            "signal_type": scores.signal_type,
            "priority": priority,
        }

