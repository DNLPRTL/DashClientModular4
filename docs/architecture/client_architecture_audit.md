# Auditoria de arquitectura del cliente

Fecha: 2026-05-12

Commit auditado inicialmente: `8334adb`.

Objetivo: certificar si DashClientModular4 esta listo como base tecnica estable para volver a Phase 0 y, mas tarde, implementar baselines ABR sin contaminar salidas, metricas ni contrato de controlador.

## Resumen de arquitectura actual

La cadena actual es:

`config YAML -> main.py -> ClientConfig/RunContext -> DashParser -> controller registry -> Player -> SegmentDownloader -> media engine fake/gst -> CSV/manifest/log`

El cliente ya separa suficientemente las responsabilidades principales para cerrar Phase 1 como base tecnica, con cautelas documentadas:

- `fake` es la ruta controlada para tests y trabajo futuro de replay/control.
- `gst` es integracion/demo, no benchmark-grade.
- Los controladores actuales son test/debug o legacy.
- Los CSV son artefactos de validacion/evaluacion, no tablas finales de resultados.
- El contrato de entrada a baselines queda documentado, pero la metodologia academica sigue en Phase 0.

## Tabla de readiness

| Area/modulo | Responsabilidad | Estado | Evidencia actual | Accion en Block 14 | Riesgo restante | Bloquea cierre Phase 1? |
|---|---|---|---|---|---|---|
| `main.py` | Runner config-driven, creacion de controller/downloader/parser/engine y manifest status. | PASS | Usa `ClientConfig`, `create_run_context`, registry y `Player`. | Auditado; sin cambio de codigo. | `_run_legacy_analysis` sigue como ruta opcional separada. | No |
| `player.py` | Bucle de descarga/reproduccion, feedback, CSV, fases y stalls agregados. | WARN | Sigue concentrando logica de pacing, warm-up, retry y CSV. | Auditado y cubierto por tests de flujo fake. | Refactor fino pendiente antes de benchmarks complejos. | No |
| `progress_bar.py` | UI Tk humana opcional. | PASS | Muestra progreso y senales humanas; no escribe artefactos. | Import de Tkinter hecho opcional; etiqueta `BW` ya no es principal. | Solo demo local; no autoridad experimental. | No |
| `core.client_config` | Configuracion, defaults y compatibilidad de nombres antiguos. | PASS | Normaliza `dataset_filename` y nombres legacy a artefactos canonicos. | Auditado. | Compatibilidad legacy debe mantenerse clasificada. | No |
| `core.run_context` | Directorio de run, manifest, config resuelta, entorno. | PASS | Manifest usa claves canonicas y `benchmark_neutrality`. | Auditado por readiness script. | Ninguno bloqueante. | No |
| `core.output_artifacts` | Constantes canonicas y nombres legacy. | PASS | Define `segment_telemetry.csv`, `evaluation_segments.csv` y legacy tuple. | Auditado. | Legacy solo compatibilidad. | No |
| `core.dataset_schema` | Headers CSV y validacion de filas. | PASS | Headers unicos y builders existentes. | Se anadio fuente default real de feedback keys y builder default. | Nuevos campos de controladores futuros deben documentarse. | No |
| `core.benchmark_contract` | Fases y gates neutrales. | PASS | `eval_phase`, `use_for_eval`, stall classes. | Auditado. | Event-level stall telemetry pendiente. | No |
| `core.runtime_feedback` | Construccion del payload dict al controlador. | PASS | Devuelve claves en orden contractual. | Ahora usa `CURRENT_FEEDBACK_KEYS` como orden canonico. | API dict conserva nombres legacy. | No |
| contrato/base/registry | API de controladores y registro. | PASS | `TARGET_RATE_UNIT`, quantizer y registry limitados. | Se agregaron aliases canonicos y estado semantico. | API futura puede migrar a objeto tipado. | No |
| `fixed_quality` | Controlador determinista fijo. | PASS | Clamp por ladder y `max_level`. | Auditado. | No es baseline academico. | No |
| `scripted_quality` | Controlador determinista por `segment_index`. | PASS | Secuencia reproducible de niveles. | Auditado. | No es baseline academico. | No |
| `max_quality_controller` | Legacy/debug/stress. | WARN | Selecciona maximo nivel y loguea `bwe`. | Clasificado en docs/contrato. | Nombre `MaxQuality` y metricas debug historicas. | No |
| downloader | Descarga completa con retries e info de timing. | WARN | No hace streaming ni abortos; mide `elapsed_total`. | Auditado, no cambiado. | Metodologia de retries/throughput pendiente. | No |
| parser | MPD DASH a representaciones/segmentos. | WARN | Soporta SegmentList, SegmentTemplate, SegmentBase/SIDX basico. | Auditado, no cambiado. | Flatten de adaptation sets y compatibilidad codec deben revisarse antes de benchmarks. | No |
| fake media engine | Reproduccion simulada controlada con eventos. | PASS | No requiere red/GST/display y emite eventos. | Cubierto por tests de flujo. | No sustituye metodologia de red final. | No |
| GStreamer media engine | Integracion con pipeline real. | WARN | Import-safe y diagnosticos mejorados. | Boundary verificado por readiness script. | No benchmark-grade; timing no comparable. | No |
| environment check | Validacion dev/gst/analysis. | PASS | `dev` requerido, `gst` opcional/strict. | Auditado. | GST strict depende de Ubuntu preparado. | No |
| run docs/tests | Documentacion y guardrails. | PASS | Docs Phase 1, provenance, output contract, runbooks. | Se agregan audit, baseline contract, report y readiness script. | Mantener docs sincronizados al anadir baselines. | No |

## Conceptos antiguos detectados

- `dataset.csv` y `dataset_training.csv`: DEPRECATED COMPATIBILITY. No son salidas canonicas.
- `dataset_filename`: DEPRECATED COMPATIBILITY en config; se normaliza.
- `bwe`: DEPRECATED COMPATIBILITY dentro del feedback; alias canonico `measured_download_rate`.
- `cur_bitrate`, `max_bitrate`, `min_bitrate`: DEPRECATED COMPATIBILITY; valores en bytes/s, alias a tasas de representacion.
- `training dataset`: permitido solo para negar que exista dataset final.
- `benchmark-grade`: permitido para explicar que GST no lo es.
- `FIX`/comentarios historicos en parser/fake: WARN no bloqueante; describen correcciones previas.

No se detectaron `TraceLab` ni `abr_rl` como arquitectura actual.

## Contaminacion potencial de metricas

El riesgo principal sigue en `Player`, porque todavia centraliza pacing, warm-up, retry local, escritura de CSV y stalls agregados. Block 14 no reescribe esa logica para no cambiar semantica. La mitigacion es documental y contractual: futuros baselines no deben tocar ese codigo para favorecer decisiones, y cualquier cambio de comportamiento debe tener tests y reporte propio.

## Veredicto

No hay FAIL bloqueante para cerrar Phase 1 como base tecnica. Quedan WARN metodologicos que pertenecen a Phase 0 o fases posteriores.
