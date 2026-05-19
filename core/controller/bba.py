from __future__ import annotations

import math
from numbers import Real

from .base import BaseController
from .contract import quantize_rate_to_level


DEFAULT_RESERVOIR_S = 5.0
DEFAULT_CUSHION_S = 10.0


class BbaController(BaseController):
    """BBA-0 style reservoir/cushion buffer-map controller."""

    name = "bba"

    def __init__(self, reservoir_s=DEFAULT_RESERVOIR_S, cushion_s=DEFAULT_CUSHION_S, **_unused):
        super().__init__()
        self.reservoir_s = _non_negative_float(reservoir_s, DEFAULT_RESERVOIR_S)
        self.cushion_s = _positive_float(cushion_s, DEFAULT_CUSHION_S)
        self._last_rates_Bps = []
        self.last_metrics = {}

    def calcControlAction(self):
        feedback = self.feedback or {}
        rates = _available_rates_Bps(feedback)
        self._last_rates_Bps = rates

        if not rates:
            return _finish(self, 0.0)

        buffer_s = _finite_float(feedback.get("queued_time"))
        if len(rates) == 1:
            return self._finish_decision(rates, 0, buffer_s, "single_representation")

        if buffer_s is None or buffer_s < 0.0:
            return self._finish_decision(rates, 0, buffer_s, "invalid_buffer_fallback")

        high_threshold_s = self.reservoir_s + self.cushion_s
        if buffer_s <= self.reservoir_s:
            chosen_level = 0
            reason = "reservoir"
        elif buffer_s >= high_threshold_s:
            chosen_level = len(rates) - 1
            reason = "upper_cushion"
        else:
            # BBA-0 maps buffer position inside the cushion to a discrete representation index.
            position = (buffer_s - self.reservoir_s) / self.cushion_s
            chosen_level = int(math.floor(position * (len(rates) - 1)))
            chosen_level = _clamp_level(chosen_level, rates)
            reason = "cushion"

        return self._finish_decision(rates, chosen_level, buffer_s, reason)

    def quantizeRate(self, rate):
        if self._last_rates_Bps:
            try:
                return quantize_rate_to_level(rate, self._last_rates_Bps)
            except ValueError:
                return 0
        return super().quantizeRate(rate)

    def _finish_decision(self, rates, chosen_level, buffer_s, reason):
        chosen_level = _clamp_level(chosen_level, rates)
        chosen_rate = float(rates[chosen_level])
        self.last_metrics = {
            "reason": reason,
            "buffer_s": buffer_s,
            "reservoir_s": self.reservoir_s,
            "cushion_s": self.cushion_s,
            "chosen_level": chosen_level,
            "target_rate_Bps": chosen_rate,
        }
        return _finish(self, chosen_rate)


def _available_rates_Bps(feedback):
    if not feedback:
        return []

    raw_rates = feedback.get("rates", []) or []
    try:
        values = list(raw_rates)
    except TypeError:
        return []
    if not values:
        return []

    rates = []
    for value in values:
        rate = _finite_float(value)
        if rate is None or rate <= 0.0:
            return []
        rates.append(rate)

    max_level = _to_int(feedback.get("max_level"), len(rates) - 1)
    max_level = max(0, min(max_level, len(rates) - 1))
    return rates[: max_level + 1]


def _clamp_level(value, rates):
    if not rates:
        return 0
    level = _to_int(value, 0)
    return max(0, min(level, len(rates) - 1))


def _finish(controller, rate):
    controller.setIdleDuration(0.0)
    controller.setControlAction(float(rate))
    return float(rate)


def _non_negative_float(value, default):
    parsed = _finite_float(value)
    if parsed is None or parsed < 0.0:
        return float(default)
    return float(parsed)


def _positive_float(value, default):
    parsed = _finite_float(value)
    if parsed is None or parsed <= 0.0:
        return float(default)
    return float(parsed)


def _finite_float(value):
    if isinstance(value, bool) or not isinstance(value, Real):
        return None
    parsed = float(value)
    if not math.isfinite(parsed):
        return None
    return parsed


def _to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
