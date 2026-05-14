# Paper Card: BOLA Baseline

| field | value |
| --- | --- |
| title | BOLA: Near-Optimal Bitrate Adaptation for Online Videos |
| authors | Kevin Spiteri, Rahul Urgaonkar, Ramesh K. Sitaraman |
| year | 2020 |
| venue | IEEE/ACM Transactions on Networking |
| DOI/URL if known | https://doi.org/10.1109/TNET.2020.2996964 |
| type | Academic ABR baseline paper |
| role in the TFG | Primary source for the mandatory BOLA baseline. |
| key contribution | Formulates bitrate adaptation as utility maximization and uses Lyapunov optimization for a buffer-based online controller without explicit bandwidth prediction. |
| algorithm family if applicable | Buffer-based utility optimization. |
| required signals if applicable | Buffer occupancy, representation ladder, segment duration, utility per representation, current level, and BOLA control parameters. |
| implementation relevance | Future implementation must define the utility function and parameter calibration before code. |
| what it does NOT justify | Does not justify implementing dash.js DYNAMIC, FAST SWITCHING, or a mixed BOLA-E variant without an explicit source mapping. |
| use in thesis memory | Chapter 2 BOLA background; Chapter 5 implementation; Chapter 6 comparison. |
| provisional BibTeX key | `spiteri2020bola` |
| decision | Mandatory later baseline; implementation blocked until the full five-doc package exists. |
