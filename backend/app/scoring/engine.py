from dataclasses import dataclass

from app.models.enums import SignalType
from app.scoring.config import load_weights


def clamp(value: float, floor: float = 0.0, ceiling: float = 1.0) -> float:
    return max(floor, min(ceiling, value))


def normalize_unit_to_100(value: float) -> float:
    return round(clamp((value + 1) / 2, 0.0, 1.0) * 100, 2)


def positive_part(value: float) -> float:
    return max(value, 0.0)


def negative_part(value: float) -> float:
    return max(-value, 0.0)


@dataclass
class ScoreBundle:
    attention_score: float
    structure_score: float
    positioning_score: float
    hidden_accumulation_score: float
    narrative_ignition_score: float
    retail_trap_score: float
    signal_type: SignalType
    signal_score: float
    confidence: float


class ScoringEngine:
    def __init__(self) -> None:
        self.weights = load_weights()

    def compute_component_scores(
        self, attention: dict, market: dict, positioning: dict
    ) -> tuple[float, float, float]:
        component_weights = self.weights["component_weights"]
        attention_score = sum(
            attention.get(metric, 0.0) * weight
            for metric, weight in component_weights["attention"].items()
        )
        structure_score = sum(
            market.get(metric, 0.0) * weight
            for metric, weight in component_weights["structure"].items()
        )
        positioning_score = sum(
            positioning.get(metric, 0.0) * weight
            for metric, weight in component_weights["positioning"].items()
        )
        return attention_score, structure_score, positioning_score

    def compute_signal_scores(
        self,
        attention_score: float,
        structure_score: float,
        positioning_score: float,
        delta_attention: float,
        delta_structure: float,
        completeness: float,
    ) -> ScoreBundle:
        signal_weights = self.weights["signal_weights"]

        hidden = (
            signal_weights["hidden_accumulation"]["structure_score"] * structure_score
            + signal_weights["hidden_accumulation"]["attention_score"] * attention_score
            + signal_weights["hidden_accumulation"]["positioning_score"] * positioning_score
        )
        ignition = (
            signal_weights["narrative_ignition"]["attention_score"] * attention_score
            + signal_weights["narrative_ignition"]["structure_score"] * structure_score
            + signal_weights["narrative_ignition"]["positioning_score"] * positioning_score
            + signal_weights["narrative_ignition"]["delta_attention"] * positive_part(delta_attention)
            + signal_weights["narrative_ignition"]["delta_structure"] * positive_part(delta_structure)
        )
        trap = (
            signal_weights["retail_trap"]["attention_score"] * attention_score
            + signal_weights["retail_trap"]["structure_score"] * structure_score
            + signal_weights["retail_trap"]["positioning_score"] * positioning_score
            + signal_weights["retail_trap"]["delta_attention"] * positive_part(delta_attention)
            + abs(signal_weights["retail_trap"]["delta_structure"]) * negative_part(delta_structure)
        )

        raw_scores = {
            SignalType.HIDDEN_ACCUMULATION: hidden,
            SignalType.NARRATIVE_IGNITION: ignition,
            SignalType.RETAIL_TRAP: trap,
        }
        ranked = sorted(raw_scores.items(), key=lambda item: item[1], reverse=True)
        signal_type, leader_raw = ranked[0]
        runner_up_raw = ranked[1][1]
        gap = max(leader_raw - runner_up_raw, 0.0)
        signal_score = round(min(normalize_unit_to_100(leader_raw) + (clamp(gap / 0.18) * 8), 100.0), 2)
        conviction = clamp((signal_score - 55) / 20, 0.0, 1.0)
        separation = clamp(gap / 0.18, 0.0, 1.0)
        consistency = clamp((abs(structure_score) + abs(attention_score) + abs(positioning_score)) / 3)
        confidence = round(
            clamp((0.45 * conviction) + (0.30 * separation) + (0.15 * consistency) + (0.10 * completeness)),
            2,
        )

        return ScoreBundle(
            attention_score=round(normalize_unit_to_100(attention_score), 2),
            structure_score=round(normalize_unit_to_100(structure_score), 2),
            positioning_score=round(normalize_unit_to_100(positioning_score), 2),
            hidden_accumulation_score=round(normalize_unit_to_100(hidden), 2),
            narrative_ignition_score=round(normalize_unit_to_100(ignition), 2),
            retail_trap_score=round(normalize_unit_to_100(trap), 2),
            signal_type=signal_type,
            signal_score=signal_score,
            confidence=confidence,
        )
