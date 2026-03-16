import json
from functools import lru_cache

from app.core.config import get_settings


@lru_cache
def load_weights() -> dict:
    return json.loads(get_settings().scoring_weights_path.read_text())


@lru_cache
def load_thresholds() -> dict:
    return json.loads(get_settings().thresholds_path.read_text())

