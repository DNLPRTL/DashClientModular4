# Hardening Step 7: Controller API / ABR Decision Contract

Date: 2026-05-08

This step documents and test-protects the current controller-facing contract before adding comparable ABR baselines.

## What Changed

- Added `core/controller/contract.py`.
- Added `tests/test_controller_contract.py`.
- Updated `BaseController.quantizeRate()` to use the shared contract quantizer while keeping the public legacy method name.
- Documented the required player feedback keys, units, target-rate unit, and quantization rule.

## Current Controller API

The controller API remains dict-based for backward compatibility:

- `setPlayerFeedback(feedback_dict)` receives the latest player feedback.
- `calcControlAction()` returns a target rate.
- `getControlAction()` returns the last target rate recorded by the controller.
- `quantizeRate(rate)` maps a target rate to a representation level.
- `getIdleDuration()` returns controller-requested idle time between downloads.

No dataclass replacement, controller API redesign, or runtime/player refactor is introduced in this block.

## Feedback And Decision Units

Feedback keys and units are now explicit in `core/controller/contract.py`.

- Buffer byte counters use `bytes`.
- Buffer and download durations use `seconds`.
- Bitrate ladder values use `bytes_per_second`, not bits per second.
- Target rates returned by controllers use `bytes_per_second`.
- Quality levels are integer indices into the MPD bitrate ladder.
- Segment indices use `segment_or_item_index`.
- Segment request timestamps use `perf_counter_seconds`.

Controllers receive the ladder in `feedback_dict["rates"]`. A controller returns a target rate from `calcControlAction()`, and the player-facing quantizer chooses the highest ladder index whose rate is less than or equal to that target. Targets below the minimum rate map to level `0`; targets above the maximum rate map to the last matching level.

## Controller Boundaries

Controllers may choose a target rate and idle duration through the existing API. They must not own parser behavior, downloader behavior, media-engine timing, buffer mutation, retry policy, stall accounting, CSV schema, QoE logic, or benchmark orchestration.

This contract is intentionally not overfit to `MaxQualityController`. It describes what any future ABR controller will receive and return.

## Boundaries Preserved

- No ABR baseline was implemented.
- No learned or AI controller was added.
- ABR decisions, buffering, retry behavior, warm-up, preroll, pacing, downshift behavior, stall handling, throughput estimation, CSV semantics, QoE logic, GStreamer timing, downloader behavior, and parser behavior were not changed.
- Windows tests still do not require GStreamer.
- Tests remain offline and `unittest`-based.

## Current Caveats

The controller contract is now test-protected, but runtime responsibility separation is still pending.

Benchmark neutrality is still pending.

Generated datasets are still validation artifacts, not final benchmark results.

The GStreamer runtime path is still operational validation only and is not benchmark-grade yet.

ABR baselines must not be implemented until the client hardening path is complete.
