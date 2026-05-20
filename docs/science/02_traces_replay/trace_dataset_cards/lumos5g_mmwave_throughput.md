# Trace dataset card — Lumos5G mmWave throughput

## Identity

- Name: Lumos5G: Mapping and Predicting Commercial mmWave 5G Throughput.
- Primary paper: Arvind Narayanan et al. IMC 2020.
- Dataset/project: Lumos5G commercial mmWave 5G measurement study.
- Year: 2020.
- Type: 5G/mmWave throughput measurement and prediction dataset/source.
- Phase 3.2A status: mandatory dataset/source card.
- Phase 3.2A decision: high-variability 5G OOD candidate, not first integration.

## Domain

Commercial mmWave 5G in a major U.S. city, focused on application-perceived throughput on user equipment.

## Availability

Project/data source exists according to paper/source. Exact download status, license and raw format must be verified before use.

## License

Unknown/TBD.

## Size

Paper reports 563,840 per-second throughput samples with features, 38,632 GB downloaded over 5G, six months of measurements, walking over 331 km, driving over 132 km and stationary data.

## Format

TBD before use. Paper emphasizes throughput samples with UE-side features and context.

## Throughput unit

Mbps/Gbps in paper figures. Exact dataset columns and units TBD.

## Time granularity

One-second samples according to paper dataset statistics.

## Duration

Six months of measurements according to paper table.

## Mobility/scenario

Walking, driving and stationary. Includes indoor/outdoor urban settings and mmWave-specific factors.

## ABR usage in literature

Relevant to high-resolution video and throughput prediction for bandwidth adaptation. Not directly a DASH ABR benchmark dataset yet.

## Train suitability

Not first target. Possible future IA/5G predictor work.

## Validation suitability

Possible modern 5G validation if raw throughput traces are accessible and convertible.

## Test suitability

Possible 5G test source.

## OOD suitability

Strong high-variance 5G/mmWave OOD candidate.

## Leakage risks

- Location/trajectory repetition can leak if split naively.
- Repeated passes over same trajectories must be grouped.
- Prediction features should not be mixed into simple throughput replay without a methodology note.

## Download requirements

- No download in Phase 3.2A.
- If later used, store under `_datasets/phase3_traces_replay/06_lumos5g_candidate`.
- Verify availability, license, schema and whether traces are directly replayable.

## DashClientModular4 integration notes

Use as an OOD/generalization source first. Do not make it the first runner-conversion target.

## Replay/emulation requirements

- Custom Python runner: possible only after schema verification.
- Mahimahi: possible only after conversion.
- tc/netem: not first path.

## Limitations

Primarily a 5G throughput prediction/mapping study; direct ABR replay use must be justified and may require filtering/conversion.

## Decision

`candidate-high-variability-5g-OOD`

## Memory usage

- Chapter 6 OOD/generalization discussion.
- Defense: explain why 5G/mmWave is kept as OOD rather than first integration.

## BibTeX provisional

```bibtex
@inproceedings{narayanan2020lumos5g,
  title = {Lumos5G: Mapping and Predicting Commercial mmWave 5G Throughput},
  author = {Narayanan, Arvind and Ramadan, Eman and Mehta, Rishabh and Hu, Xinyue and Liu, Qingxu and Fezeu, Rostand A. K. and Dayalan, Udhaya Kumar and Verma, Saurabh and Ji, Peiqi and Li, Tao and Qian, Feng and Zhang, Zhi-Li},
  booktitle = {Proceedings of the ACM Internet Measurement Conference},
  year = {2020}
}
```
