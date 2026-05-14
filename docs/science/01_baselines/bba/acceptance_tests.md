# bba Acceptance Tests

These tests define future behavior for the BBA-0-style controller. They do not add code tests in this block.

## Unit Tests

Assume default `reservoir_s = 5.0`, `cushion_s = 10.0`, and rates `[100, 200, 400, 800]` in bytes per second unless stated otherwise.

| test | input | expected result | tolerance |
| --- | --- | --- | --- |
| below reservoir | buffer `4.99` | target `100`, level `0` | exact |
| at reservoir | buffer `5.0` | target `100`, level `0` | exact |
| halfway cushion | buffer `10.0` | normalized `0.5`, floor level `1`, target `200` | exact |
| near top cushion | buffer `14.9` | level `2`, target `400` | exact |
| at high threshold | buffer `15.0` | target `800`, level `3` | exact |
| above high threshold | buffer `30.0` | target `800`, level `3` | exact |
| missing buffer | buffer `None` or non-finite | target `100`, level `0` | exact |
| negative buffer | buffer `-1.0` | target `100`, level `0` | exact |
| one-level ladder | rates `[300]`, any valid buffer | target `300`, level `0` | exact |
| invalid cushion | `cushion_s <= 0` | configuration validation failure | exact |

## Fake Smoke Tests

| scenario | setup | expected result | what it proves |
| --- | --- | --- | --- |
| low-buffer run | fake feedback keeps buffer below reservoir | controller stays at min | safe low-buffer behavior |
| growing buffer | fake feedback increases buffer across cushion | selected level rises monotonically or holds | deterministic buffer map |
| high buffer | fake feedback stays above high threshold | controller selects max | high-buffer mapping |
| no throughput data | valid buffer with missing size/time | decision still succeeds | throughput not required |

Smoke outputs are not benchmark results.

## Minimum Scenarios

- Empty ladder validation failure.
- Single-level ladder.
- Missing, negative, and non-finite buffer values.
- Exact threshold equality for reservoir and reservoir plus cushion.

## Invariants

- Buffer occupancy is the primary decision signal.
- No throughput-based primary rule in BBA-0.
- No selected level outside the ladder.
- Target rate unit is bytes per second.
- Identical feedback and parameters produce identical output.

## Invalidating Failures

- Selecting a high rate when buffer is below or equal to reservoir.
- Using throughput to override normal BBA-0 behavior.
- Treating `queued_bytes` as benchmark-equivalent buffer.
- Modifying runtime/player/metric/config files.
- Claiming fake smoke output as benchmark evidence.

## Platform Validation

| platform | command | expected |
| --- | --- | --- |
| Windows | `python -m unittest discover` | pass |
| Windows | `python scripts/check_client_readiness.py --strict` | pass |
| Ubuntu | same commands when available | pass |

## Benchmark Claim Boundary

These tests validate deterministic BBA behavior only. They do not define final QoE, trace replay, production Netflix equivalence, or benchmark results.
