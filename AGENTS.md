# AGENTS.md

Guía de trabajo para DashClientModular4.

## FASE 1 — Hardening total del cliente

Objetivo: dejar el cliente DASH limpio, robusto, modular y preparado para implementar controladores ABR sin deuda técnica.

## Principios

1. Mantener el cliente limpio, modular y testeable.
2. No introducir controladores ABR definitivos hasta que el reproductor base esté estable.
3. No meter vídeos, segmentos DASH ni ficheros pesados en el repositorio.
4. Separar claramente:
   - parser MPD
   - descarga de segmentos
   - buffer
   - motor de reproducción
   - control ABR
   - logging
   - evaluación
5. Todo cambio importante debe tener commit propio.
