from __future__ import annotations

from math import sqrt

from app.scoring.engine import clamp


def percentile_rank(current: float, history: list[float]) -> float:
    samples = [float(value) for value in history if value is not None]
    if not samples:
        return clamp(current, -1.0, 1.0) if -1.0 <= current <= 1.0 else 0.5
    less_or_equal = sum(1 for value in samples if value <= current)
    return less_or_equal / len(samples)


def zscore(current: float, history: list[float]) -> float:
    samples = [float(value) for value in history if value is not None]
    if len(samples) < 2:
        return 0.0
    mean = sum(samples) / len(samples)
    variance = sum((value - mean) ** 2 for value in samples) / len(samples)
    std = sqrt(variance)
    if std == 0:
        return 0.0
    return (current - mean) / std


def zscore_to_unit(current: float, history: list[float], scale: float = 2.5) -> float:
    return clamp(zscore(current, history) / scale, -1.0, 1.0)


def percentile_to_unit(current: float, history: list[float]) -> float:
    return clamp(percentile_rank(current, history) * 2 - 1, -1.0, 1.0)


def blend_normalized(current: float, history: list[float], *, scale: float = 2.5) -> float:
    z_component = zscore_to_unit(current, history, scale=scale)
    percentile_component = percentile_to_unit(current, history)
    return clamp((0.6 * z_component) + (0.4 * percentile_component), -1.0, 1.0)
