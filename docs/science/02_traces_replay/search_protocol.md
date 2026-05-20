# Search Protocol

This protocol defines how Phase 3 searches for trace datasets, replay tools and emulation methodology. It is designed to be reproducible without downloading data during Phase 3.1.

## Search Questions

1. Which public throughput trace datasets have been used for HTTP Adaptive Streaming or ABR evaluation?
2. Which datasets include enough timing and throughput information to drive a future DashClientModular4 fake trace runner?
3. Which datasets include cellular context metrics useful for OOD or generalization analysis?
4. Which replay or emulation tools are scientifically established and practical for this Python client?
5. Which sources are method references only, and which are candidate inputs for future experiments?

## Search Locations

| location | use |
| --- | --- |
| ACM Digital Library, USENIX, IEEE, publisher pages | Paper identity, DOI, venue and official abstracts. |
| University/project pages | Dataset description, access instructions and citation requirements. |
| Dataset repositories such as GitHub, Zenodo or institutional archives | Availability, format, license and storage risk. |
| Tool manuals and project pages | Method capabilities, platform requirements and limitations. |
| Existing Phase 2 docs | Controller context and forbidden benchmark claims. |

## Query Patterns

- `"adaptive bitrate" throughput traces dataset`
- `"HTTP Adaptive Streaming" throughput traces`
- `"DASH" "bandwidth traces" dataset`
- `"Mahimahi" "adaptive bitrate" replay`
- `"tc netem" "network emulation" throughput trace`
- `"4G LTE" "throughput" "dataset" "adaptive video"`
- `"5G" "throughput" "dataset" "context metrics"`
- `"Puffer" "data description" "video streaming"`
- `"Pensieve" "trace" "replay" "evaluation"`

## Inclusion Criteria

A source can be included when it satisfies at least one of these conditions:

- it is a replay or emulation method used in network systems research;
- it is an ABR paper that documents trace/simulation/replay methodology;
- it is a throughput trace dataset with timing data;
- it is a cellular or broadband dataset that can inform scenario realism;
- it provides metadata needed to evaluate availability, license, format or storage risk.

## Exclusion Criteria

Exclude or defer sources when:

- they only contain subjective QoE labels and no directly reusable throughput/time series;
- they require large raw downloads before metadata can be evaluated;
- license or redistribution terms are incompatible with the repository rules;
- they require changing controllers, player behavior, media engines or metric definitions;
- they only support IA/RL training and do not inform Phase 3 trace/replay methodology;
- they are generated artifacts, PDFs, logs, CSVs, ZIPs or media files.

## Capture Fields

For every candidate source, capture:

- title and short name;
- authors or maintaining organization;
- year and venue or repository;
- DOI or stable URL;
- source type: method, dataset, dataset paper, manual, reference;
- domain: fixed broadband, 3G/HSDPA, 4G/LTE, 5G, live/HAS, deployment;
- availability and license notes;
- data format, unit, granularity and duration if known;
- Phase 3 role and current decision;
- storage, integration and leakage risks.

## Staged Workflow

1. Record the source in `source_inventory.md`.
2. Add or update a row in `trace_dataset_matrix.md` if it is a dataset candidate.
3. Create a dataset or method card only after the source is promoted from inventory review.
4. Complete `trace_dataset_selection.md` before any dataset becomes final.
5. Complete `replay_emulation_decision.md` before any runner or emulation script is implemented.

## Evidence Handling

- Use links and paraphrases, not copied paper text.
- Do not store PDFs in the repository.
- Do not store dataset samples in the repository.
- Record uncertainty explicitly as `TBD`.
- Re-check publisher and dataset pages before final thesis bibliography or implementation work.

