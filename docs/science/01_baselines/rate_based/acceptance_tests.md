# rate_based Acceptance Tests

Status: implemented in `tests/test_rate_based_controller.py` during Phase 2.3.2.

These tests validate decision logic and client-contract compatibility. They are not benchmark results and do not define final QoE/reward.

## Unit Test Coverage

| category | implemented case | expected result |
| --- | --- | --- |
| registry | `rate_based` is registered | `create_controller("rate_based")` returns `RateBasedController` |
| registry regression | `min_rate`, `fixed_rate`, `max_rate`, `fixed_quality`, `scripted_quality`, `max_quality` remain available | existing names still instantiate |
| current API | `calcControlAction()` returns a numeric target rate | return value is a `float`; `getControlAction()` matches |
| target-rate unit | explicit `bps` throughput converts to bytes/s | target rate is bytes/s and quantizes to the expected index |
| representation index | target rate maps through `quantizeRate()` | `quality_level` is a representation index |
| console boundary | stdout is patched during decision | controller writes no console output |
| measured throughput | rates `[100, 200, 400, 800]`, `bwe=300`, safety `0.85` | target `200`, level `1` |
| below minimum | safe throughput below the minimum ladder rate | target minimum representation |
| above maximum | throughput above maximum from current level `1` | upshift limited to one level, target `400` |
| startup fallback | no valid throughput, no valid size/time | target startup/min representation |
| invalid download time | size present with zero or negative time | no crash; startup/min fallback |
| direct bytes/time | `last_fragment_size / last_download_time = 300 B/s` | safe `255 B/s`, target `200` |
| safety factor | same throughput with `0.5` vs `1.0` safety | lower safety factor selects lower target |
| low buffer guard | high throughput but `queued_time <= 2.0` | target lowered from current high level |
| explicit units | `rates_unit=bps` and `measured_throughput_bps` | converted to bytes/s before selection |
| invalid ladder | empty, missing, malformed or non-positive rates | return `0.0` safely |
| conservative upshift | high throughput from level `0` | at most one-level upshift |
| aggressive downshift | unsafe throughput from level `3` | multi-level drop to safe low level |
| EWMA/drop behavior | high estimate followed by unsafe instant measurement | instant unsafe drop remains aggressive |
| single representation | one-entry ladder | target only representation, index `0` |
| forbidden signals | RTT/loss/cwnd/server/oracle fields added | decision unchanged |
| forbidden field absence | no RTT/loss/server fields | decision still succeeds |

## Fake Smoke Coverage

Phase 2.3.2 requires at least one short fake-engine run with `controller.name: "rate_based"` through the current CLI/config path.

The smoke run must verify the canonical artifacts:

- `run_manifest.json`
- `config.resolved.json`
- `environment.json`
- `run.log`
- `segment_telemetry.csv`
- `evaluation_segments.csv`

The smoke run must also verify that these legacy outputs are not produced:

- `dataset.csv`
- `dataset_training.csv`

## Deferred Smoke Scenarios

A stable local fake smoke run is feasible with the current CLI/config path. A capacity-drop or low-capacity smoke scenario is deferred until replay/traces or a controlled downloader/network fixture exists. Creating a throttling system in this block would add benchmark infrastructure, which is explicitly out of scope.

## Invariants

- Deterministic output for identical feedback and controller state.
- No selected quality outside the ladder.
- All target rates are bytes/s.
- `quality_level` means representation index.
- Buffer is a guard only, not the primary decision rule.
- No TCP RTT, packet loss, congestion window, server state, external oracle, console output, final QoE/reward, replay trace, or GStreamer-only signal is used.

## Invalidating Failures

- Returning bits/s while the contract expects bytes/s.
- Selecting a representation index outside `[0, max_level]`.
- Upshifting more than `max_upshift_levels` when conservative upshift is enabled.
- Using forbidden network/server/oracle fields.
- Writing custom CSVs or mutating canonical artifact semantics.
- Treating fake smoke output as benchmark evidence.

## Platform Validation

Required commands for this implementation block:

```powershell
python -m unittest discover
python scripts/check_client_readiness.py --strict
python -m py_compile core/controller/contract.py
python -m py_compile core/controller/registry.py
python -m py_compile core/controller/sanity_rate.py
python -m py_compile core/controller/rate_based.py
```
