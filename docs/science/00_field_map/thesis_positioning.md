# Thesis Positioning

## Proposed Position

This TFG should be positioned as a reproducible engineering and experimental platform for studying classic ABR baselines in MPEG-DASH, not as a new ABR algorithm in the initial phase.

The contribution is the disciplined construction of a clean client, the scientific intake of ABR literature, and a staged path toward comparable baseline implementation.

## What the Work Can Claim

- A modular DASH client architecture prepared for ABR controllers.
- A documentation-first methodology for translating ABR papers into implementation specs.
- A selected initial baseline set covering sanity, throughput-based, buffer-based, and MPC-style controllers.
- A clear separation between integration/demo playback and controlled benchmarking.
- Traceability from sources to thesis sections, tables, figures, and future code.

## What the Work Must Not Claim Yet

- A final QoE model.
- Benchmark-grade GStreamer playback evaluation.
- A trained or implemented AI/RL controller.
- A complete survey of all modern ABR methods.
- Direct implementation fidelity to a paper before the paper is distilled into the required Markdown artifacts.

## Thesis Chapters Fed by This Scaffold

| chapter | input from docs/science |
| --- | --- |
| Chapter 1: introduction and motivation | DASH growth context, local YouTube traffic work, need for reproducible ABR experimentation. |
| Chapter 2: background/state of the art | DASH terminology, HAS taxonomy, baseline families, selected sources. |
| Chapter 5: implementation | Future baseline implementation specs and controller API mappings. |
| Chapter 6: evaluation | Acceptance matrices, signal matrix, and declared limitations. |
| Bibliography | Source inventories and provisional BibTeX keys. |
| Annexes | Source cards, implementation specs, acceptance tests, traceability tables. |
