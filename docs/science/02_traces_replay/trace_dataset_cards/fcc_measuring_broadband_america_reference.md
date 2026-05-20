# Trace dataset card — FCC Measuring Broadband America reference

## Identity

- Name: FCC Measuring Broadband America / Measuring Broadband Raw Data Releases — Fixed.
- Project/source: Federal Communications Commission.
- Year: multiple historical releases.
- Type: fixed-broadband measurement data source.
- Phase 3.2A status: mandatory reference-only dataset card.
- Phase 3.2A decision: reference-only until conversion/download plan.

## Domain

Fixed broadband measurement data.

## Availability

Public raw-data release pages exist. Current source note says the program is not collecting additional data and historical releases remain available.

## License

Government/public-data status likely, but exact reuse/citation policy must be verified before packaging.

## Size

High/unknown. Treat as high storage risk.

## Format

Raw measurement releases. Exact schema TBD.

## Throughput unit

TBD.

## Time granularity

TBD. Pensieve paper references FCC traces with 5-second granularity after selecting/processing a category, but that does not mean raw FCC data can be used directly without conversion.

## Duration

TBD. Pensieve paper used derived traces, not a direct Phase 3.2A download.

## Mobility/scenario

Fixed broadband.

## ABR usage in literature

Important because Pensieve-style methodology used FCC broadband traces.

## Train suitability

Possible later only after conversion plan.

## Validation suitability

Possible later only after conversion plan.

## Test suitability

Possible later only after conversion plan.

## OOD suitability

Broadband OOD candidate if training uses mobile/HAS traces.

## Leakage risks

- Raw releases may include repeated measurements from same probes/locations.
- Must group by probe/location/time if used.
- Conversion choices can introduce hidden leakage if windows from same measurement are split randomly.

## Download requirements

No download in Phase 3.2A.

## DashClientModular4 integration notes

Keep as broadband reference source. Do not implement parser until a dedicated conversion/storage plan exists.

## Replay/emulation requirements

TBD after conversion plan.

## Limitations

Large and complex source; not suitable for first local dataset.

## Decision

`reference-only-until-conversion-plan`

## Memory usage

- Chapter 6: broadband reference and prior-methodology context.
- Bibliography.

## BibTeX provisional

```bibtex
@misc{fccMeasuringBroadbandAmerica,
  title = {Measuring Broadband America},
  author = {{Federal Communications Commission}},
  year = {2026},
  note = {Accessed 2026-05-20}
}
```
