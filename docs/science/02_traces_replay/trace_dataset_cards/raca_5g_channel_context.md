# Trace dataset card — Raca et al. 5G channel/context dataset

## Identity

- Name: Beyond Throughput, The Next Generation: A 5G Dataset with Channel and Context Metrics.
- Primary paper: Darijo Raca, Dylan Leahy, Cormac J. Sreenan, Jason J. Quinlan. MMSys 2020.
- Dataset/project: UCC/MISL 5G dataset.
- Year: 2020.
- Type: real-world 5G throughput + channel/context KPI dataset.
- Phase 3.2A status: mandatory dataset card.
- Phase 3.2A decision: 5G OOD/modern-mobile candidate, not first integration.

## Domain

5G production network from a major Irish mobile operator.

## Availability

Public GitHub repository/source exists. Download must remain outside the repository.

## License

GPL-3.0 according to repository/source note. Review implications before copying any data/code.

## Size

Paper reports 83 traces and 3142 minutes total duration.

## Format

G-NetTrack Pro data with timestamp, GPS, velocity, operator/cell/network mode, downlink/uplink bitrate, download state, ping statistics, SNR/RSRQ/RSRP and other channel/context metrics.

## Throughput unit

Paper lists `DL_bitrate` and `UL_bitrate` at application layer in kbps.

## Time granularity

One sample per second.

## Duration

3142 minutes total production dataset duration.

## Mobility/scenario

Static and driving mobility patterns. Application patterns include file download, Netflix and Amazon Prime streaming.

## ABR usage in literature

Designed for 5G/HAS/adaptive-client research and includes video streaming application patterns.

## Train suitability

Possible later, but not first target.

## Validation suitability

Possible modern 5G validation source.

## Test suitability

Possible modern 5G test source.

## OOD suitability

Strong 5G OOD candidate.

## Leakage risks

- Same operator/device/month/application/mobility patterns can leak if split naively.
- GPL-3.0 and repository contents must not be copied blindly.
- App-specific streaming traces may be influenced by service behavior.

## Download requirements

- Download outside repo only.
- Store under `_datasets/phase3_traces_replay/05_5g_ireland_candidate`.
- Verify license and schema before use.

## DashClientModular4 integration notes

Likely requires a converter selecting `DL_bitrate` and timestamp fields. Preserve app pattern and mobility metadata for OOD labeling.

## Replay/emulation requirements

- Custom Python runner: possible after converter.
- Mahimahi: possible after conversion, not first path.
- tc/netem: not first path.

## Limitations

High integration risk compared with simple HSDPA/Ghent logs. 5G application and channel context may be more complex than throughput-only replay.

## Decision

`candidate-5g-OOD-or-modern-mobile`

## Memory usage

- Chapter 6 OOD/generalization table.
- Future work if IA uses context features.

## BibTeX provisional

```bibtex
@inproceedings{raca2020beyondThroughput5g,
  title = {Beyond Throughput, The Next Generation: A 5G Dataset with Channel and Context Metrics},
  author = {Raca, Darijo and Leahy, Dylan and Sreenan, Cormac J. and Quinlan, Jason J.},
  booktitle = {Proceedings of the 11th ACM Multimedia Systems Conference},
  year = {2020}
}
```
