from __future__ import annotations

from numbers import Real

from .base import BaseController


class MinRateController(BaseController):
    """Sanity controller that always targets the lowest available rate."""

    name = "min_rate"

    def __init__(self, **_unused):
        super().__init__()

    def calcControlAction(self):
        rates = _available_rates(self.feedback)
        if not rates:
            return _finish(self, 0.0)
        return _finish(self, rates[0])


class MaxRateController(BaseController):
    """Sanity controller that always targets the highest available rate."""

    name = "max_rate"

    def __init__(self, **_unused):
        super().__init__()

    def calcControlAction(self):
        rates = _available_rates(self.feedback)
        if not rates:
            return _finish(self, 0.0)
        return _finish(self, rates[-1])


class FixedRateController(BaseController):
    """Sanity controller that targets a configured level or rate."""

    name = "fixed_rate"

    def __init__(
        self,
        level=None,
        quality_level=None,
        fixed_level=None,
        target_rate=None,
        fixed_rate=None,
        rate=None,
        target_rate_unit="bytes_per_second",
        rate_unit=None,
    ):
        super().__init__()
        self.level = _first_not_none(level, quality_level, fixed_level)
        self.target_rate = _first_not_none(target_rate, fixed_rate, rate)
        self.target_rate_unit = rate_unit if rate_unit is not None else target_rate_unit

    def calcControlAction(self):
        rates = _available_rates(self.feedback)
        if not rates:
            return _finish(self, 0.0)

        if self.level is not None:
            level = _clamp_level(self.level, rates)
            return _finish(self, rates[level])

        target_rate = _target_rate_to_bytes_per_second(self.target_rate, self.target_rate_unit)
        if target_rate is None:
            return _finish(self, rates[0])

        level = _floor_rate_to_level(target_rate, rates)
        return _finish(self, rates[level])


def _available_rates(feedback):
    if not feedback:
        return []

    raw_rates = feedback.get("rates", []) or []
    try:
        rates = _normalize_rates(raw_rates)
    except ValueError:
        return []

    if not rates:
        return []

    max_level = _to_int(feedback.get("max_level"), len(rates) - 1)
    max_level = max(0, min(max_level, len(rates) - 1))
    return rates[: max_level + 1]


def _normalize_rates(raw_rates):
    rates = []
    for value in raw_rates:
        if isinstance(value, bool) or not isinstance(value, Real):
            raise ValueError("Rates must be numeric bytes-per-second values.")
        rate = float(value)
        if rate <= 0:
            raise ValueError("Rates must be positive bytes-per-second values.")
        rates.append(rate)
    return rates


def _floor_rate_to_level(target_rate, rates):
    if target_rate <= rates[0]:
        return 0

    level = 0
    for index, rate in enumerate(rates):
        if target_rate >= rate:
            level = index
    return level


def _clamp_level(value, rates):
    level = _to_int(value, 0)
    return max(0, min(level, len(rates) - 1))


def _target_rate_to_bytes_per_second(value, unit):
    if value is None:
        return None
    try:
        rate = float(value)
    except (TypeError, ValueError):
        return None
    if rate < 0:
        return 0.0

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


def _finish(controller, rate):
    controller.setIdleDuration(0.0)
    controller.setControlAction(float(rate))
    return float(rate)


def _first_not_none(*values):
    for value in values:
        if value is not None:
            return value
    return None


def _to_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
