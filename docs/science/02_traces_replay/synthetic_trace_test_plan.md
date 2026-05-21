# Synthetic Trace Test Plan

Synthetic traces are the first validation layer for any future replay runner. They avoid dataset licensing, storage and leakage risks during runner development.

## Goals

- Validate trace parsing and unit conversion.
- Validate deterministic timing behavior.
- Validate controller-neutral execution.
- Validate artifact manifests.
- Exercise edge cases before real datasets are used.

## Candidate Synthetic Traces

| id | shape | purpose |
| --- | --- | --- |
| SYN-CONSTANT-LOW | constant throughput below mid ladder | Check constrained selection and buffer pressure. |
| SYN-CONSTANT-HIGH | constant throughput above top ladder | Check stable high-capacity behavior. |
| SYN-STEP-DOWN | high throughput followed by low throughput | Check response to capacity collapse. |
| SYN-STEP-UP | low throughput followed by high throughput | Check recovery behavior. |
| SYN-SAWTOOTH | repeated rise and fall | Check oscillation sensitivity. |
| SYN-BLIP-OUTAGE | short near-zero intervals | Check severe dips without real trace data. |
| SYN-JITTER | random but seeded variation around a mean | Check deterministic seeded variability. |
| SYN-INVALID | missing, negative or non-monotonic values | Check validation rejects bad input. |

## Test Rules

- Use `unittest`, not `pytest`, if future tests are added.
- Keep synthetic traces small and hand-authored if they are committed.
- Do not commit generated trace outputs.
- Do not use synthetic results for performance ranking.
- Do not convert synthetic test objectives into final QoE/reward.

## Success Criteria For Future Runner Work

A future runner is ready for real trace conversion only after synthetic tests prove:

1. invalid traces fail clearly;
2. valid traces produce deterministic artifacts;
3. all controllers can run through the same mechanism;
4. output locations obey repository hygiene rules;
5. no runtime controller/player/media/metric code was altered for a specific dataset.

## Phase 3.2A Source-Triage Update

Minimum synthetic traces for the first runner design:

| id | purpose |
| --- | --- |
| `constant_high` | stable bandwidth above all representations; validates no artificial stalls |
| `constant_low` | stable bandwidth below high representations; validates conservative behavior |
| `step_down` | bandwidth collapse; validates buffer/rebuffer handling |
| `step_up` | recovery; validates adaptation behavior |
| `oscillating` | repeated variation; validates deterministic playback simulation |
| `zero_gap` | temporary zero throughput; validates stall accounting |

Synthetic traces are test fixtures only. They are not benchmark evidence.

## Phase 3.2B Schema Update

Future synthetic fixtures must use `normalized_trace_schema_v1`:

- `timestamp_s`
- `duration_s`
- `throughput_kbps`

Minimum invalid cases:

- missing required column;
- nonnumeric timestamp;
- decreasing timestamp;
- zero or negative duration;
- negative throughput;
- missing throughput without an explicit converter policy.

Future tests must use `unittest`. Phase 3.2B does not add fixtures or tests.
