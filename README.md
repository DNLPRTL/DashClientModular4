# DashClientModular4

Cliente DASH modular para el TFG.

## Objetivo

Crear un reproductor DASH robusto, limpio y preparado para comparar controladores ABR clásicos y basados en IA/RL.

## Estructura principal

- core/controller: controladores ABR.
- core/media_engine: motor de reproducción.
- core/parser: parser MPD y lógica DASH.
- core/utils: utilidades comunes.
- config: configuración del cliente.
- docs: arquitectura, investigación y runbooks.
- scripts: scripts de setup, smoke tests y evaluación.
- tests: pruebas automáticas.

## Decisión importante

Los vídeos DASH, segmentos y ficheros pesados no deben meterse en este repositorio.

El contenido DASH vive fuera del repo.
