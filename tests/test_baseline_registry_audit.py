from __future__ import annotations

import inspect
import unittest

from core.controller.bba import BbaController
from core.controller.bola import BolaController
from core.controller.contract import QUALITY_LEVEL_UNIT, TARGET_RATE_UNIT
from core.controller.fixed_quality import FixedQualityController
from core.controller.max_quality_controller import MaxQualityController
from core.controller.mpc import MpcController
from core.controller.rate_based import RateBasedController
from core.controller.registry import CONTROLLER_REGISTRY, available_controllers, create_controller
from core.controller.robust_mpc import RobustMpcController
from core.controller.sanity_rate import FixedRateController, MaxRateController, MinRateController
from core.controller.scripted_quality import ScriptedQualityController


CANONICAL_BASELINES = {
    "min_rate": MinRateController,
    "fixed_rate": FixedRateController,
    "max_rate": MaxRateController,
    "rate_based": RateBasedController,
    "bba": BbaController,
    "bola": BolaController,
    "mpc": MpcController,
    "robust_mpc": RobustMpcController,
}

LEGACY_DEBUG_CONTROLLERS = {
    "fixed_quality": FixedQualityController,
    "scripted_quality": ScriptedQualityController,
    "max_quality": MaxQualityController,
}


class BaselineRegistryAuditTest(unittest.TestCase):
    def test_all_phase_2_3_canonical_controllers_are_registered(self):
        available_keys = {spec.key for spec in available_controllers()}

        self.assertTrue(set(CANONICAL_BASELINES).issubset(CONTROLLER_REGISTRY))
        self.assertTrue(set(CANONICAL_BASELINES).issubset(available_keys))

        for name, expected_type in CANONICAL_BASELINES.items():
            with self.subTest(controller=name):
                spec = CONTROLLER_REGISTRY[name]
                self.assertEqual(name, spec.key)
                self.assertIsInstance(create_controller(name), expected_type)

    def test_legacy_and_debug_controller_names_remain_preserved(self):
        for name, expected_type in LEGACY_DEBUG_CONTROLLERS.items():
            with self.subTest(controller=name):
                spec = CONTROLLER_REGISTRY[name]
                self.assertEqual(name, spec.key)
                self.assertIsInstance(create_controller(name), expected_type)

    def test_registry_keys_and_specs_are_not_silently_renamed(self):
        for registry_key, spec in CONTROLLER_REGISTRY.items():
            with self.subTest(controller=registry_key):
                self.assertEqual(registry_key, spec.key)

    def test_registered_controllers_expose_current_controller_api(self):
        for name in CANONICAL_BASELINES:
            with self.subTest(controller=name):
                controller = create_controller(name)

                self.assertTrue(callable(controller.setPlayerFeedback))
                self.assertTrue(callable(controller.calcControlAction))
                self.assertTrue(callable(controller.getControlAction))
                self.assertTrue(callable(controller.quantizeRate))
                self.assertTrue(callable(controller.getIdleDuration))

    def test_registry_contract_does_not_require_final_qoe_or_reward_objects(self):
        self.assertEqual("bytes_per_second", TARGET_RATE_UNIT)
        self.assertEqual("representation_index", QUALITY_LEVEL_UNIT)

        forbidden_required_params = {"qoe", "final_qoe", "reward", "final_reward"}
        for name in CANONICAL_BASELINES:
            with self.subTest(controller=name):
                signature = inspect.signature(CONTROLLER_REGISTRY[name].factory)
                required_params = {
                    param.name
                    for param in signature.parameters.values()
                    if param.default is inspect.Parameter.empty
                    and param.kind
                    in (
                        inspect.Parameter.POSITIONAL_ONLY,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        inspect.Parameter.KEYWORD_ONLY,
                    )
                }

                self.assertFalse(required_params & forbidden_required_params)
                self.assertIsInstance(create_controller(name, {}), CANONICAL_BASELINES[name])


if __name__ == "__main__":
    unittest.main()
