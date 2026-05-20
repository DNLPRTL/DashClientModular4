# Trace dataset card — Lancaster ABR-Throughput-Traces

## Identity

- Name: ABR-Throughput-Traces.
- Project/source: lancs-net/ABR-Throughput-Traces.
- Year: CDN logs from a single day in 2018 according to source note/repository.
- Type: live HTTP Adaptive Streaming throughput traces derived from CDN logs.
- Phase 3.2A status: mandatory dataset card.
- Phase 3.2A decision: first-benchmark-design candidate and possible first-real-integration candidate after HSDPA/Ghent.

## Domain

Live HTTP Adaptive Streaming service, BT Sport 1, derived from CDN logs.

## Availability

Public GitHub repository exists. Download must remain outside the repository.

## License

Unknown/TBD. Verify repository license before copying or redistribution.

## Size

7,000 traces according to repository/source note.

## Format

TBD from repository files. Likely throughput time series; exact units and timestamps must be verified.

## Throughput unit

Repository/source note reports mean throughput in kbps. Exact per-line unit TBD.

## Time granularity

TBD.

## Duration

4 minutes per trace.

## Mobility/scenario

Not mobile-route traces. Live HAS/CDN service traces.

## ABR usage in literature

Directly relevant to HAS/live throughput and larger trace-set evaluation.

## Train suitability

Possible later because it has many traces, but must avoid same-day/session leakage.

## Validation suitability

Strong candidate if split policy is controlled.

## Test suitability

Strong candidate for broader HAS/live evaluation after converter.

## OOD suitability

Potential OOD if training uses mobile traces; potential in-domain live/HAS if training uses HAS logs.

## Leakage risks

- All traces come from a single service/day according to source note.
- Same-day/service correlations can leak if randomly split.
- Session/user/CDN grouping must be checked before train/test use.

## Download requirements

- Download outside repo only.
- Store under `_datasets/phase3_traces_replay/07_lancaster_has_candidate`.
- Verify license, exact format and grouping metadata.

## DashClientModular4 integration notes

Potentially valuable because the traces are already throughput traces and numerous. Use after HSDPA/Ghent conversion path is stable.

## Replay/emulation requirements

- Custom Python runner: likely path after converter.
- Mahimahi: possible after conversion.
- tc/netem: not first path.

## Limitations

Single service/day limits generality. Trace duration may be shorter than some full-video runs and must be aligned with test segment count.

## Decision

`candidate-selected-for-first-benchmark-design`

## Memory usage

- Chapter 6 dataset matrix and benchmark design.
- Appendix: split/leakage notes.

## BibTeX provisional

```bibtex
@misc{lancasterAbrThroughputTraces,
  title = {ABR-Throughput-Traces},
  author = {{Lancaster Networks Group}},
  year = {2018},
  howpublished = {GitHub repository},
  note = {Accessed 2026-05-20}
}
```
