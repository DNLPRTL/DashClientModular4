from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Mapping

from .max_quality_controller import MaxQualityController


@dataclass(frozen=True)
class ControllerSpec:
    key: str
    label: str
    factory: Callable[..., object]


CONTROLLER_REGISTRY = {
    "max_quality": ControllerSpec(
        key="max_quality",
        label="Fijo (maxima calidad)",
        factory=MaxQualityController,
    ),
}


def available_controllers():
    return list(CONTROLLER_REGISTRY.values())


def create_controller(key, params: Mapping[str, object] | None = None):
    try:
        return CONTROLLER_REGISTRY[key].factory(**dict(params or {}))
    except KeyError as exc:
        available = ", ".join(sorted(CONTROLLER_REGISTRY))
        raise ValueError(f"Unknown controller '{key}'. Available: {available}") from exc
