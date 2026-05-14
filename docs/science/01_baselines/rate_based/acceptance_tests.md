# rate_based Acceptance Tests

These are documentation-level acceptance tests. They are precise enough to become future `unittest` cases and fake-engine smoke checks, but no code tests are added in this block.

## Unit Tests

| test | input | expected result | tolerance |
| --- | --- | --- | --- |
| startup fallback | rates `[100, 200, 400]`, no valid size/time | target `100`, level `0` | exact |
| highest safe rate | rates `[100, 200, 400]`, smoothed throughput `300`, safety `0.85` gives `255` | target `200`, level `1` | exact |
| below minimum | rates `[100, 200, 400]`, safe throughput `80` | target `100`, level `0` | exact |
| above maximum with conservative up | rates `[100, 200, 400]`, current level `1`, safe throughput `1000` | target `400`, level `2` | exact |
| conservative up from min | rates `[100, 200, 400, 800]`, current level `0`, safe throughput `800` | target `200`, level `1` | exact |
| aggressive down | rates `[100, 200, 400, 800]`, current level `3`, safe throughput `180` | target `100`, level `0` | exact |
| critical buffer guard | rates `[100, 200, 400]`, current level `2`, safe throughput `400`, buffer below threshold | target no higher than `200` | exact |
| invalid download time | positive size and `last_download_time <= 0` | startup fallback | exact |
| one-level ladder | rates `[250]` | target `250`, level `0` | exact |
| forbidden signals absent | feedback contains no RTT/loss keys | decision still succeeds | exact |

## Fake Smoke Tests

| scenario | setup | expected result | what it proves |
| --- | --- | --- | --- |
| stable high throughput | fake run with repeated fast downloads and adequate buffer | gradual upshift, at most one level per segment | deterministic conservative increase |
| sudden capacity drop | high level followed by slow download measurements | immediate downshift to safe lower level | aggressive decrease |
| startup no history | first media decision without valid previous measurement | startup/min representation | safe startup |
| low buffer despite high throughput | high throughput but `queued_time` below critical threshold | lower or minimum representation | buffer is safety guard |

Smoke outputs are not benchmark results.

## Minimum Scenarios

- Empty ladder must raise validation failure.
- Single-representation ladder must select level 0.
- Missing `last_fragment_size` or `last_download_time` must not crash.
- All target rates must be bytes per second.

## Invariants

- Deterministic output for identical feedback and controller state.
- No quality index outside the ladder.
- No TCP RTT or packet loss dependency.
- No console/log/progress dependency.
- No CSV or metric mutation by the controller.

## Invalidating Failures

- Returning bits per second while the contract expects bytes per second.
- Selecting a level outside `[0, max_level]`.
- Upshifting more than one level when `conservative_up=true`.
- Using GStreamer events as benchmark-grade rebuffering input.
- Claiming fake smoke output as benchmark evidence.

## Platform Validation

| platform | command | expected |
| --- | --- | --- |
| Windows | `python -m unittest discover` | pass |
| Windows | `python scripts/check_client_readiness.py --strict` | pass |
| Ubuntu | same commands when available | pass |

## Benchmark Claim Boundary

These acceptance tests validate controller behavior and integration readiness only. They do not define final QoE, benchmark reward, replay methodology, or comparative results.
