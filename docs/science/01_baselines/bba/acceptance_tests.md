# bba Acceptance Tests

Status: implemented in `tests/test_bba_controller.py` during Phase 2.3.3.

These tests validate the BBA-0 decision rule and client-contract compatibility. They are not benchmark results and do not define final QoE/reward.

## Unit Test Coverage

| category | implemented case | expected result |
| --- | --- | --- |
| registry | `bba` is registered | `create_controller("bba")` returns `BbaController` |
| registry regression | `min_rate`, `fixed_rate`, `max_rate`, `rate_based`, `fixed_quality`, `scripted_quality`, `max_quality` remain available | existing names still instantiate |
| current API | `calcControlAction()` returns a numeric target rate | return value is a `float`; `getControlAction()` matches |
| target-rate unit | ladder values are bytes/s | target rate is bytes/s and quantizes to the expected index |
| representation index | target rate maps through `quantizeRate()` | `quality_level` is a representation index |
| console boundary | stdout is patched during decision | controller writes no console output |
| below reservoir | default reservoir `5.0`, buffer `4.99` | target minimum representation |
| at reservoir | buffer `5.0` | target minimum representation |
| above high threshold | buffer `30.0` | target maximum representation |
| at high threshold | buffer `15.0` | target maximum representation |
| mid cushion | buffer `10.0` with rates `[100, 200, 400, 800]` | target `200`, level `1` |
| near top cushion | buffer `14.9` | target `400`, level `2` |
| monotonicity | increasing buffer sequence | selected level is non-decreasing |
| missing buffer | `queued_time` absent or `None` | safe minimum fallback |
| invalid buffer | negative, infinite or NaN buffer | safe minimum fallback |
| invalid parameters | `reservoir_s < 0`, `cushion_s <= 0` | defaults `5.0` and `10.0` are used |
| single representation | one-entry ladder | target only representation, index `0` |
| invalid ladder | empty, missing, malformed or non-positive rates | return `0.0` safely |
| max-level clamp | high buffer with `max_level=2` | target highest available level only |
| throughput independence | same buffer with very low and very high throughput fields | same decision |
| forbidden network fields | RTT/loss/cwnd/server/oracle fields added | decision unchanged |
| forbidden text fields | console/log/progress fields added | decision unchanged |

## Fake Smoke Coverage

Phase 2.3.3 requires at least one short fake-engine run with `controller.name: "bba"` through the current CLI/config path.

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

A standard local fake smoke run is feasible with the current CLI/config path. A richer low-buffer or cross-cushion scenario is deferred until replay/traces or a controlled fake scenario fixture exists. Adding special buffer scripting in this block would create new runtime/benchmark infrastructure, which is out of scope.

## Invariants

- Buffer occupancy is the primary decision signal.
- Throughput is not used as the primary BBA-0 rule.
- No selected level outside the ladder.
- Target rate unit is bytes per second.
- `quality_level` means representation index.
- Identical feedback and parameters produce identical output.
- No TCP RTT, packet loss, congestion window, server state, external oracle, console output, final QoE/reward, replay trace, or GStreamer-only signal is used.

## Invalidating Failures

- Selecting a high rate when buffer is below or equal to reservoir.
- Using throughput to override normal BBA-0 behavior.
- Returning bits/s while the contract expects bytes/s.
- Treating `queued_bytes` as benchmark-equivalent buffer.
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
python -m py_compile core/controller/bba.py
```
