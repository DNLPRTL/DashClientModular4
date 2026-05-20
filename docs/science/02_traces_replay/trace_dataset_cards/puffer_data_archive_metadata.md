# Trace dataset card — Puffer data archive metadata

## Identity

- Name: Puffer data archive / Puffer statistics.
- Project/source: Stanford Puffer.
- Year: data collection began in January 2019 according to source note; ongoing data publication.
- Type: real-world video streaming logs/data archive.
- Phase 3.2A status: mandatory metadata-only source card.
- Phase 3.2A decision: metadata-only until conversion/storage/causal plan.

## Domain

Real-world live video streaming service with randomized ABR experiments.

## Availability

Puffer publishes anonymized data/results for research and has an analysis repository. Do not download raw daily data in Phase 3.2A.

## License

Unknown/TBD. Verify before use.

## Size

High. Treat as high storage and integration risk.

## Format

Daily/raw archives and analysis pipeline. Exact schema must be studied before any use.

## Throughput unit

Chunk/log-derived measurements; exact fields TBD.

## Time granularity

Chunk/session-level, not a simple exogenous capacity trace by default.

## Duration

Daily ongoing data archive. Exact selected period TBD.

## Mobility/scenario

Real users over Internet paths. Not controlled local traces.

## ABR usage in literature

Puffer/Fugu, CausalSim, Veritas and later work use Puffer-like data or platform methodology.

## Train suitability

Possible later only with a careful plan; not Phase 3.2A.

## Validation suitability

Possible later only with a careful plan.

## Test suitability

Possible later only with a careful plan.

## OOD suitability

Strong real-world candidate, but not a simple OOD throughput trace.

## Leakage risks

Very high:
- logs reflect decisions made by deployed ABR algorithms;
- causal confounding risk;
- session/user/time correlations;
- survivorship and deployment-context bias;
- daily data may produce hidden temporal leakage.

## Download requirements

No raw data download in Phase 3.2A.

## DashClientModular4 integration notes

Use now only to document methodology and future data possibilities. If later used, first create a Puffer-specific schema, storage, license and causal-risk plan.

## Replay/emulation requirements

Not first target. Requires a careful decision whether logs can be converted to exogenous throughput traces or whether they should be treated differently.

## Limitations

Complex and causally nontrivial. Not suitable as first dataset for runner implementation.

## Decision

`metadata-only-until-conversion-storage-causal-plan`

## Memory usage

- Chapter 6: real-world methodology, threats to validity and future work.

## BibTeX provisional

```bibtex
@misc{pufferDataArchive,
  title = {Puffer data archive and data description},
  author = {{Stanford Puffer}},
  year = {2026},
  note = {Accessed 2026-05-20}
}
```
