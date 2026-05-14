# Candidate Card: PANDA

| field | value |
| --- | --- |
| title | Probe and Adapt: Rate Adaptation for HTTP Video Streaming at Scale |
| authors | Zhi Li, Xiaoqing Zhu, Josh Gahm, Rong Pan, Hao Hu, Ali C. Begen, Dave Oran |
| year | 2013 / 2014 |
| venue | arXiv / later journal or conference versions to verify before implementation |
| DOI/URL if known | https://arxiv.org/abs/1305.0510 |
| type | Optional candidate |
| role in the TFG | Possible stronger throughput-family comparator after the mandatory rate-based baseline. |
| key contribution | Introduces probe-and-adapt behavior for HAS rate adaptation at scale. |
| algorithm family if applicable | Throughput/rate probing. |
| required signals if applicable | Throughput/rate estimate, probing state, buffer safety context, representation ladder. |
| implementation relevance | Could be useful if the TFG later needs a more advanced non-MPC throughput controller. |
| what it does NOT justify | Does not replace the mandatory Liu et al. rate-based baseline in the initial order. |
| use in thesis memory | Optional candidates or future work. |
| provisional BibTeX key | `li2013panda` |
| decision | Optional only; do not implement initially. |
