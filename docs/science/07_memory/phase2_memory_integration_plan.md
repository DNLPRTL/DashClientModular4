# Phase 2 Memory Integration Plan

This plan maps Phase 2 closure evidence into the final TFG memory. It is planning material, not final thesis prose.

## Chapter 1: Motivation

Use Phase 2 to explain why ABR baselines are necessary before IA/RL work:

- DASH streaming quality depends on client-side adaptation decisions;
- IA only has value if compared against transparent non-neural baselines;
- the client had to be hardened first so later comparisons do not mix algorithm behavior with infrastructure debt.

## Chapter 2: ABR Background And Selected Baselines

Use the literature cards, field map and baseline selection matrix to introduce:

- receiver-driven DASH ABR;
- throughput-based methods;
- buffer-based methods;
- utility/buffer methods;
- model predictive methods;
- robust prediction variants;
- IA/RL methods as later context.

State the selected Phase 2 baseline set:

- technical controls: `min_rate`, `fixed_rate`, `max_rate`;
- academic baselines: `rate_based`, `bba`, `bola`, `mpc`, `robust_mpc`;
- optional/deferred methods: SODA, RBC, Pensieve, DYNAMIC, FAST SWITCHING.

## Chapter 5: Python Implementation And Controller Architecture

Use Phase 2 closure docs to explain:

- the controller registry and canonical names;
- the current dict-based controller API;
- target rates in bytes per second;
- quality levels as representation indices;
- how source evidence becomes spec, mapping, tests and implementation;
- why controllers do not parse MPDs, download segments, write CSV files or define evaluation metrics;
- how sanity controllers validated plumbing before academic baselines;
- how each academic controller maps to a module and unit-test file.

## Chapter 6: Evaluation Boundary

Use the closure and limitation docs to state what has not yet been evaluated:

- no final QoE/reward;
- no replay/traces/emulation;
- no final benchmark;
- no real-network ranking;
- fake smoke is integration validation;
- GStreamer is integration/demo only.

This chapter should introduce the evidence ladder: unit tests, fake smoke, readiness checks, future replay/emulation, and only later final benchmark results.

## Bibliography Mapping

Use the bibliography plan and source inventories to connect:

- `liu2011rateAdaptation` to `rate_based`;
- `huang2014bba` to `bba`;
- `spiteri2020bola` and `spiteri2019dashjs` to BOLA and practical dash.js caveats;
- `yin2015mpc` to `mpc` and `robust_mpc`;
- `mao2017pensieve` to historical IA/RL context and RobustMPC comparison context;
- `chen2024soda` to optional modern future work.

## Annexes

Good annex candidates:

- controller specs;
- controller API mappings;
- acceptance tests;
- command validation summaries;
- registry inventory;
- reproducibility and artifact contracts;
- limitations and deferred-work tables.

Do not include raw PDFs, generated run directories, CSV logs, media segments or benchmark artifacts in the repository.
