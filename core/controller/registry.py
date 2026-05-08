from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping, Optional

from .fixed_quality import FixedQualityController
from .max_quality_controller import MaxQualityController
from .scripted_quality import ScriptedQualityController


@dataclass(frozen=True)
class ControllerSpec:
    key: str
    label: str
    factory: Callable[..., object]


CONTROLLER_REGISTRY = {
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
