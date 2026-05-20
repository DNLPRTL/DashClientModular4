# Trace dataset card — Norway HSDPA / MMSys 2013

## Identity

- Name: Commute Path Bandwidth Traces from 3G Networks.
- Primary paper: Haakon Riiser, Paul Vigmostad, Carsten Griwodz, Pål Halvorsen. *Commute Path Bandwidth Traces from 3G Networks: Analysis and Applications*. MMSys 2013.
- Dataset/project: Norway/Oslo 3G/HSDPA commute bandwidth traces.
- Year: 2013.
- Type: real-world mobile throughput trace dataset.
- Phase 3.2A status: mandatory dataset card.
- Phase 3.2A decision: first-real-integration candidate.

## Domain

3G/UMTS/HSDPA mobile access during public-transport commute routes around Oslo, Norway, plus a few car logs.

## Availability

Public dataset page/source exists. Download must remain outside the repository.

## License

Unknown/TBD. Verify before redistribution or packaging.

## Size

TBD from dataset archive. Paper reports 86 traces from 11 routes.

## Format

Plain ASCII text logs. Paper describes six fields per log entry:
1. Unix timestamp.
2. Monotonic timestamp in milliseconds.
3. Latitude.
4. Longitude.
5. Bytes received since previous measurement.
6. Milliseconds elapsed since previous measurement.

## Throughput unit

Derived from bytes received and elapsed milliseconds. Conversion to internal schema should produce bits/s or kbps consistently.

## Time granularity

Approximately one sample per second.

## Duration

Per trace TBD after dataset inspection. Paper/source describe commute-route logs and repeated routes.

## Mobility/scenario

Metro, tram, train, bus, ferry and some car traces.

## ABR usage in literature

Classic ABR-relevant dataset. Pensieve-style methodology uses HSDPA traces as a mobile trace source.

## Train suitability

Possible only if not reserved for legacy-mobile test/OOD. Do not use for IA training until final split is closed.

## Validation suitability

Possible, but should be separated by route/session.

## Test suitability

Strong candidate for legacy-mobile controlled testing.

## OOD suitability

Good legacy-mobile OOD candidate if future training uses broadband or modern LTE/5G traces.

## Leakage risks

- Multiple traces from same routes can leak route-specific conditions.
- Do not split random windows from the same route into train/test without grouping.
- If sliding windows are used later, group by original trace/route first.

## Download requirements

- Download outside repo only.
- Store under `_datasets/phase3_traces_replay/01_hsdpa_norway_candidate`.
- Record source, license, download date and conversion notes.

## DashClientModular4 integration notes

This is the preferred first external trace candidate because the format is simple and ABR-relevant. A converter can map each line to a common internal schema once Phase 3.2B authorizes implementation.

## Replay/emulation requirements

- Custom Python runner: yes, likely first target.
- Mahimahi: possible after conversion to packet-delivery trace, not first target.
- tc/netem: not first target.

## Limitations

Legacy 3G/HSDPA behavior should not be overclaimed as modern LTE/5G behavior.

## Decision

`candidate-selected-for-first-real-integration`

## Memory usage

- Chapter 6 dataset selection table.
- Appendix: dataset card and conversion notes.

## BibTeX provisional

```bibtex
@inproceedings{riiser2013commutePath,
  title = {Commute Path Bandwidth Traces from 3G Networks: Analysis and Applications},
  author = {Riiser, Haakon and Vigmostad, Paul and Griwodz, Carsten and Halvorsen, Pal},
  booktitle = {Proceedings of the 4th ACM Multimedia Systems Conference},
  year = {2013}
}
```
