# Chapter 05 Baseline Implementation Notes

These notes are source material for the future memory. They are not final LaTeX chapter text.

## Implementation Narrative

The baseline controllers were implemented incrementally in Python after the Phase 1 client contract was stable. The client already separated MPD parsing, downloading, media-engine behavior, controller decisions, logging and output artifacts. Phase 2.3 therefore focused on controller modules and tests, not on changing the player or metric pipeline.

Sanity controllers came first because they prove the narrowest possible controller path:

- a config name resolves through the registry;
- the controller receives feedback;
- the controller returns a target rate in bytes per second;
- the player quantizes the target rate to a representation index;
- fake-engine runs can produce canonical artifacts without benchmark claims.

Only after that path was stable were academic baselines added.

## Registry Explanation

`core/controller/registry.py` maps config names to `ControllerSpec` entries. `create_controller(name, params)` instantiates the matching factory. The registry is important because manifests and configs record controller identity by name; no controller should be selected by importing classes manually in runtime code.

The canonical Phase 2.3 names are:

- `min_rate`
- `fixed_rate`
- `max_rate`
- `rate_based`
- `bba`
- `bola`
- `mpc`
- `robust_mpc`

Legacy/debug names `fixed_quality`, `scripted_quality` and `max_quality` remain available for tests and stress/debug flows.

## Scientific Idea To Code

| controller | scientific/code idea | implementation file |
| --- | --- | --- |
| `min_rate` | always select the lowest available representation for path sanity | `core/controller/sanity_rate.py` |
| `fixed_rate` | select a configured level or target rate, clamped to the ladder | `core/controller/sanity_rate.py` |
| `max_rate` | always select the highest allowed representation for path sanity | `core/controller/sanity_rate.py` |
| `rate_based` | estimate application-layer throughput, smooth it, apply a safety factor and select the highest safe representation | `core/controller/rate_based.py` |
| `bba` | map buffer seconds through reservoir/cushion thresholds | `core/controller/bba.py` |
| `bola` | score each representation with a BOLA-basic utility/buffer/size objective | `core/controller/bola.py` |
| `mpc` | enumerate short-horizon quality sequences, predict throughput with a harmonic mean, simulate buffer/rebuffer and return the first action of the best sequence | `core/controller/mpc.py` |
| `robust_mpc` | reuse the MPC planner but reduce predicted throughput using recent prediction error | `core/controller/robust_mpc.py` |

## What Tests Prove

Controller unit tests prove deterministic fixture behavior, edge-case fallback, unit handling, registry compatibility and forbidden-signal boundaries. They are deliberately small and do not require videos, PDFs, network, GStreamer or replay traces.

They do not prove final QoE, real-network performance, paper-level reproduction or controller superiority.

## Unit Handling

- Controller target rates are bytes per second.
- Quality levels are representation indices.
- The ladder comes from MPD/client state through `rates`.
- Buffer is seconds through `queued_time`.
- Segment duration is seconds through `fragment_duration`.
- Segment sizes are bytes where exact sizes are available; otherwise BOLA/MPC-style controllers can approximate `rate * fragment_duration`.

## Defense Explanation Style

In the memory, explain each controller by its signal, decision rule, scope boundary and tests. Do not list all code. A good explanation is:

1. name the scientific family;
2. name the local simplification;
3. show which feedback fields are used;
4. explain how the decision becomes `target_rate`;
5. explain how `target_rate` becomes a representation index;
6. point to the unit tests and limitations.
