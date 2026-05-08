from __future__ import annotations

from .base import BaseController


class FixedQualityController(BaseController):
    """Deterministic test/debug controller that always selects one level."""

    name = "fixed_quality"

    def __init__(self, level: int = 0):
        super().__init__()
        self.level = level

    def calcControlAction(self):
        feedback = self.feedback or {}
        rates = feedback.get("rates", []) or []

        if not rates:
            self.setIdleDuration(0.0)
            self.setControlAction(0.0)
            return 0.0

        chosen_level = _clamp_level(self.level, rates, feedback.get("max_level"))
        chosen_rate = rates[chosen_level]

        self.setIdleDuration(0.0)
        self.setControlAction(chosen_rate)
        return chosen_rate

    def __repr__(self):
        return "<FixedQualityController level={0}>".format(self.level)


def _clamp_level(level, rates, feedback_max_level=None):
    max_available_level = len(rates) - 1
    max_level = _to_int(feedback_max_level, max_available_level)
    max_level = max(0, min(max_level, max_available_level))

    requested_level = _to_int(level, 0)
    return max(0, min(requested_level, max_level))


def _to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
