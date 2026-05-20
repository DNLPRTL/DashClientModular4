from __future__ import annotations

import itertools
import math

from .mpc import (
    DEFAULT_HORIZON,
    DEFAULT_MAX_ENUMERATED_SEQUENCES,
    DEFAULT_MIN_SEGMENT_DURATION_S,
    DEFAULT_MIN_VALID_THROUGHPUT_BPS,
    DEFAULT_QUALITY_REWARD_MODE,
    DEFAULT_REBUFFER_PENALTY,
    DEFAULT_SIZE_MODE,
    DEFAULT_STARTUP_LEVEL,
    DEFAULT_SWITCH_PENALTY,
    DEFAULT_THROUGHPUT_HISTORY_WINDOW,
    MpcController,
    _available_rates_Bps,
    _candidate_segment_sizes_B,
    _clamp_level,
    _configured_throughput_history_Bps,
    _current_level,
    _finite_float,
    _harmonic_mean_Bps,
    _measured_throughput_sample_Bps,
    _non_negative_float,
    _positive_float,
    _positive_int,
    _qualities_log_rate_ratio,
    _rate_to_bytes_per_second,
    _simulate_sequence,
    _to_int,
)


DEFAULT_PREDICTION_ERROR_WINDOW = 5
DEFAULT_STARTUP_SAFETY_FACTOR = 0.85
DEFAULT_EPSILON_THROUGHPUT_BPS = 0.001


