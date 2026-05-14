# Source Card: dash.js Practical BOLA Source

| field | value |
| --- | --- |
| title | From Theory to Practice: Improving Bitrate Adaptation in the DASH Reference Player |
| authors | Kevin Spiteri, Ramesh K. Sitaraman, Daniel Sparacio |
| year | 2019 |
| venue | ACM Transactions on Multimedia Computing, Communications and Applications |
| DOI/URL if known | https://doi.org/10.1145/3336497 |
| type | Practical source artifact |
| role in the TFG | Practical source for BOLA-E, DYNAMIC, FAST SWITCHING, and Sabre in the DASH reference player context. |
| key contribution | Bridges theoretical BOLA-style adaptation and production/reference-player behavior in dash.js. |
| algorithm family if applicable | Practical BOLA variant and hybrid production ABR methods. |
| required signals if applicable | For BOLA-E: buffer, ladder, utility/parameters. For DYNAMIC: throughput-mode and BOLA-mode signals plus mode switch thresholds. For FAST SWITCHING: buffer/segment replacement context. |
| implementation relevance | Use only to document BOLA practical context and possible future dash.js-derived variants. |
| what it does NOT justify | Does not justify implementing DYNAMIC or FAST SWITCHING initially. Does not authorize silently mixing paper BOLA and dash.js behavior. |
| use in thesis memory | Chapter 2 practical player context; Chapter 5 limitations if BOLA is adapted. |
| provisional BibTeX key | `spiteri2019dashjs` |
| decision | Create source card now; defer DYNAMIC and FAST SWITCHING as optional future hybrid/practical methods. |

## Specific dash.js Policy

DYNAMIC combines throughput mode at low buffer with BOLA mode at higher buffer and became the default ABR algorithm in dash.js 3.0.0. It is useful context, but it is not part of the initial baseline set.
