# Trace dataset card — Raca et al. 4G LTE channel/context dataset

## Identity

- Name: Beyond Throughput: a 4G LTE Dataset with Channel and Context Metrics.
- Primary paper: Darijo Raca, Jason J. Quinlan, Ahmed H. Zahran, Cormac J. Sreenan. MMSys 2018.
- Dataset/project: UCC/MISL 4G LTE dataset.
- Year: 2018.
- Type: real-world 4G LTE throughput + channel/context KPI dataset.
- Phase 3.2A status: mandatory dataset card.
- Phase 3.2A decision: modern-mobile/OOD candidate, not first integration.

## Domain

4G/LTE production networks from two major Irish mobile operators.

## Availability

Public dataset/source pages exist. Download must remain outside the repository.

## License

Unknown/TBD. Verify Zenodo/UCC license before use or redistribution.

## Size

Paper/source describe 135 traces.

## Format

G-NetTrack Pro data with cellular KPIs, context metrics, downlink/uplink throughput and cell-related information.

## Throughput unit

Mbit/s in paper figures/tables. Exact dataset columns and units must be verified.

## Time granularity

One sample per second.

## Duration

Average duration about 15 minutes per trace. Table in paper reports total duration by mobility category.

## Mobility/scenario

Static, pedestrian, bus, car and train. Source notes also mention tram; verify exact category naming before final table.

## ABR usage in literature

Designed to support HAS/adaptive video streaming research and evaluation beyond throughput-only traces.

## Train suitability

Possible later if used as modern-mobile training source; not final in Phase 3.2A.

## Validation suitability

Possible modern-mobile validation source.

## Test suitability

Possible modern-mobile test source.

## OOD suitability

Strong OOD candidate if training uses HSDPA/Ghent/Lancaster.

## Leakage risks

- Same operator/mobility route correlations.
- Repeated or grouped traces must not be split naively.
- KPI-rich traces should not be mixed with throughput-only traces without documenting ignored variables.

## Download requirements

- Download outside repo only.
- Store under `_datasets/phase3_traces_replay/04_4g_ireland_candidate`.
- Verify license, schema, units and column names.

## DashClientModular4 integration notes

The simple runner will likely use only timestamp + downlink throughput initially. Context/channel columns can be preserved in metadata for future IA/generalization work.

## Replay/emulation requirements

- Custom Python runner: possible after converter.
- Mahimahi: possible after conversion but not first target.
- tc/netem: not first target.

## Limitations

More complex than throughput-only traces. Sampling granularity and Android API constraints must be reported.

## Decision

`candidate-modern-mobile-or-OOD`

## Memory usage

- Chapter 6 OOD/generalization policy.
- Dataset selection matrix.
- Possible future IA features discussion.

## BibTeX provisional

```bibtex
@inproceedings{raca2018beyondThroughput4g,
  title = {Beyond Throughput: a 4G LTE Dataset with Channel and Context Metrics},
  author = {Raca, Darijo and Quinlan, Jason J. and Zahran, Ahmed H. and Sreenan, Cormac J.},
  booktitle = {Proceedings of the 9th ACM Multimedia Systems Conference},
  year = {2018}
}
```
