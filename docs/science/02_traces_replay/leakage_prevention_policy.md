# Leakage Prevention Policy

Leakage occurs when information from validation, test or OOD data influences implementation, parameter selection or interpretation before the final evaluation. This policy applies to future Phase 3 and later work.

## Leakage Types

| leakage type | example | prevention |
| --- | --- | --- |
| Trace reuse leakage | Same route/session appears in train and test. | Split by trace/session/source identity. |
| Parameter leakage | Controller thresholds adjusted after inspecting test results. | Freeze parameters before test execution. |
| Scenario leakage | Test scenarios are repeatedly used as development fixtures. | Use synthetic development traces and reserve real test traces. |
| OOD leakage | OOD traces guide parameter changes. | Run OOD after choices are frozen. |
| Metadata leakage | Context fields unavailable to controllers influence adaptation logic. | Keep context fields out of controller inputs unless later explicitly approved. |
| Artifact leakage | Generated CSV/logs from test runs are used as training data. | Separate artifact folders and label split provenance. |
| Manual inspection leakage | Human review of test traces changes selection policy. | Document all inspection before split freeze. |

## Controls

1. Create dataset cards before download or conversion.
2. Record split assignment before benchmark execution.
3. Use synthetic traces for runner development.
4. Freeze controller parameters before final test and OOD runs.
5. Keep raw traces and generated artifacts outside git.
6. Record checksums or stable external identifiers for selected traces.
7. Label every run artifact with dataset ID, trace ID, split, method and commit.
8. Do not redefine metrics after seeing comparative results.

## Phase 3.1 Boundary

Because Phase 3.1 downloads no datasets and runs no benchmark, there is no experimental leakage yet. The risk begins when later phases inspect, convert, tune or execute trace-driven runs.

## Phase 3.2A Source-Triage Update

### New Leakage Risks Recognized

- Sliding-window leakage: windows from the same original trace must not cross train/validation/test/OOD boundaries.
- Route leakage: repeated commute routes must be grouped.
- Service/day leakage: Lancaster traces from a single service/day require careful grouping.
- Operator/device/app leakage: Raca 4G/5G must be grouped by available metadata.
- Trajectory leakage: Lumos5G repeated passes over same locations/trajectories must not be split naively.
- Causal trace leakage: Puffer/log-derived traces may reflect choices of deployed ABR algorithms and are not automatically exogenous capacity traces.

### Required Policy

Every dataset conversion plan must produce a manifest with:

- source dataset id;
- original file id;
- route/session/day/operator/app metadata when available;
- split assignment;
- reason for split assignment;
- conversion version;
- unit normalization.