class RobustMpcController(MpcController):
    """RobustMPC ABR baseline: MPC with conservative prediction correction.

    Implements the local RobustMPC spec in
    docs/science/01_baselines/robust_mpc/implementation_spec.md.
    """

    name = "robust_mpc"

    def __init__(
        self,
        horizon=DEFAULT_HORIZON,
        throughput_history_window=DEFAULT_THROUGHPUT_HISTORY_WINDOW,
        prediction_error_window=DEFAULT_PREDICTION_ERROR_WINDOW,
        startup_safety_factor=DEFAULT_STARTUP_SAFETY_FACTOR,
        epsilon_throughput_Bps=None,
        epsilon_throughput=None,
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
        super().__init__(
            horizon=horizon,
            throughput_history_window=throughput_history_window,
            rebuffer_penalty=rebuffer_penalty,
            switch_penalty=switch_penalty,
            startup_level=startup_level,
            startup_quality=startup_quality,
            max_enumerated_sequences=max_enumerated_sequences,
            min_valid_throughput_Bps=min_valid_throughput_Bps,
            min_valid_throughput=min_valid_throughput,
            min_segment_duration_s=min_segment_duration_s,
            quality_reward_mode=quality_reward_mode,
            size_mode=size_mode,
        )
        self.prediction_error_window = _positive_int(
            prediction_error_window,
            DEFAULT_PREDICTION_ERROR_WINDOW,
        )
        self.startup_safety_factor = _unit_interval_float(
            startup_safety_factor,
            DEFAULT_STARTUP_SAFETY_FACTOR,
        )
        self.epsilon_throughput_Bps = _positive_float(
            _first_not_none(epsilon_throughput_Bps, epsilon_throughput),
            DEFAULT_EPSILON_THROUGHPUT_BPS,
        )

        self._prediction_error_history = []
        self._pending_prediction_Bps = None
        self._last_actual_sample_key = None

    def calcControlAction(self):
        feedback = self.feedback or {}
        rates = _available_rates_Bps(feedback)
        self._last_rates_Bps = rates

        if not rates:
            self.last_metrics = {"reason": "invalid_ladder", "target_rate_Bps": 0.0}
            return self._finish_with_no_pending(0.0)

        current_level = _current_level(feedback, rates, self._last_level)
        startup_level = _clamp_level(self.startup_level, rates)

        if len(rates) == 1:
            return self._finish_robust_decision(
                rates=rates,
                chosen_level=0,
                current_level=current_level,
                reason="single_representation",
            )

        segment_duration_s = _finite_float(feedback.get("fragment_duration"))
        if segment_duration_s is None or segment_duration_s < self.min_segment_duration_s:
            return self._finish_robust_decision(
                rates=rates,
                chosen_level=startup_level,
                current_level=current_level,
                segment_duration_s=segment_duration_s,
                reason="invalid_segment_duration_fallback",
            )

        self._update_actual_and_error_history(feedback)
        prediction_history = self._prediction_history_Bps(feedback)
        base_prediction_Bps = _harmonic_mean_Bps(prediction_history)
        if base_prediction_Bps is None or base_prediction_Bps < self.min_valid_throughput_Bps:
            return self._finish_robust_decision(
                rates=rates,
                chosen_level=startup_level,
                current_level=current_level,
                segment_duration_s=segment_duration_s,
                throughput_history_Bps=prediction_history,
                base_prediction_Bps=base_prediction_Bps,
                reason="startup_fallback_no_valid_throughput",
            )

        robust_prediction_Bps, error_history, error_max, correction_mode = self._robust_prediction_Bps(
            feedback,
            base_prediction_Bps,
        )
        if robust_prediction_Bps is None or robust_prediction_Bps <= 0.0:
            return self._finish_robust_decision(
                rates=rates,
                chosen_level=startup_level,
                current_level=current_level,
                segment_duration_s=segment_duration_s,
                throughput_history_Bps=prediction_history,
                base_prediction_Bps=base_prediction_Bps,
                prediction_error_history=error_history,
                prediction_error_max=error_max,
                correction_mode=correction_mode,
                reason="invalid_robust_prediction_fallback",
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
                predicted_throughput_Bps=robust_prediction_Bps,
                candidate_sizes_B=candidate_sizes_B,
                rebuffer_penalty=self.rebuffer_penalty,
                switch_penalty=self.switch_penalty,
            )
            if score > best_score:
                best_score = score
                best_sequence = sequence
                best_metrics = metrics

        if not best_sequence:
            return self._finish_robust_decision(
                rates=rates,
                chosen_level=startup_level,
                current_level=current_level,
                segment_duration_s=segment_duration_s,
                throughput_history_Bps=prediction_history,
                base_prediction_Bps=base_prediction_Bps,
                robust_prediction_Bps=robust_prediction_Bps,
                prediction_error_history=error_history,
                prediction_error_max=error_max,
                correction_mode=correction_mode,
                reason="no_sequence_fallback",
            )

        return self._finish_robust_decision(
            rates=rates,
            chosen_level=best_sequence[0],
            current_level=current_level,
            segment_duration_s=segment_duration_s,
            buffer_s=buffer_s,
            throughput_history_Bps=prediction_history,
            base_prediction_Bps=base_prediction_Bps,
            robust_prediction_Bps=robust_prediction_Bps,
            prediction_error_history=error_history,
            prediction_error_max=error_max,
            correction_mode=correction_mode,
            effective_horizon=effective_horizon,
            sequence_count=sequence_count,
            qualities_by_level=qualities,
            segment_sizes_B=candidate_sizes_B,
            best_sequence=list(best_sequence),
            best_score=best_score,
            best_metrics=best_metrics,
            reason="robust_mpc_sequence_selection",
        )

    def _update_actual_and_error_history(self, feedback):
        sample = _measured_throughput_sample_Bps(feedback)
        if sample is None or sample < self.min_valid_throughput_Bps:
            return

        sample_key = (
            _to_int(feedback.get("segment_index"), -1),
            sample,
            _finite_float(feedback.get("last_fragment_size")),
            _finite_float(feedback.get("last_download_time")),
        )
        if sample_key == self._last_actual_sample_key:
            return

        if self._pending_prediction_Bps is not None:
            error = _prediction_error_ratio(
                predicted_Bps=self._pending_prediction_Bps,
                actual_Bps=sample,
                epsilon_Bps=self.epsilon_throughput_Bps,
            )
            if error is not None:
                self._prediction_error_history.append(error)
                self._prediction_error_history = self._prediction_error_history[-self.prediction_error_window :]

        self._throughput_history_Bps.append(sample)
        self._throughput_history_Bps = self._throughput_history_Bps[-self.throughput_history_window :]
        self._last_actual_sample_key = sample_key

    def _robust_prediction_Bps(self, feedback, base_prediction_Bps):
        error_history = self._combined_prediction_error_history(feedback)
        if error_history:
            recent_errors = error_history[-self.prediction_error_window :]
            error_max = max(recent_errors)
            robust_prediction = base_prediction_Bps / (1.0 + error_max)
            correction_mode = "prediction_error_correction"
        else:
            error_max = None
            robust_prediction = base_prediction_Bps * self.startup_safety_factor
            correction_mode = "startup_safety_factor"

        robust_prediction = _finite_float(robust_prediction)
        if robust_prediction is None:
            return None, error_history, error_max, correction_mode
        robust_prediction = max(robust_prediction, self.epsilon_throughput_Bps)
        robust_prediction = min(robust_prediction, base_prediction_Bps)
        return robust_prediction, error_history, error_max, correction_mode

    def _combined_prediction_error_history(self, feedback):
        configured = _configured_prediction_error_history(feedback)
        paired = _prediction_errors_from_history_pairs(feedback, self.epsilon_throughput_Bps)
        combined = configured + paired + list(self._prediction_error_history)
        finite_errors = []
        for value in combined:
            parsed = _finite_float(value)
            if parsed is not None and parsed >= 0.0:
                finite_errors.append(parsed)
        return finite_errors[-self.prediction_error_window :]

    def _finish_robust_decision(
        self,
        rates,
        chosen_level,
        current_level,
        reason,
        segment_duration_s=None,
        buffer_s=None,
        throughput_history_Bps=None,
        base_prediction_Bps=None,
        robust_prediction_Bps=None,
        prediction_error_history=None,
        prediction_error_max=None,
        correction_mode=None,
        effective_horizon=None,
        sequence_count=None,
        qualities_by_level=None,
        segment_sizes_B=None,
        best_sequence=None,
        best_score=None,
        best_metrics=None,
    ):
        target = self._finish_decision(
            rates=rates,
            chosen_level=chosen_level,
            current_level=current_level,
            segment_duration_s=segment_duration_s,
            buffer_s=buffer_s,
            throughput_history_Bps=throughput_history_Bps,
            predicted_throughput_Bps=robust_prediction_Bps,
            effective_horizon=effective_horizon,
            sequence_count=sequence_count,
            qualities_by_level=qualities_by_level,
            segment_sizes_B=segment_sizes_B,
            best_sequence=best_sequence,
            best_score=best_score,
            best_metrics=best_metrics,
            reason=reason,
        )
        self.last_metrics.update(
            {
                "base_prediction_Bps": base_prediction_Bps,
                "robust_prediction_Bps": robust_prediction_Bps,
                "prediction_error_history": prediction_error_history,
                "prediction_error_max": prediction_error_max,
                "prediction_error_window": self.prediction_error_window,
                "startup_safety_factor": self.startup_safety_factor,
                "epsilon_throughput_Bps": self.epsilon_throughput_Bps,
                "robust_correction_mode": correction_mode,
                "pensieve_implemented": False,
                "rl_or_neural_state_used": False,
                "internal_objective_only": True,
            }
        )
        if robust_prediction_Bps is not None and reason == "robust_mpc_sequence_selection":
            self._pending_prediction_Bps = robust_prediction_Bps
        return target

    def _finish_with_no_pending(self, rate):
        self.setIdleDuration(0.0)
        self.setControlAction(float(rate))
        return float(rate)


def _configured_prediction_error_history(feedback):
    for key in (
        "prediction_error_history",
        "prediction_errors",
        "robust_prediction_error_history",
        "robust_mpc_prediction_error_history",
        "mpc_prediction_error_history",
    ):
        if key not in feedback:
            continue
        try:
            values = list(feedback.get(key) or [])
        except TypeError:
            continue
        errors = []
        for value in values:
            parsed = _finite_float(value)
            if parsed is not None and parsed >= 0.0:
                errors.append(parsed)
        if errors:
            return errors
    return []


def _prediction_errors_from_history_pairs(feedback, epsilon_Bps):
    predictions = _configured_rate_history_Bps(
        feedback,
        (
            "predicted_throughput_history_Bps",
            "predicted_throughput_history",
            "predicted_throughput_history_bps",
            "predicted_throughput_history_kbps",
            "predicted_throughput_history_mbps",
            "previous_predicted_throughput_history_Bps",
            "previous_predicted_throughput_history",
            "previous_predicted_throughput_history_bps",
            "robust_mpc_prediction_history_Bps",
            "robust_mpc_prediction_history",
            "robust_mpc_prediction_history_bps",
            "mpc_prediction_history_Bps",
            "mpc_prediction_history",
            "mpc_prediction_history_bps",
        ),
    )
    if not predictions:
        return []

    actual_keys = (
        "actual_throughput_history_Bps",
        "actual_throughput_history",
        "actual_throughput_history_bps",
        "actual_throughput_history_kbps",
        "actual_throughput_history_mbps",
        "robust_mpc_actual_throughput_history_Bps",
        "robust_mpc_actual_throughput_history",
        "robust_mpc_actual_throughput_history_bps",
    )
    actuals = _configured_rate_history_Bps(feedback, actual_keys)
    if not actuals and not any(key in feedback for key in actual_keys):
        actuals = _configured_rate_history_Bps(feedback, ("throughput_history_Bps",))
    if not actuals:
        return []

    count = min(len(predictions), len(actuals))
    errors = []
    for predicted, actual in zip(predictions[-count:], actuals[-count:]):
        error = _prediction_error_ratio(predicted, actual, epsilon_Bps)
        if error is not None:
            errors.append(error)
    return errors


def _configured_rate_history_Bps(feedback, keys):
    for key in keys:
        if key not in feedback:
            continue
        unit = "bytes_per_second"
        if key.endswith("_bps"):
            unit = "bits_per_second"
        elif key.endswith("_kbps"):
            unit = "kilobits_per_second"
        elif key.endswith("_mbps"):
            unit = "megabits_per_second"

        try:
            values = list(feedback.get(key) or [])
        except TypeError:
            continue
        rates = []
        for value in values:
            rate = _rate_to_bytes_per_second(value, unit)
            if rate is not None and rate > 0.0:
                rates.append(rate)
        if rates:
            return rates
    return []


def _prediction_error_ratio(predicted_Bps, actual_Bps, epsilon_Bps):
    predicted = _finite_float(predicted_Bps)
    actual = _finite_float(actual_Bps)
    epsilon = _finite_float(epsilon_Bps)
    if predicted is None or actual is None or epsilon is None or epsilon <= 0.0:
        return None
    denominator = max(actual, epsilon)
    error = abs(predicted - actual) / denominator
    if not math.isfinite(error):
        return None
    return error


def _unit_interval_float(value, default):
    parsed = _non_negative_float(value, default)
    if parsed <= 0.0 or parsed > 1.0:
        return float(default)
    return float(parsed)


def _first_not_none(*values):
    for value in values:
        if value is not None:
            return value
    return None
