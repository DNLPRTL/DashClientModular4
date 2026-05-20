from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping, Optional

from .bola import BolaController
from .bba import BbaController
from .fixed_quality import FixedQualityController
from .max_quality_controller import MaxQualityController
from .mpc import MpcController
from .rate_based import RateBasedController
from .sanity_rate import FixedRateController, MaxRateController, MinRateController
from .scripted_quality import ScriptedQualityController


@dataclass(frozen=True)
class ControllerSpec:
    key: str
    label: str
    factory: Callable[..., object]


CONTROLLER_REGISTRY = {
    "min_rate": ControllerSpec(
        key="min_rate",
        label="Min rate (sanity/control)",
        factory=MinRateController,
    ),
    "fixed_rate": ControllerSpec(
        key="fixed_rate",
        label="Fixed rate or level (sanity/control)",
        factory=FixedRateController,
    ),
    "max_rate": ControllerSpec(
        key="max_rate",
        label="Max rate (sanity/control)",
        factory=MaxRateController,
    ),
    "rate_based": ControllerSpec(
        key="rate_based",
        label="Rate-based throughput baseline",
        factory=RateBasedController,
    ),
    "bba": ControllerSpec(
        key="bba",
        label="BBA buffer-based baseline",
        factory=BbaController,
    ),
    "bola": ControllerSpec(
        key="bola",
        label="BOLA-basic utility/buffer baseline",
        factory=BolaController,
    ),
    "mpc": ControllerSpec(
        key="mpc",
        label="MPC hybrid planning baseline",
        factory=MpcController,
    ),
    "fixed_quality": ControllerSpec(
        key="fixed_quality",
        label="Fixed quality (test/debug)",
        factory=FixedQualityController,
    ),
    "scripted_quality": ControllerSpec(
        key="scripted_quality",
        label="Scripted quality (test/debug)",
        factory=ScriptedQualityController,
    ),
    "max_quality": ControllerSpec(
        key="max_quality",
        label="Max quality (legacy/debug/stress)",
        factory=MaxQualityController,
    ),
}


def available_controllers():
    return list(CONTROLLER_REGISTRY.values())


def create_controller(key, params: Optional[Mapping[str, object]] = None):
    try:
        return CONTROLLER_REGISTRY[key].factory(**dict(params or {}))
    except KeyError as exc:
        available = ", ".join(sorted(CONTROLLER_REGISTRY))
        raise ValueError(f"Unknown controller '{key}'. Available: {available}") from exc
