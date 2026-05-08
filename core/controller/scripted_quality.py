from __future__ import annotations

from .base import BaseController


class ScriptedQualityController(BaseController):
    """Deterministic test/debug controller driven by segment_index."""

    name = "scripted_quality"

    def __init__(self, levels=None, repeat_last: bool = True):
        super().__init__()
        self.levels = _normalize_levels(levels)
        self.repeat_last = bool(repeat_last)

    def calcControlAction(self):
        feedback = self.feedback or {}
        rates = feedback.get("rates", []) or []

        if not rates:
            self.setIdleDuration(0.0)
            self.setControlAction(0.0)
            return 0.0

        segment_index = _to_non_negative_int(feedback.get("segment_index"), 0)
        selected_level = self._level_for_segment(segment_index)
        chosen_level = _clamp_level(selected_level, rates, feedback.get("max_level"))
        chosen_rate = rates[chosen_level]

        self.setIdleDuration(0.0)
        self.setControlAction(chosen_rate)
        return chosen_rate

    def _level_for_segment(self, segment_index):
        if segment_index < len(self.levels):
            return self.levels[segment_index]
        if self.repeat_last:
            return self.levels[-1]
        return 0

    def __repr__(self):
        return "<ScriptedQualityController levels={0} repeat_last={1}>".format(
            self.levels,
            self.repeat_last,
        )


def _normalize_levels(levels):
    if levels is None:
        return [0]
    if isinstance(levels, (str, bytes)):
        return [0]

    try:
        values = list(levels)
    except TypeError:
        return [0]

    if not values:
        return [0]

    normalized = []
    for value in values:
        normalized.append(_to_int(value, 0))
    return normalized or [0]


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


def _to_non_negative_int(value, default):
    parsed = _to_int(value, default)
    if parsed < 0:
        return default
    return parsed
