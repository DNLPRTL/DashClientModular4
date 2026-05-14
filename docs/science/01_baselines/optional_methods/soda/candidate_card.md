# Candidate Card: SODA

| field | value |
| --- | --- |
| title | SODA: An Adaptive Bitrate Controller for Consistent High-Quality Video Streaming |
| authors | Tianyu Chen, Yiheng Lin, Nicolas Christianson, Zahaib Akhtar, Sharath Dharmaji, Mohammad Hajiesmaili, Adam Wierman, Ramesh K. Sitaraman |
| year | 2024 |
| venue | ACM SIGCOMM 2024 |
| DOI/URL if known | https://doi.org/10.1145/3651890.3672260 |
| type | Modern optional candidate |
| role in the TFG | Strongest modern non-neural optional comparator and future extension candidate. |
| key contribution | Smoothness optimized dynamic adaptive controller, SOCO-inspired, robust to throughput prediction errors, and designed for production deployability. |
| algorithm family if applicable | Modern non-neural optimization / smoothness-oriented ABR. |
| required signals if applicable | Throughput prediction, buffer/latency context, smoothness objective, QoE model, controller parameters. |
| implementation relevance | Useful later if the TFG extends beyond classic baselines to a recent non-neural method. |
| what it does NOT justify | Does not justify adding SODA to the initial implementation order, changing QoE now, or implementing production-specific assumptions before documentation. |
| use in thesis memory | Optional methods table and future-work discussion. |
| provisional BibTeX key | `chen2024soda` |
| decision | Document only; do not implement initially. |
