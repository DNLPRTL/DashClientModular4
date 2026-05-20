# Trace dataset card — Ghent 4G/LTE Bandwidth Logs

## Identity

- Name: 4G/LTE Bandwidth Logs.
- Related paper: Jeroen van der Hooft et al. *HTTP/2-Based Adaptive Streaming of HEVC Video over 4G/LTE Networks*. 2016.
- Dataset/project: Ghent 4G/LTE bandwidth logs.
- Year: measurements January/February 2016; dataset page reports 2015-12-16 to 2016-02-04.
- Type: real-world 4G/LTE throughput traces.
- Phase 3.2A status: mandatory dataset card.
- Phase 3.2A decision: first-real-integration candidate.

## Domain

4G/LTE mobile access in and around Ghent, Belgium.

## Availability

Public dataset page/source exists. Download must remain outside the repository.

## License

Unknown/TBD. Verify before redistribution or packaging.

## Size

Paper reports 40 traces and 5 hours of monitoring.

## Format

Logs from an Android application. The paper describes GPS coordinates, bytes received since the previous datapoint and milliseconds since the previous datapoint, from which average throughput can be calculated.

## Throughput unit

Derived from bytes and elapsed milliseconds; convert to internal bits/s or kbps consistently.

## Time granularity

TBD after dataset inspection. The format is analogous to Riiser-style logs.

## Duration

5 hours total monitoring according to the paper.

## Mobility/scenario

Foot, bicycle, bus, tram, train and car.

## ABR usage in literature

Used in an HTTP adaptive streaming over 4G/LTE study. Good complement to HSDPA for mobile bandwidth variation.

## Train suitability

Possible later, but not before split policy is closed.

## Validation suitability

Strong candidate for LTE/mobile validation if HSDPA is used for first integration.

## Test suitability

Strong candidate for mobile LTE test set.

## OOD suitability

Candidate OOD if training uses HSDPA/broadband/HAS traces.

## Leakage risks

- Multiple traces by transport mode and route may be correlated.
- Do not randomly split subwindows without grouping by original trace/route/mode.
- Do not merge with HSDPA as one undifferentiated mobile dataset.

## Download requirements

- Download outside repo only.
- Store under `_datasets/phase3_traces_replay/03_4g_belgium_candidate`.
- Record source, license, download date and conversion notes.

## DashClientModular4 integration notes

Good second external trace target after HSDPA because the format is similar enough to support the same converter design with LTE domain labeling.

## Replay/emulation requirements

- Custom Python runner: likely first path.
- Mahimahi: possible after conversion, not first path.
- tc/netem: not first path.

## Limitations

LTE measurements from a specific city and period; do not generalize globally.

## Decision

`candidate-selected-for-first-real-integration`

## Memory usage

- Chapter 6 dataset selection table.
- Appendix: dataset card and conversion notes.

## BibTeX provisional

```bibtex
@article{vanDerHooft2016ghent4g,
  title = {HTTP/2-Based Adaptive Streaming of HEVC Video over 4G/LTE Networks},
  author = {van der Hooft, Jeroen and Petrangeli, Stefano and Wauters, Tim and Huysegems, Rafael and Rondao Alface, Patrice and Bostoen, Tom and De Turck, Filip},
  year = {2016}
}
```
