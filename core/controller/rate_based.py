from __future__ import annotations

import math
from collections.abc import Mapping
from numbers import Real

from .base import BaseController
from .contract import quantize_rate_to_level


DEFAULT_SAFETY_FACTOR = 0.85
DEFAULT_EWMA_ALPHA = 0.5
DEFAULT_CRITICAL_BUFFER_S = 2.0
DEFAULT_STARTUP_LEVEL = 0
DEFAULT_MAX_UPSHIFT_LEVELS = 1


class RateBasedController(BaseController):
    """Application-layer throughput ABR baseline derived from Liu et al. 2011."""

    name = "rate_based"

    def __init__(
        self,
        safety_factor=DEFAULT_SAFETY_FACTOR,
        ewma_alpha=DEFAULT_EWMA_ALPHA,
        critical_buffer_s=DEFAULT_CRITICAL_BUFFER_S,
        startup_level=None,
        startup_quality=None,
        conservative_upshift=True,
        conservative_up=None,
        max_upshift_levels=DEFAULT_MAX_UPSHIFT_LEVELS,
        aggressive_downshift=True,
        allow_multi_level_down=None,
        min_valid_download_time_s=0.0,
        **_unused,
    ):
        super().__init__()
        self.safety_factor = _bounded_float(safety_factor, DEFAULT_SAFETY_FACTOR, minimum=0.0, maximum=1.0)
        self.ewma_alpha = _bounded_float(ewma_alpha, DEFAULT_EWMA_ALPHA, minimum=0.0, maximum=1.0)
        self.critical_buffer_s = _non_negative_float(critical_buffer_s, DEFAULT_CRITICAL_BUFFER_S)
        self.startup_level = _to_int(_first_not_none(startup_level, startup_quality), DEFAULT_STARTUP_LEVEL)
        self.conservative_upshift = bool(conservative_upshift if conservative_up is None else conservative_up)
        self.max_upshift_levels = max(1, _to_int(max_upshift_levels, DEFAULT_MAX_UPSHIFT_LEVELS))
        self.aggressive_downshift = bool(
            aggressive_downshift if allow_multi_level_down is None else allow_multi_level_down
        )
        self.min_valid_download_time_s = _non_negative_float(min_valid_download_time_s, 0.0)

        self._smoothed_throughput_Bps = None
        self._last_rates_Bps = []
        self._last_level = None
        self.last_metrics = {}

    def calcControlAction(self):
        feedback = self.feedback or {}
        rates = _available_rates_Bps(feedback)
        self._last_rates_Bps = rates

        if not rates:
            return _finish(self, 0.0)

        current_level = _current_level(feedback, rates, self._last_level)
        startup_level = _clamp_level(self.startup_level, rates)

        if len(rates) == 1:
            return self._finish_decision(
                rates=rates,
                chosen_level=0,
                current_level=current_level,
                measured_throughput_Bps=None,
                decision_throughput_Bps=None,
                safe_throughput_Bps=None,
                reason="single_representation",
            )

        measured_throughput_Bps = _measured_throughput_Bps(feedback, self.min_valid_download_time_s)
        decision_throughput_Bps = self._decision_throughput(feedback, measured_throughput_Bps, current_level, rates)

        if decision_throughput_Bps is None:
            return self._finish_decision(
                rates=rates,
                chosen_level=startup_level,
                current_level=current_level,
                measured_throughput_Bps=None,
                decision_throughput_Bps=None,
                safe_throughput_Bps=None,
                reason="startup_fallback",
            )

        # All ladder rates and throughput estimates are bytes per second.
        safe_throughput_Bps = max(0.0, decision_throughput_Bps * self.safety_factor)
        candidate_level = _floor_rate_to_level(safe_throughput_Bps, rates)
        candidate_level = self._apply_buffer_guard(feedback, candidate_level, current_level)
        candidate_level = self._apply_transition_rule(candidate_level, current_level)

        return self._finish_decision(
            rates=rates,
            chosen_level=candidate_level,
            current_level=current_level,
            measured_throughput_Bps=measured_throughput_Bps,
            decision_throughput_Bps=decision_throughput_Bps,
            safe_throughput_Bps=safe_throughput_Bps,
            reason="throughput_selection",
        )

    def quantizeRate(self, rate):
        if self._last_rates_Bps:
            try:
                return quantize_rate_to_level(rate, self._last_rates_Bps)
            except ValueError:
                return 0
        return super().quantizeRate(rate)

    def _decision_throughput(self, feedback, measured_throughput_Bps, current_level, rates):
        if measured_throughput_Bps is None:
            history_estimate = _history_throughput_Bps(feedback)
            if history_estimate is not None:
                measured_throughput_Bps = history_estimate
            elif self._smoothed_throughput_Bps is not None:
                return self._smoothed_throughput_Bps
            else:
                return None

        previous = self._smoothed_throughput_Bps
        if previous is None:
            self._smoothed_throughput_Bps = measured_throughput_Bps
            return measured_throughput_Bps

        smoothed = self.ewma_alpha * measured_throughput_Bps + (1.0 - self.ewma_alpha) * previous
        self._smoothed_throughput_Bps = smoothed

        if self.aggressive_downshift:
            current_rate = rates[_clamp_level(current_level, rates)]
            if measured_throughput_Bps * self.safety_factor < current_rate:
                return min(smoothed, measured_throughput_Bps)
        return smoothed

    def _apply_buffer_guard(self, feedback, candidate_level, current_level):
        buffer_s = _finite_float(feedback.get("queued_time"))
        current_level = _clamp_level(current_level, self._last_rates_Bps)
        candidate_level = _clamp_level(candidate_level, self._last_rates_Bps)

        if buffer_s is None:
            return min(candidate_level, current_level)
        if buffer_s <= self.critical_buffer_s:
            return min(candidate_level, max(0, current_level - 1))
        return candidate_level

    def _apply_transition_rule(self, candidate_level, current_level):
        candidate_level = _clamp_level(candidate_level, self._last_rates_Bps)
        current_level = _clamp_level(current_level, self._last_rates_Bps)

        if candidate_level > current_level and self.conservative_upshift:
            return min(candidate_level, current_level + self.max_upshift_levels)
        if candidate_level < current_level and not self.aggressive_downshift:
            return max(candidate_level, current_level - 1)
        return candidate_level

    def _finish_decision(
        self,
        rates,
        chosen_level,
        current_level,
        measured_throughput_Bps,
        decision_throughput_Bps,
        safe_throughput_Bps,
        reason,
    ):
        chosen_level = _clamp_level(chosen_level, rates)
        chosen_rate = float(rates[chosen_level])
        self._last_level = chosen_level
        self.last_metrics = {
            "reason": reason,
            "current_level": current_level,
            "chosen_level": chosen_level,
            "target_rate_Bps": chosen_rate,
            "measured_throughput_Bps": measured_throughput_Bps,
            "smoothed_throughput_Bps": self._smoothed_throughput_Bps,
            "decision_throughput_Bps": decision_throughput_Bps,
            "safe_throughput_Bps": safe_throughput_Bps,
            "safety_factor": self.safety_factor,
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

    rates_unit = feedback.get("rates_unit", "bytes_per_second")
    rates = []
    for raw_rate in values:
        rate = _rate_to_bytes_per_second(raw_rate, rates_unit)
        if rate is None or rate <= 0.0:
            return []
        rates.append(rate)

    max_level = _to_int(feedback.get("max_level"), len(rates) - 1)
    max_level = max(0, min(max_level, len(rates) - 1))
    return rates[: max_level + 1]


def _measured_throughput_Bps(feedback, min_valid_download_time_s):
    for key, unit in (
        ("measured_throughput_Bps", "bytes_per_second"),
        ("measured_throughput", "bytes_per_second"),
        ("throughput_Bps", "bytes_per_second"),
        ("throughput", "bytes_per_second"),
        ("bwe", "bytes_per_second"),
        ("measured_throughput_bps", "bits_per_second"),
        ("throughput_bps", "bits_per_second"),
        ("measured_throughput_kbps", "kilobits_per_second"),
        ("throughput_kbps", "kilobits_per_second"),
    ):
        if key in feedback:
            throughput = _rate_to_bytes_per_second(feedback.get(key), unit)
            if throughput is not None and throughput > 0.0:
                return throughput

    last_size = _finite_float(feedback.get("last_fragment_size"))
    last_time = _finite_float(feedback.get("last_download_time"))
    if last_size is None or last_size <= 0.0:
        return None
    if last_time is None or last_time <= min_valid_download_time_s:
        return None

    return last_size / last_time


def _history_throughput_Bps(feedback):
    for key, unit in (
        ("throughput_history_Bps", "bytes_per_second"),
        ("throughput_history", "bytes_per_second"),
        ("throughput_history_bps", "bits_per_second"),
        ("throughput_history_kbps", "kilobits_per_second"),
    ):
        if key not in feedback:
            continue
        try:
            values = list(feedback.get(key) or [])
        except TypeError:
            continue
        normalized = []
        for value in values:
            throughput = _rate_to_bytes_per_second(value, unit)
            if throughput is not None and throughput > 0.0:
                normalized.append(throughput)
        if normalized:
            return min(normalized)
    return None


def _rate_to_bytes_per_second(value, default_unit):
    if isinstance(value, Mapping):
        unit = value.get("unit", default_unit)
        raw_value = _first_not_none(value.get("rate"), value.get("bitrate"), value.get("bandwidth"))
    else:
        unit = default_unit
        raw_value = value

    rate = _finite_float(raw_value)
    if rate is None:
        return None

    normalized_unit = str(unit or "bytes_per_second").strip().lower()
    normalized_unit = normalized_unit.replace("-", "_").replace(" ", "_")

    if normalized_unit in {"bytes_per_second", "byte_per_second", "bytes/s", "byte/s", "b/s", "bps_bytes"}:
        return rate
    if normalized_unit in {"bits_per_second", "bit_per_second", "bps", "bit/s", "bits/s"}:
        return rate / 8.0
    if normalized_unit in {"kilobits_per_second", "kbps", "kbit/s", "kbits/s"}:
        return (rate * 1000.0) / 8.0
    if normalized_unit in {"megabits_per_second", "mbps", "mbit/s", "mbits/s"}:
        return (rate * 1000000.0) / 8.0
    return rate


def _floor_rate_to_level(target_rate, rates):
    level = 0
    for index, rate in enumerate(rates):
        if target_rate >= rate:
            level = index
    return level


def _current_level(feedback, rates, last_level):
    default_level = 0 if last_level is None else last_level
    return _clamp_level(_to_int(feedback.get("level"), default_level), rates)


def _clamp_level(value, rates):
    if not rates:
        return 0
    level = _to_int(value, 0)
    return max(0, min(level, len(rates) - 1))


def _finish(controller, rate):
    controller.setIdleDuration(0.0)
    controller.setControlAction(float(rate))
    return float(rate)


def _bounded_float(value, default, minimum, maximum):
    parsed = _finite_float(value)
    if parsed is None:
        return float(default)
    if parsed <= minimum:
        return float(default)
    return float(min(parsed, maximum))


def _non_negative_float(value, default):
    parsed = _finite_float(value)
    if parsed is None or parsed < 0.0:
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


def _first_not_none(*values):
    for value in values:
        if value is not None:
            return value
    return None
