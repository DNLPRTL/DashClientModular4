# Source evidence â€” local UGR streaming-related work

Phase: 2.2A â€” PDF-grounded source evidence  
Sources: Ameigeiras et al. 2012; Ramos-MuÃ±oz et al. 2014.  
Status: local related work evidence only. Not baseline evidence and not runtime code.

## Purpose

This document captures how the two local/professor-related papers fit into the TFG without changing the technical roadmap.

## Source roles

| Source | Role |
|---|---|
| Ameigeiras et al. 2012 â€” Analysis and modelling of YouTube traffic | local/UGR work on YouTube progressive-download traffic modeling |
| Ramos-MuÃ±oz et al. 2014 â€” Characteristics of mobile YouTube traffic | local/UGR work on mobile YouTube traffic, 3G terminals and buffer/download behavior |

## Evidence extracted from Ameigeiras et al. 2012

### YouTube traffic as important video traffic

The paper motivates YouTube as a significant part of Internet traffic and argues that understanding its traffic generation pattern helps predict user video quality and improve network design.

Use in TFG:
- motivation;
- local related work;
- historical context before DASH/HAS ABR.

### Progressive download behavior

The paper characterizes YouTube over HTTP/TCP progressive download from a regular PC.

Relevant traffic pattern:
- initial burst;
- later throttling phase;
- traffic generation depends on video encoding rate;
- if bandwidth is reduced, excess data behaves as if accumulated in a server-side buffer and later drained.

Use in TFG:
- explain that HTTP video traffic is not trivial constant-rate delivery;
- motivate why client buffer and network variation matter.

### Model/emulation

The paper proposes a YouTube server traffic generation model and validates it by comparing synthetic traces against original YouTube server downloads.

Use in TFG:
- cite as local precedent for traffic characterization and emulation thinking;
- do not reuse model as DASH benchmark;
- do not implement YouTube traffic generator in Phase 2.

## Evidence extracted from Ramos-MuÃ±oz et al. 2014

### Mobile YouTube traffic

The paper characterizes YouTube traffic from iOS and Android terminals over 3G mobile networks.

Relevant observations:
- mobile access uses different formats/parameters from desktop;
- 3GP formats and lower encoding rates appear in the study;
- YouTube mobile also exhibits initial burst and throttling phases;
- terminal behavior can strongly influence downloads.

### Device and buffer behavior

The paper reports:
- high-end Android terminals can use a dual-threshold buffer policy that interrupts and resumes download depending on buffer occupancy;
- iOS terminals may download the full clip without interruption;
- mid-range Android terminals may throttle due to TCP receive-window behavior when buffer fills.

Use in TFG:
- show that client/device/buffer behavior matters in real video traffic;
- create local-related-work link to professor/group research;
- support motivation for studying ABR client logic.

## Decision

These papers are included as:
```text
local_related_work / video_traffic_characterization
```

They are not:
```text
ABR baselines
DASH controller sources
QoE final sources
runtime requirements
benchmark methodology
```

## How to cite in thesis

Chapter 1:
- one or two sentences in motivation about video traffic, burst/throttling and mobile variability.

Chapter 2:
- subsection "Antecedentes locales sobre caracterizaciÃ³n de trÃ¡fico de vÃ­deo".
- Explain that these works characterize YouTube traffic and mobile YouTube behavior.
- Transition to MPEG-DASH/HAS and ABR.

Suggested paragraph idea:
```text
Trabajos previos realizados en el entorno de la Universidad de Granada caracterizaron el trÃ¡fico de YouTube en accesos de PC y redes mÃ³viles, mostrando patrones de rÃ¡faga inicial, throttling y comportamientos dependientes del terminal y del buffer. Estos antecedentes motivan el estudio de mecanismos cliente de adaptaciÃ³n de bitrate en escenarios de vÃ­deo sobre HTTP.
```

## Copyright/figure rule

Do not copy figures from these papers into the thesis or repository.

Instead create original diagrams later:
- progressive download: initial burst + throttling;
- mobile terminal buffer thresholds;
- transition from traffic characterization to DASH ABR.

## Implementation non-goals

- Do not implement a YouTube traffic generator.
- Do not implement Android dual-threshold policy.
- Do not change DashClientModular4 to mobile/3G-specific behavior.
- Do not alter baseline order.
- Do not add traces/replay/benchmark now.