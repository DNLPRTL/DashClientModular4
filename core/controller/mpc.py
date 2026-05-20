from __future__ import annotations

import itertools
import math
from collections.abc import Mapping
from numbers import Real

from .base import BaseController
from .contract import quantize_rate_to_level


DEFAULT_HORIZON = 3
DEFAULT_THROUGHPUT_HISTORY_WINDOW = 5
DEFAULT_REBUFFER_PENALTY = 4.3
DEFAULT_SWITCH_PENALTY = 1.0
DEFAULT_STARTUP_LEVEL = 0
DEFAULT_MAX_ENUMERATED_SEQUENCES = 4096
DEFAULT_MIN_VALID_THROUGHPUT_BPS = 0.001
DEFAULT_MIN_SEGMENT_DURATION_S = 0.001
DEFAULT_QUALITY_REWARD_MODE = "log_rate_ratio"
DEFAULT_SIZE_MODE = "exact_or_bitrate_duration"


class MpcController(BaseController):
    """Small-horizon enumerative MPC ABR baseline.

    Implements the local MPC spec in
    docs/science/01_baselines/mpc/implementation_spec.md.
    """

    name = "mpc"

    def __init__(
        self,
        horizon=DEFAULT_HORIZON,
        throughput_history_window=DEFAULT_THROUGHPUT_HISTORY_WINDOW,
        rebuffer_penalty=DEFAULT_REBUFFER_PENALTY,
        switch_penalty=DEFAULT_SWITCH_PENALTY,
        startup_level=None,
        startup_quality=None,
        max_enumerated_sequences=DEFAULT_MAX_ENUMERATED_SEQUENCES,
        min_valid_throughput_Bps=None,
        min_valid_throughput=None,
        min_segment_duration_s=DEFAULT_MIN_SEGMENT_DURATION_S,
        quality_reward_mode=DEFAULT_QUALITY_REWARD_MODE,
        size_mode=DEFAULT_SIZE_MODE,
        **_unused,
    ):
        super().__init__()
        self.horizon = _positive_int(horizon, DEFAULT_HORIZON)
        self.throughput_history_window = _positive_int(
            throughput_history_window,
            DEFAULT_THROUGHPUT_HISTORY_WINDOW,
        )
        self.rebuffer_penalty = _non_negative_float(rebuffer_penalty, DEFAULT_REBUFFER_PENALTY)
        self.switch_penalty = _non_negative_float(switch_penalty, DEFAULT_SWITCH_PENALTY)
        self.startup_level = _to_int(_first_not_none(startup_level, startup_quality), DEFAULT_STARTUP_LEVEL)
        self.max_enumerated_sequences = _positive_int(
            max_enumerated_sequences,
            DEFAULT_MAX_ENUMERATED_SEQUENCES,
        )
        self.min_valid_throughput_Bps = _positive_float(
            _first_not_none(min_valid_throughput_Bps, min_valid_throughput),
            DEFAULT_MIN_VALID_THROUGHPUT_BPS,
        )
        self.min_segment_duration_s = _positive_float(min_segment_duration_s, DEFAULT_MIN_SEGMENT_DURATION_S)
        self.quality_reward_mode = _normalized_choice(
            quality_reward_mode,
            {DEFAULT_QUALITY_REWARD_MODE},
            DEFAULT_QUALITY_REWARD_MODE,
        )
        self.size_mode = _normalized_choice(
            size_mode,
            {DEFAULT_SIZE_MODE, "bitrate_times_duration"},
            DEFAULT_SIZE_MODE,
        )

        self._throughput_history_Bps = []
        self._last_sample_key = None
        self._last_rates_Bps = []
        self._last_level = None
        self.last_metrics = {}

    def calcControlAction(self):
        feedback = self.feedback or {}
        rates = _available_rates_Bps(feedback)
        self._last_rates_Bps = rates

        if not rates:
            self.last_metrics = {"reason": "invalid_ladder", "target_rate_Bps": 0.0}
            return _finish(self, 0.0)

        current_level = _current_level(feedback, rates, self._last_level)
        startup_level = _clamp_level(self.startup_level, rates)

        if len(rates) == 1:
            return self._finish_decision(
                rates=rates,
                chosen_level=0,
                current_level=current_level,
                reason="single_representation",
            )

        segment_duration_s = _finite_float(feedback.get("fragment_duration"))
        if segment_duration_s is None or segment_duration_s < self.min_segment_duration_s:
            return self._finish_decision(
                rates=rates,
                chosen_level=startup_level,
                current_level=current_level,
                segment_duration_s=segment_duration_s,
                reason="invalid_segment_duration_fallback",
            )

        self._update_throughput_history(feedback)
        prediction_history = self._prediction_history_Bps(feedback)
        predicted_throughput_Bps = _harmonic_mean_Bps(prediction_history)
        if predicted_throughput_Bps is None or predicted_throughput_Bps < self.min_valid_throughput_Bps:
            return self._finish_decision(
                rates=rates,
                chosen_level=startup_level,
                current_level=current_level,
                segment_duration_s=segment_duration_s,
                throughput_history_Bps=prediction_history,
                predicted_throughput_Bps=predicted_throughput_Bps,
                reason="startup_fallback_no_valid_throughput",
            )

        buffer_s = _finite_float(feedback.get("queued_time"))
        if buffer_s is None or buffer_s < 0.0:
            buffer_s = 0.0

        candidate_sizes_B = _candidate_segment_sizes_B(feedback, rates, segment_duration_s, self.size_mode)
        qualities = _qualities_log_rate_ratio(rates)
        effective_horizon = self._effective_horizon(len(rates), feedback)

        best_score = -math.inf
        best_sequence = None
        best_metrics = None
        sequence_count = 0
        for sequence in itertools.product(range(len(rates)), repeat=effective_horizon):
            sequence_count += 1
            score, metrics = _simulate_sequence(
                sequence=sequence,
                qualities=qualities,
                current_level=current_level,
                initial_buffer_s=buffer_s,
                segment_duration_s=segment_duration_s,
                predicted_throughput_Bps=predicted_throughput_Bps,
                candidate_sizes_B=candidate_sizes_B,
                rebuffer_penalty=self.rebuffer_penalty,
                switch_penalty=self.switch_penalty,
            )
            if score > best_score:
                best_score = score
                best_sequence = sequence
                best_metrics = metrics

        if not best_sequence:
            return self._finish_decision(
                rates=rates,
                chosen_level=startup_level,
                current_level=current_level,
                segment_duration_s=segment_duration_s,
                throughput_history_Bps=prediction_history,
                predicted_throughput_Bps=predicted_throughput_Bps,
                reason="no_sequence_fallback",
            )

        return self._finish_decision(
            rates=rates,
            chosen_level=best_sequence[0],
            current_level=current_level,
            segment_duration_s=segment_duration_s,
            buffer_s=buffer_s,
            throughput_history_Bps=prediction_history,
            predicted_throughput_Bps=predicted_throughput_Bps,
            effective_horizon=effective_horizon,
            sequence_count=sequence_count,
            qualities_by_level=qualities,
            segment_sizes_B=candidate_sizes_B,
            best_sequence=list(best_sequence),
            best_score=best_score,
            best_metrics=best_metrics,
            reason="mpc_sequence_selection",
        )

    def quantizeRate(self, rate):
        if self._last_rates_Bps:
            try:
                return quantize_rate_to_level(rate, self._last_rates_Bps)
            except ValueError:
                return 0
        return super().quantizeRate(rate)

    def _update_throughput_history(self, feedback):
        sample = _measured_throughput_sample_Bps(feedback)
        if sample is None or sample < self.min_valid_throughput_Bps:
            return

        sample_key = (
            _to_int(feedback.get("segment_index"), -1),
            sample,
            _finite_float(feedback.get("last_fragment_size")),
            _finite_float(feedback.get("last_download_time")),
        )
        if sample_key == self._last_sample_key:
            return

        self._throughput_history_Bps.append(sample)
        if len(self._throughput_history_Bps) > self.throughput_history_window:
            self._throughput_history_Bps = self._throughput_history_Bps[-self.throughput_history_window :]
        self._last_sample_key = sample_key

    def _prediction_history_Bps(self, feedback):
        configured_history = _configured_throughput_history_Bps(feedback)
        combined = configured_history + list(self._throughput_history_Bps)
        positive = [value for value in combined if value >= self.min_valid_throughput_Bps]
        return positive[-self.throughput_history_window :]

    def _effective_horizon(self, level_count, feedback):
        horizon = max(1, int(self.horizon))
        remaining = _remaining_segments(feedback)
        if remaining is not None:
            horizon = min(horizon, remaining)

        while horizon > 1 and (level_count ** horizon) > self.max_enumerated_sequences:
            horizon -= 1
        return max(1, horizon)

    def _finish_decision(
        self,
        rates,
        chosen_level,
        current_level,
        reason,
        segment_duration_s=None,
        buffer_s=None,
        throughput_history_Bps=None,
        predicted_throughput_Bps=None,
        effective_horizon=None,
        sequence_count=None,
        qualities_by_level=None,
        segment_sizes_B=None,
        best_sequence=None,
        best_score=None,
        best_metrics=None,
    ):
        chosen_level = _clamp_level(chosen_level, rates)
        chosen_rate = float(rates[chosen_level])
        self._last_level = chosen_level
        self.last_metrics = {
            "reason": reason,
            "current_level": current_level,
            "chosen_level": chosen_level,
            "target_rate_Bps": chosen_rate,
            "segment_duration_s": segment_duration_s,
            "buffer_s": buffer_s,
            "throughput_history_Bps": throughput_history_Bps,
            "predicted_throughput_Bps": predicted_throughput_Bps,
            "configured_horizon": self.horizon,
            "effective_horizon": effective_horizon,
            "sequence_count": sequence_count,
            "quality_reward_mode": self.quality_reward_mode,
            "qualities_by_level": qualities_by_level,
            "segment_sizes_B": segment_sizes_B,
            "best_sequence": best_sequence,
            "best_score": best_score,
            "best_metrics": best_metrics,
            "rebuffer_penalty": self.rebuffer_penalty,
            "switch_penalty": self.switch_penalty,
            "max_enumerated_sequences": self.max_enumerated_sequences,
            "internal_objective_only": True,
        }
        return _finish(self, chosen_rate)


