# bba Notes For Memory

## Neutral Academic Summary

`bba` is the second academic ABR baseline implemented after `rate_based`. It represents the classical buffer-based family: the client maps playback buffer occupancy to a representation using a reservoir and cushion.

Primary citation: Huang et al. 2014, `huang2014bba`.

## Why BBA Follows rate_based

`rate_based` established the throughput-driven baseline. BBA is implemented next because it is the cleanest contrast: it does not predict capacity as the main rule, and instead treats buffer occupancy as the central control state.

This order makes the thesis narrative simple:

1. sanity controllers prove the contract and fake integration;
2. `rate_based` proves application-layer throughput ABR;
3. `bba` proves buffer-map ABR.

## How BBA Differs From Throughput-Based ABR

`rate_based` asks: "What representation fits under a safe throughput estimate?"

`bba` asks: "How full is the playback buffer?"

The Phase 2.3.3 BBA controller ignores throughput fields for the decision. Two feedback dictionaries with the same `queued_time` and different `bwe`/download measurements must produce the same target rate.

## Reservoir And Cushion

Defaults:

```text
reservoir_s = 5.0
cushion_s = 10.0
```

Decision regions:

| buffer region | expected decision |
| --- | --- |
| `buffer <= reservoir_s` | minimum representation |
| `reservoir_s < buffer < reservoir_s + cushion_s` | deterministic intermediate ladder mapping |
| `buffer >= reservoir_s + cushion_s` | maximum representation |

Intermediate mapping:

```text
x = (buffer_level_s - reservoir_s) / cushion_s
target_level = floor(x * (num_representations - 1))
```

The controller returns `rates[target_level]` in bytes per second.

## What BBA-0 Simplification Means

BBA-0 here means the simple reservoir/cushion rate map:

- no startup capacity estimator;
- no Netflix production internals;
- no VBR-specific tuning;
- no throughput primary rule;
- no final QoE/reward;
- no benchmark claim from smoke output.

Startup capacity estimation is documented as optional in the paper evidence but deferred because the first implementation should isolate the buffer-map behavior.

## Paper-To-Code Mapping

| paper concept | DashClientModular4 implementation |
| --- | --- |
| playback buffer occupancy | `queued_time` |
| reservoir | `reservoir_s` parameter |
| cushion | `cushion_s` parameter |
| discrete bitrate ladder | `rates` in bytes/s |
| selected representation | quantized target rate / representation index |
| invalid low buffer state | minimum representation fallback |
| capacity estimate | deferred, not used in BBA-0 |

## Fake Smoke Interpretation

Fake smoke validates that:

- `bba` can be selected by config;
- it receives controller feedback;
- it returns bytes/s target rates;
- the player quantizes those targets to representation indices;
- canonical artifacts are produced;
- deprecated `dataset.csv` and `dataset_training.csv` are not produced.

Fake smoke does not prove final performance, QoE improvement, real-network superiority, Netflix production equivalence, or paper-level benchmark behavior. Comparison against BOLA, MPC and RobustMPC is deferred.

## How Tests Prove Correctness

The unit tests prove the local BBA-0 decision rule:

- buffer below or equal to reservoir selects minimum;
- buffer above or equal to reservoir+cushion selects maximum;
- mid-cushion buffer maps deterministically to an intermediate level;
- increasing buffer gives non-decreasing quality;
- missing/negative/non-finite buffer falls back safely;
- invalid reservoir/cushion values use documented defaults;
- throughput and forbidden network/text fields do not affect decisions.

They do not prove final QoE or benchmark superiority.

## Suggested Chapter Usage

Chapter 2: introduce BBA as the classical buffer-based ABR contrast to throughput-based adaptation.

Chapter 5: explain the implemented reservoir/cushion map, parameter defaults, API mapping and tests.

Chapter 6 later: use it as a comparator only after benchmark methodology and final QoE/reward are defined.
