# Phase 2 To Phase 3 Transition

## Next Phase

PHASE 3 - traces / replay / emulation.

Phase 2 closes the baseline implementation set. Phase 3 must now define how DashClientModular4 will produce reproducible network conditions before any final benchmark or QoE ranking is attempted.

## Phase 3 Goals

Phase 3 should:

- choose trace datasets and document provenance, licenses and relevance;
- decide whether replay, emulation or both are required;
- decide whether Mahimahi is appropriate or whether alternatives are needed;
- define reproducible network scenarios for stable, constrained, dropping, recovering and unstable conditions;
- connect traces to the DashClientModular4 fake/replay architecture;
- preserve controller contract neutrality across all scenarios;
- define train/test/OOD splits if future IA/RL work needs learning or tuning;
- avoid train/test leakage;
- decide how generated run artifacts will be stored, excluded from git and summarized;
- keep benchmark claims deferred until methodology, QoE/reward and result-interpretation policy are complete.

## Non-Implementation Boundary

Phase 2.4 does not:

- implement replay;
- add traces or datasets;
- select Mahimahi as final methodology;
- create emulation scripts;
- define final QoE/reward;
- run benchmark experiments;
- change controllers to fit traces;
- change player/runtime/media-engine behavior.

## Inputs From Phase 2

Phase 3 inherits:

- canonical controller names;
- controller contract units and boundaries;
- baseline implementation specs;
- unit-test and fake-smoke validation rules;
- artifact contracts;
- limitation and result-interpretation policies.

Those inputs let Phase 3 focus on methodology rather than controller construction.

## Phase 3 Closure Criteria Draft

Phase 3 should close only when:

- trace/replay/emulation scope is explicitly selected;
- datasets or synthetic scenarios are documented;
- scenario reproducibility is validated;
- leakage risks are documented;
- generated artifacts are excluded from git;
- controller comparison remains neutral;
- final benchmark claims are still deferred if final QoE/reward is not closed.
