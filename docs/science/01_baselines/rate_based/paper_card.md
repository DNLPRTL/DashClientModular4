# Paper Card: Rate-Based Baseline

| field | value |
| --- | --- |
| title | Rate Adaptation for Adaptive HTTP Streaming |
| authors | Changhao Liu, Imed Bouazizi, Moncef Gabbouj |
| year | 2011 |
| venue | ACM MMSys 2011 |
| DOI/URL if known | https://doi.org/10.1145/1943552.1943575 |
| type | Academic ABR baseline paper |
| role in the TFG | Primary source for the mandatory throughput/rate-based baseline. |
| key contribution | Receiver-driven rate adaptation using HTTP segment download measurements, with smoothed throughput, conservative increase, and aggressive decrease behavior without TCP-layer RTT/loss dependency. |
| algorithm family if applicable | Throughput-based / rate-based ABR. |
| required signals if applicable | Segment size, segment download time, representation ladder, current level, previous throughput estimate, and segment index. |
| implementation relevance | Implemented in Phase 2.3.2: derives measured throughput from application-layer download signals, smooths it with EWMA, applies a safety factor, and maps target rate to the ladder through the existing controller contract. |
| what it does NOT justify | Does not justify a final QoE reward, trace replay design, TCP-layer instrumentation, or modifying downloader/player metrics. |
| use in thesis memory | Chapter 2 baseline family; Chapter 5 implementation; Chapter 6 comparison. |
| provisional BibTeX key | `liu2011rateAdaptation` |
| decision | Mandatory baseline implemented first among academic ABR controllers; fake smoke is integration validation only, not benchmark evidence. |
