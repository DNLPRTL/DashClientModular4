from __future__ import annotations

import math
from collections.abc import Mapping
from numbers import Real

from .base import BaseController
from .contract import quantize_rate_to_level


DEFAULT_BOLA_V = 5.0
DEFAULT_BOLA_GAMMA = 0.2
DEFAULT_MIN_SEGMENT_DURATION_S = 0.001
DEFAULT_UTILITY_MODE = "log_rate_ratio"
DEFAULT_SIZE_MODE = "exact_or_bitrate_duration"
DEFAULT_ALL_NEGATIVE_POLICY = "min_rate"


class BolaController(BaseController):
    """BOLA-basic utility/buffer score controller.

    Implements the local BOLA-basic spec in
    docs/science/01_baselines/bola/implementation_spec.md.
    """

    name = "bola"

    def __init__(
        self,
        bola_v=None,
        V=None,
        v=None,
        bola_gamma=None,
        gamma=None,
        low_buffer_fallback_s=None,
        bola_qlow_s=None,
        qlow_s=None,
        min_segment_duration_s=DEFAULT_MIN_SEGMENT_DURATION_S,
        utility_mode=DEFAULT_UTILITY_MODE,
        size_mode=DEFAULT_SIZE_MODE,
        all_negative_policy=DEFAULT_ALL_NEGATIVE_POLICY,
        **_unused,
    ):
        super().__init__()
        self.bola_v = _positive_float(_first_not_none(bola_v, V, v), DEFAULT_BOLA_V)
        self.bola_gamma = _positive_float(_first_not_none(bola_gamma, gamma), DEFAULT_BOLA_GAMMA)
        self.low_buffer_fallback_s = _optional_non_negative_float(
            _first_not_none(low_buffer_fallback_s, bola_qlow_s, qlow_s)
        )
        self.min_segment_duration_s = _positive_float(min_segment_duration_s, DEFAULT_MIN_SEGMENT_DURATION_S)
        self.utility_mode = _normalized_choice(utility_mode, {DEFAULT_UTILITY_MODE}, DEFAULT_UTILITY_MODE)
        self.size_mode = _normalized_choice(
            size_mode,
            {DEFAULT_SIZE_MODE, "bitrate_times_duration"},
            DEFAULT_SIZE_MODE,
        )
        self.all_negative_policy = _normalized_choice(
            all_negative_policy,
            {DEFAULT_ALL_NEGATIVE_POLICY},
            DEFAULT_ALL_NEGATIVE_POLICY,
        )
        self._last_rates_Bps = []
        self.last_metrics = {}

    def calcControlAction(self):
        feedback = self.feedback or {}
        rates = _available_rates_Bps(feedback)
        self._last_rates_Bps = rates

        if not rates:
            self.last_metrics = {"reason": "invalid_ladder", "target_rate_Bps": 0.0}
            return _finish(self, 0.0)

        buffer_s = _finite_float(feedback.get("queued_time"))
        segment_duration_s = _finite_float(feedback.get("fragment_duration"))

        if len(rates) == 1:
            return self._finish_decision(
                rates=rates,
                chosen_level=0,
                buffer_s=buffer_s,
                segment_duration_s=segment_duration_s,
                reason="single_representation",
            )

        if buffer_s is None or buffer_s < 0.0:
            return self._finish_decision(
                rates=rates,
                chosen_level=0,
                buffer_s=buffer_s,
                segment_duration_s=segment_duration_s,
                reason="invalid_buffer_fallback",
            )

        if segment_duration_s is None or segment_duration_s < self.min_segment_duration_s:
            return self._finish_decision(
                rates=rates,
                chosen_level=0,
                buffer_s=buffer_s,
                segment_duration_s=segment_duration_s,
                reason="invalid_segment_duration_fallback",
            )

        low_buffer_fallback_s = self._low_buffer_fallback_s(segment_duration_s)
        if buffer_s <= low_buffer_fallback_s:
            return self._finish_decision(
                rates=rates,
                chosen_level=0,
                buffer_s=buffer_s,
                segment_duration_s=segment_duration_s,
                reason="low_buffer_fallback",
                low_buffer_fallback_s=low_buffer_fallback_s,
            )

        utilities = _utilities_log_rate_ratio(rates)
        sizes_B = _candidate_segment_sizes_B(feedback, rates, segment_duration_s, self.size_mode)
        min_size_B = min(sizes_B)
        size_units = [size_B / min_size_B for size_B in sizes_B]
        q_segments = buffer_s / segment_duration_s

        scores = []
        best_level = 0
        best_score = -math.inf
        for level, utility in enumerate(utilities):
            score = (
                self.bola_v * (utility + self.bola_gamma * segment_duration_s) - q_segments
            ) / size_units[level]
            scores.append(score)
            if score > best_score:
                best_score = score
                best_level = level

        reason = "score_selection"
        chosen_level = best_level
        if best_score <= 0.0 and self.all_negative_policy == DEFAULT_ALL_NEGATIVE_POLICY:
            chosen_level = 0
            reason = "all_non_positive_scores_min_rate_fallback"

        return self._finish_decision(
            rates=rates,
            chosen_level=chosen_level,
            buffer_s=buffer_s,
            segment_duration_s=segment_duration_s,
            reason=reason,
            low_buffer_fallback_s=low_buffer_fallback_s,
            q_segments=q_segments,
            utilities=utilities,
            segment_sizes_B=sizes_B,
            size_units=size_units,
            scores=scores,
            raw_best_level=best_level,
            raw_best_score=best_score,
        )

    def quantizeRate(self, rate):
        if self._last_rates_Bps:
            try:
                return quantize_rate_to_level(rate, self._last_rates_Bps)
            except ValueError:
                return 0
        return super().quantizeRate(rate)

    def _low_buffer_fallback_s(self, segment_duration_s):
        if self.low_buffer_fallback_s is None:
            return float(segment_duration_s)
        return float(self.low_buffer_fallback_s)

    def _finish_decision(
        self,
        rates,
        chosen_level,
        buffer_s,
        segment_duration_s,
        reason,
        low_buffer_fallback_s=None,
        q_segments=None,
        utilities=None,
        segment_sizes_B=None,
        size_units=None,
        scores=None,
        raw_best_level=None,
        raw_best_score=None,
    ):
        chosen_level = _clamp_level(chosen_level, rates)
        chosen_rate = float(rates[chosen_level])
        self.last_metrics = {
            "reason": reason,
            "buffer_s": buffer_s,
            "segment_duration_s": segment_duration_s,
            "low_buffer_fallback_s": low_buffer_fallback_s,
            "q_segments": q_segments,
            "bola_v": self.bola_v,
            "bola_gamma": self.bola_gamma,
            "utility_mode": self.utility_mode,
            "size_mode": self.size_mode,
            "all_negative_policy": self.all_negative_policy,
            "utilities_by_level": utilities,
            "segment_sizes_B": segment_sizes_B,
            "size_units_by_level": size_units,
            "scores_by_level": scores,
            "raw_best_level": raw_best_level,
            "raw_best_score": raw_best_score,
            "chosen_level": chosen_level,
            "target_rate_Bps": chosen_rate,
            "no_download_wait_supported": False,
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


def _utilities_log_rate_ratio(rates):
    min_rate = min(rates)
    return [math.log(rate / min_rate) for rate in rates]


def _candidate_segment_sizes_B(feedback, rates, segment_duration_s, size_mode):
    approximate = [float(rate) * float(segment_duration_s) for rate in rates]
    if size_mode == "bitrate_times_duration":
        return approximate

    raw_sizes = _first_existing(
        feedback,
        (
            "segment_sizes_B",
            "segment_sizes_bytes",
            "segment_size_bytes_by_level",
            "representation_sizes_B",
            "representation_sizes_bytes",
            "size_bytes_by_level",
        ),
    )
    exact_sizes = _normalize_segment_sizes_B(raw_sizes, len(rates), feedback.get("segment_sizes_unit", "bytes"))
    if exact_sizes is None:
        return approximate
    return exact_sizes


def _normalize_segment_sizes_B(raw_sizes, count, default_unit):
    if raw_sizes is None:
        return None

    values = []
    if isinstance(raw_sizes, Mapping):
        for index in range(count):
            if index in raw_sizes:
                values.append(raw_sizes[index])
            elif str(index) in raw_sizes:
                values.append(raw_sizes[str(index)])
            else:
                return None
    else:
        try:
            values = list(raw_sizes)
        except TypeError:
            return None
        if len(values) < count:
            return None
        values = values[:count]

    sizes = []
    for value in values:
        size = _size_to_bytes(value, default_unit)
        if size is None or size <= 0.0:
            return None
        sizes.append(size)
    return sizes


def _rate_to_bytes_per_second(value, default_unit):
    if isinstance(value, Mapping):
        unit = value.get("unit", default_unit)
        raw_value = _first_not_none(value.get("rate"), value.get("bitrate"), value.get("bandwidth"), value.get("value"))
    else:
        unit = default_unit
        raw_value = value

    rate = _finite_float(raw_value)
    if rate is None:
        return None

    normalized_unit = _normalize_unit(unit, "bytes_per_second")
    if normalized_unit in {"bytes_per_second", "byte_per_second", "bytes/s", "byte/s", "b/s", "bps_bytes"}:
        return rate
    if normalized_unit in {"bits_per_second", "bit_per_second", "bps", "bit/s", "bits/s"}:
        return rate / 8.0
    if normalized_unit in {"kilobits_per_second", "kbps", "kbit/s", "kbits/s"}:
        return (rate * 1000.0) / 8.0
    if normalized_unit in {"megabits_per_second", "mbps", "mbit/s", "mbits/s"}:
        return (rate * 1000000.0) / 8.0
    return rate


def _size_to_bytes(value, default_unit):
    if isinstance(value, Mapping):
        unit = value.get("unit", default_unit)
        raw_value = _first_not_none(value.get("bytes"), value.get("size"), value.get("value"))
    else:
        unit = default_unit
        raw_value = value

    size = _finite_float(raw_value)
    if size is None:
        return None

    normalized_unit = _normalize_unit(unit, "bytes")
    if normalized_unit in {"bytes", "byte", "b_bytes"}:
        return size
    if normalized_unit in {"bits", "bit", "b"}:
        return size / 8.0
    if normalized_unit in {"kilobits", "kbit", "kbits", "kb"}:
        return (size * 1000.0) / 8.0
    if normalized_unit in {"megabits", "mbit", "mbits", "mb"}:
        return (size * 1000000.0) / 8.0
    return size


def _clamp_level(value, rates):
    if not rates:
        return 0
    level = _to_int(value, 0)
    return max(0, min(level, len(rates) - 1))


def _finish(controller, rate):
    controller.setIdleDuration(0.0)
    controller.setControlAction(float(rate))
    return float(rate)


def _positive_float(value, default):
    parsed = _finite_float(value)
    if parsed is None or parsed <= 0.0:
        return float(default)
    return float(parsed)


def _optional_non_negative_float(value):
    if value is None:
        return None
    parsed = _finite_float(value)
    if parsed is None or parsed < 0.0:
        return None
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


def _first_existing(mapping, keys):
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _normalized_choice(value, allowed, default):
    text = str(value or default).strip().lower()
    text = text.replace("-", "_").replace(" ", "_")
    if text in allowed:
        return text
    return default


def _normalize_unit(unit, default):
    text = str(unit or default).strip().lower()
    return text.replace("-", "_").replace(" ", "_")
