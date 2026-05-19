# Paper Card: BBA Baseline

| field | value |
| --- | --- |
| title | A Buffer-Based Approach to Rate Adaptation: Evidence from a Large Video Streaming Service |
| authors | Te-Yuan Huang, Ramesh Johari, Nick McKeown, Matthew Trunnell, Mark Watson |
| year | 2014 |
| venue | ACM SIGCOMM 2014 |
| DOI/URL if known | https://doi.org/10.1145/2619239.2626296 |
| type | Academic ABR baseline paper |
| role in the TFG | Primary source for the mandatory BBA buffer-based baseline. |
| key contribution | Uses playback buffer occupancy as the primary decision signal, with capacity estimation mainly useful during startup and a simple reservoir/cushion buffer map. |
| algorithm family if applicable | Buffer-based ABR. |
| required signals if applicable | Buffer occupancy in seconds, representation ladder, current level, reservoir, cushion, and startup rule. |
| implementation relevance | Implemented in Phase 2.3.3: documents and implements the BBA-0 buffer map, reservoir/cushion parameters, safe startup/min fallback, and ladder quantization. |
| what it does NOT justify | Does not justify throughput-only control, final QoE reward, or benchmark trace design. |
| use in thesis memory | Chapter 2 buffer-based ABR; Chapter 5 implementation; Chapter 6 comparison. |
| provisional BibTeX key | `huang2014bba` |
| decision | Mandatory baseline implemented second among academic ABR controllers, after `rate_based`; fake smoke is integration validation only, not benchmark evidence. |