def _simulate_sequence(
    sequence,
    qualities,
    current_level,
    initial_buffer_s,
    segment_duration_s,
    predicted_throughput_Bps,
    candidate_sizes_B,
    rebuffer_penalty,
    switch_penalty,
):
    simulated_buffer_s = float(initial_buffer_s)
    previous_level = current_level
    score = 0.0
    total_quality = 0.0
    total_rebuffer_s = 0.0
    total_switch_cost = 0.0
    download_times_s = []
    rebuffer_by_step_s = []
    buffer_by_step_s = []

    for level in sequence:
        size_B = candidate_sizes_B[level]
        download_time_s = size_B / predicted_throughput_Bps
        if not math.isfinite(download_time_s) or download_time_s < 0.0:
            download_time_s = math.inf

        rebuffer_s = max(download_time_s - simulated_buffer_s, 0.0)
        simulated_buffer_s = max(simulated_buffer_s - download_time_s, 0.0) + segment_duration_s

        quality = qualities[level]
        switch_cost = abs(quality - qualities[previous_level])

        total_quality += quality
        total_rebuffer_s += rebuffer_s
        total_switch_cost += switch_cost
        score += quality
        score -= rebuffer_penalty * rebuffer_s
        score -= switch_penalty * switch_cost

        download_times_s.append(download_time_s)
        rebuffer_by_step_s.append(rebuffer_s)
        buffer_by_step_s.append(simulated_buffer_s)
        previous_level = level

    return score, {
        "total_quality": total_quality,
        "total_rebuffer_s": total_rebuffer_s,
        "total_switch_cost": total_switch_cost,
        "download_times_s": download_times_s,
        "rebuffer_by_step_s": rebuffer_by_step_s,
        "buffer_by_step_s": buffer_by_step_s,
    }


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


