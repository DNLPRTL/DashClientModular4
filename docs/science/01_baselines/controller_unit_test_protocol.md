# Controller Unit Test Protocol

Future controller tests must use Python `unittest`. This document defines the minimum categories and controller-specific cases before code tests are added.

## Test Categories

| category | purpose |
| --- | --- |
| Contract tests | Verify target rates are bytes per second and selected levels stay inside the ladder. |
| Ladder tests | Empty, one-level, unsorted or invalid rates, and boundary quantization. |
| Unit conversion tests | Check bytes, seconds, bytes/second, ratios and representation indices. |
| Missing input tests | Missing buffer, missing throughput, invalid duration, invalid current level. |
| Edge case tests | Threshold equality, zero/negative values, large values, all-negative scores. |
| Deterministic decision tests | Identical feedback and state produce identical output. |
| Paper-specific invariant tests | Verify algorithm-family behavior from the source evidence. |
| Forbidden signal tests | Ensure no RTT/loss/console/GStreamer-specific benchmark dependency is required. |
| Regression tests | Lock future fixes against reintroducing invalid behavior. |

## Minimum Tests By Controller

| controller | minimum future unit tests |
| --- | --- |
| rate_based | measured throughput maps to highest safe bitrate; low buffer guard lowers selection; no throughput uses min/startup fallback; aggressive downshift after capacity drop; conservative upshift limits one-level increase. |
| bba | buffer below reservoir selects min; buffer above reservoir plus cushion selects max; mid buffer maps to deterministic index; invalid buffer selects min; cushion <= 0 is invalid config. |
| bola | low buffer selects low bitrate; higher buffer can select higher bitrate under fixture parameters; throughput is not required; segment-size approximation uses `rate * segment_duration`; invalid parameters or invalid duration fail safely. |
| mpc | high throughput and high buffer choose higher quality; low throughput or low buffer choose lower quality; rebuffer penalty affects decision; first action of best sequence is returned; missing history uses safe fallback. |
| robust_mpc | zero prediction error behaves like MPC; high recent error is more conservative than MPC; insufficient history uses fallback; prediction error is computed safely; no RL/Pensieve dependency. |

## Concrete Unit Fixtures

| fixture | values | reason |
| --- | --- | --- |
| small ladder | `[100, 200, 400]` bytes/s | Easy exact expected levels. |
| one-level ladder | `[250]` bytes/s | Contract edge case. |
| standard segment | `fragment_duration = 4.0` seconds | Size and buffer formulas are simple. |
| buffer thresholds | reservoir `5.0`, cushion `10.0` | BBA exact boundaries. |
| throughput history | `[100, 200, 400]` bytes/s | Harmonic mean can be checked. |
| robust errors | predicted/actual pairs with max error `0`, `0.5`, `1.0` | RobustMPC correction behavior. |

## Common Assertions

- Return value is numeric and positive.
- Return value is one of the ladder rates or safely quantizes to a ladder level.
- No controller reads console output, logs, local files, datasets or PDFs.
- No controller writes canonical artifacts directly.
- No final QoE/reward is asserted in unit tests.

## Test Naming Guidance

Future test modules should be explicit and boring:

- `tests/test_rate_based_controller.py`
- `tests/test_bba_controller.py`
- `tests/test_bola_controller.py`
- `tests/test_mpc_controller.py`
- `tests/test_robust_mpc_controller.py`

Use small fixtures over real media. Do not require network, GStreamer, external traces, PDFs, or datasets.
