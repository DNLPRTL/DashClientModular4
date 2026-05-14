# Source evidence â€” DASH, HAS and field map

Phase: 2.2A â€” PDF-grounded source evidence  
Sources: Stockhammer 2011; ISO/IEC 23009-1:2022; Bentaleb et al. 2019; Timmerer et al. 2025; Peroni and Gorinsky 2025.  
Status: field-map evidence only. Not runtime code.

## Purpose

This document extracts the DASH/HAS evidence needed to support the baseline implementation docs and the thesis background.

## Source roles

| Source | Role |
|---|---|
| Stockhammer 2011 | design principles and early standardization context for DASH |
| ISO/IEC 23009-1:2022 | official terminology and data model reference |
| Bentaleb et al. 2019 | ABR/HAS taxonomy and client-side adaptation context |
| Timmerer et al. 2025 | recent HAS overview and current/future directions |
| Peroni and Gorinsky 2025 | recent end-to-end streaming pipeline survey |

## Evidence extracted

### DASH addresses progressive-download and traditional-streaming limitations

Stockhammer contrasts:
- traditional stateful streaming;
- progressive download over HTTP;
- DASH/HAS with client-controlled segment requests and adaptation.

Operational consequence:
- DashClientModular4 is correctly positioned as a client-side DASH/HAS system.
- ABR controllers decide what representation to request for future segments.

### MPD and segments

ISO/IEC 23009-1:2022 specifies the formats for:
- Media Presentation Description (MPD);
- Segments;
- HTTP GET / partial GET access to resources referenced by MPD.

Operational consequence:
- Representation ladder must come from MPD/client state.
- Segment duration, Representation metadata and Segment URLs are DASH data-model concepts.
- Controllers should not invent external ladders outside client configuration/MPD state.

### DASH Client model

The standard's informative client model includes a DASH access engine that receives the MPD, constructs requests, and receives segments or parts of segments.

Operational consequence:
- Controller logic belongs client-side.
- Server is not required to run an ABR algorithm.
- Client requests segments and may dynamically select among representations.

### Adaptation Set, Representation, Segment

Useful terminology:
- `Adaptation Set`: set of interchangeable encoded versions/components.
- `Representation`: encoded deliverable version with metadata.
- `Segment`: unit of data referenced by HTTP URL or byte range.
- `Initialization Segment`: metadata needed before media segments.
- `Media Segment`: media data used for playback.

Operational consequence:
- `quality_level` should be representation index.
- `target_rate` is derived from representation bitrate.
- Future docs should use "representation" and "segment" consistently.

### Standards do not define the ABR algorithm

Bentaleb 2019 and Timmerer 2025 reinforce that DASH/HAS standards define formats/protocol structure but leave adaptation logic open to implementations.

Operational consequence:
- It is academically valid to implement multiple ABR baselines on top of the same DASH client.
- The TFG contribution is in baseline controller implementation/evaluation, not in changing the DASH standard.

### ABR families

Bentaleb 2019 and practical sources support the family taxonomy:
- throughput/rate-based;
- buffer-based;
- hybrid/control-theoretic;
- learning/neural;
- server/network-assisted variants.

Operational consequence:
- Mandatory implementation set covers: rate_based, BBA, BOLA, MPC, RobustMPC.
- SODA is optional modern non-neural.
- Pensieve is historical neural reference, not Phase 2 implementation.

### End-to-end pipeline scope

Peroni and Gorinsky 2025 frames video streaming as ingestion, processing and distribution. ABR is located in the distribution/client playback stage alongside CDN and QoE concerns.

Operational consequence:
- DashClientModular4 scope is client-side ABR, not transcoding, CDN placement, encoding ladder optimization, upload/ingestion, or server-side analytics.

## ISO copyright and usage rule

The ISO PDF is private licensed material and must not be committed to Git or copied into repo docs. Use only short paraphrased terminology and bibliographic reference.

Do not:
- copy long definitions;
- copy figures/tables;
- include the PDF in the repository;
- pass the raw ISO PDF to Codex.

## Implementation relevance

This field evidence informs:
- source inventories;
- baseline signal matrix;
- controller API mapping;
- memory chapter 2;
- thesis terminology.

It does not define:
- final QoE/reward;
- benchmark methodology;
- replay/traces;
- runtime code.

## Use in memory

Chapter 1:
- motivate video streaming and adaptive delivery.

Chapter 2:
- explain HAS/DASH, MPD, Representations, Segments and client-side ABR.

Chapter 5:
- connect client architecture to DASH concepts.

Suggested own figures:
- DASH client request loop.
- MPD -> Adaptation Set -> Representation -> Segment hierarchy.
- TFG scope inside end-to-end streaming pipeline.