def _configured_throughput_history_Bps(feedback):
    for key, unit in (
        ("throughput_history_Bps", "bytes_per_second"),
        ("throughput_history", "bytes_per_second"),
        ("mpc_throughput_history_Bps", "bytes_per_second"),
        ("throughput_history_bps", "bits_per_second"),
        ("throughput_history_kbps", "kilobits_per_second"),
        ("throughput_history_mbps", "megabits_per_second"),
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
            return normalized
    return []


def _measured_throughput_sample_Bps(feedback):
    last_size = _finite_float(feedback.get("last_fragment_size"))
    last_time = _finite_float(feedback.get("last_download_time"))
    if last_size is not None and last_size > 0.0 and last_time is not None and last_time > 0.0:
        return last_size / last_time

    for key, unit in (
        ("measured_throughput_Bps", "bytes_per_second"),
        ("measured_throughput", "bytes_per_second"),
        ("throughput_Bps", "bytes_per_second"),
        ("throughput", "bytes_per_second"),
        ("measured_throughput_bps", "bits_per_second"),
        ("throughput_bps", "bits_per_second"),
        ("measured_throughput_kbps", "kilobits_per_second"),
        ("throughput_kbps", "kilobits_per_second"),
        ("measured_throughput_mbps", "megabits_per_second"),
        ("throughput_mbps", "megabits_per_second"),
    ):
        if key in feedback:
            throughput = _rate_to_bytes_per_second(feedback.get(key), unit)
            if throughput is not None and throughput > 0.0:
                return throughput
    return None


def _harmonic_mean_Bps(values):
    positive = []
    for value in values:
        parsed = _finite_float(value)
        if parsed is not None and parsed > 0.0:
            positive.append(parsed)
    if not positive:
        return None
    denominator = sum(1.0 / value for value in positive)
    if denominator <= 0.0:
        return None
    return len(positive) / denominator


def _qualities_log_rate_ratio(rates):
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


def _remaining_segments(feedback):
    for key in ("remaining_segments", "segments_remaining", "remaining_chunks", "chunks_remaining"):
        if key not in feedback:
            continue
        value = _to_int(feedback.get(key), 0)
        if value > 0:
            return value
    return None


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


def _positive_int(value, default):
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return int(default)
    if parsed <= 0:
        return int(default)
    return parsed


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
    raw_text = str(unit or default).strip()
    compact = raw_text.replace("-", "_").replace(" ", "_")
    if compact in {"Bps", "B/s", "B_per_s", "Bytes/s", "Bytes_per_second"}:
        return "bytes_per_second"
    if compact in {"B", "Byte", "Bytes"}:
        return "bytes"

    text = raw_text.lower()
    return text.replace("-", "_").replace(" ", "_")
