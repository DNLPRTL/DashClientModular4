# Local Streaming Related Work

## Policy

Ameigeiras et al. 2012 and Ramos-Munoz et al. 2014 are included as local/UGR-related video traffic characterization work.

They are not ABR baselines. They must not create runtime requirements, controller requirements, trace requirements, or benchmark obligations.

## Role In The TFG

| source | role | thesis use | non-use |
| --- | --- | --- | --- |
| Ameigeiras et al. 2012 | Characterizes YouTube traffic and traffic generation behavior, including burst/throttling patterns. | Motivation/background evidence that video traffic behavior is structured and relevant to network design. | Not a DASH ABR controller source. |
| Ramos-Munoz et al. 2014 | Characterizes mobile YouTube traffic with mobile/device/network considerations. | Motivation/background evidence that device, buffer, and mobile network conditions affect video traffic behavior. | Not a DASH ABR controller source. |

## Suggested Thesis Message

Local work from the Universidad de Granada context can be used to motivate why video streaming traffic deserves careful measurement and modeling. The ABR baseline work in this TFG starts from that motivation but targets MPEG-DASH client-side adaptation rather than reproducing YouTube traffic models.
