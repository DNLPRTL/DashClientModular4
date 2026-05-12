# Catalogo de metricas y senales

Fecha: 2026-05-12

Este catalogo complementa `telemetry_column_provenance.md`. Usa las claves reales exportadas por el repositorio: `CURRENT_FEEDBACK_KEYS` en `core.controller.contract` y `DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS` en `core.dataset_schema`.

No define QoE final, reward final ni benchmark final.

## Tabla principal

| Nombre | Artefacto/API | Producer module/function | Consumidor | Unidad | Formula/fuente | Evento de actualizacion | Categoria | Futuro baseline puede usarlo? | Benchmark output ahora? | Decision | Razon |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `segment_index` | CSV/API | `Player.run`, `build_controller_feedback` | Player/tests/futuros controladores | index | indice actual | fila/feedback | player runtime state | Si | No | keep | Identidad de segmento. |
| `timestamp` | CSV | `time.time()` | auditoria humana | unix_seconds | reloj wall-clock | escritura fila | debug/test only | No | No | keep | Trazabilidad no scoring. |
| `feedback_queued_bytes` | CSV/API | media engine | controladores | bytes | bytes en cola | feedback | controller input | Con cautela | No | keep | Depende del engine. |
| `feedback_queued_time` | CSV/API | media engine | controladores | seconds | segundos en cola | feedback | controller input | Si | No | keep | Senal principal de buffer. |
| `feedback_cur_bitrate` | CSV/API | runtime_feedback | controladores legacy | bytes_per_second | `rates[cur_level]` | feedback | deprecated compatibility | Si con alias | No | deprecate | Nombre ambiguo. |
| `feedback_bwe` | CSV/API | runtime_feedback | controladores legacy | bytes_per_second | `last_size/last_time` o fallback a tasa actual | feedback | deprecated compatibility | Con cautela | No | deprecate | Alias canonico `measured_download_rate`. |
| `feedback_level` | CSV/API | Player | controladores | representation_index | nivel actual | feedback | controller input | Si | No | keep | Estado de seleccion. |
| `feedback_max_level` | CSV/API | Player | controladores | representation_index | max index | feedback | controller input | Si | No | keep | Limite de seguridad. |
| `feedback_cur_rate` | CSV/API | runtime_feedback | controladores | bytes_per_second | `rates[cur_level]` | feedback | deprecated compatibility | Si con alias | No | deprecate | Duplicado de tasa actual. |
| `feedback_max_rate` | CSV/API | runtime_feedback | controladores | bytes_per_second | `max(rates)` | feedback | controller input | Si | No | keep | Contexto ladder. |
| `feedback_min_rate` | CSV/API | runtime_feedback | controladores | bytes_per_second | `min(rates)` | feedback | controller input | Si | No | keep | Contexto ladder. |
| `feedback_max_bitrate` | CSV/API | runtime_feedback | controladores legacy | bytes_per_second | `max(rates)` | feedback | deprecated compatibility | Si con alias | No | deprecate | Nombre historico. |
| `feedback_min_bitrate` | CSV/API | runtime_feedback | controladores legacy | bytes_per_second | `min(rates)` | feedback | deprecated compatibility | Si con alias | No | deprecate | Nombre historico. |
| `feedback_last_fragment_size` | CSV/API | downloader/player | controladores | bytes | tamano ultimo segmento | tras descarga | downloader measurement | Con cautela | No | keep | Retry semantics pendientes. |
| `feedback_last_download_time` | CSV/API | downloader/player | controladores | seconds | `elapsed_total` o wall time local | tras descarga | downloader measurement | Con cautela | No | keep | Definicion de throughput pendiente. |
| `feedback_downloaded_bytes` | CSV/API | Player | diagnostico | bytes | acumulado media | tras descarga | player runtime state | Raramente | No | keep | Progreso runtime. |
| `feedback_fragment_duration` | CSV/API | parser/player | controladores | seconds | duracion segmento | feedback | controller input | Si | No | keep | Contexto de segmento. |
| `feedback_rates` | CSV/API | MPD/parser/player | controladores | bytes_per_second_list | ladder ordenada | feedback | controller input | Si | No | keep | Base de cuantizacion. |
| `feedback_segment_index` | CSV/API | Player | controladores | index | indice actual | feedback | controller input | Si | No | keep | Estado reproducible. |
| `feedback_start_segment_request` | CSV/API | Player | diagnostico | perf_counter_seconds | inicio request | feedback | debug/test only | No | No | keep | Timing local. |
| `feedback_stop_segment_request` | CSV/API | Player | diagnostico | perf_counter_seconds | fin request | feedback | debug/test only | No | No | keep | Timing local. |
| `is_init` | CSV | Player | evaluacion futura | boolean_int | tipo segmento | fila | evaluation gate | No | No | keep | Exclusion de init. |
| `retry_count` | CSV | Player retry loop | auditoria | count | reintentos Player | fila | pending methodology | No | No | keep | Tratamiento pendiente. |
| `segment_start_time` | CSV | Player | auditoria | perf_counter_seconds | inicio local | descarga | debug/test only | No | No | keep | Runtime trace. |
| `segment_end_time` | CSV | Player | auditoria | perf_counter_seconds | fin local | descarga | debug/test only | No | No | keep | Runtime trace. |
| `wall_time_elapsed` | CSV | Player | fases | seconds | `perf_now-start` | fila | pending methodology | No | No | keep | Startup/QoE pendiente. |
| `tp_now` | CSV | `_compute_derived_features` | auditoria futura | bytes_per_second | size/time | fila | pending methodology | Con cautela | No | keep | Formula conocida, uso final no. |
| `tp_ewma` | CSV | `_compute_derived_features` | auditoria futura | bytes_per_second | EWMA alpha 0.6 | fila | pending methodology | Con cautela | No | keep | Estimador no final. |
| `tp_min_last5` | CSV | `_compute_derived_features` | auditoria futura | bytes_per_second | min ventana 5 | fila | pending methodology | Con cautela | No | keep | Ventana no final. |
| `tp_std_last5` | CSV | `_compute_derived_features` | auditoria futura | bytes_per_second | std ventana 5 | fila | pending methodology | Con cautela | No | keep | Ventana no final. |
| `buffer_over_seg` | CSV | `_compute_derived_features` | auditoria futura | ratio | buffer/duracion | fila | pending methodology | Con cautela | No | keep | Feature candidata. |
| `headroom` | CSV | `_compute_derived_features` | auditoria futura | ratio | tp_now/cur_rate | fila | pending methodology | Con cautela | No | keep | Feature candidata. |
| `is_upswitch` | CSV | `_update_pending_policy_and_switch` | evaluacion futura | boolean_int | nivel sube | decision | pending methodology | No | No | keep | Penalizacion pendiente. |
| `is_downswitch` | CSV | `_update_pending_policy_and_switch` | evaluacion futura | boolean_int | nivel baja | decision | pending methodology | No | No | keep | Penalizacion pendiente. |
| `switch_magnitude` | CSV | `_update_pending_policy_and_switch` | evaluacion futura | levels | delta abs | decision | pending methodology | No | No | keep | Penalizacion pendiente. |
| `phase_raw` | CSV | `_PhaseDetector` | diagnostico | label | detector buffer | fila | debug/test only | No | No | keep | No fase academica. |
| `phase_smooth` | CSV | `_PhaseDetector` | diagnostico | label | smoothing buffer | fila | debug/test only | No | No | keep | No fase academica. |
| `policy_name` | CSV | Player/controller | auditoria | label | nombre controlador | fila | debug/test only | No | No | keep | Identidad runtime. |
| `policy_target_rate` | CSV | controlador | auditoria | bytes_per_second | accion devuelta | decision | pending methodology | No | No | keep | Trace de decision. |
| `policy_chosen_level` | CSV | quantizer | auditoria | representation_index | nivel cuantizado | decision | pending methodology | No | No | keep | Trace de decision. |
| `policy_decision_ms` | CSV | Player | auditoria | milliseconds | tiempo calcControlAction | decision | debug/test only | No | No | keep | Timing local. |
| `eval_phase` | CSV | benchmark_contract | evaluacion | label | clasificacion neutral | fila | evaluation gate | No | No | keep | Gate, no score. |
| `is_preroll` | CSV | Player | auditoria | boolean_int | `elapsed < PREROLL_SECONDS` | fila | pending methodology | No | No | keep | Usar `eval_phase` como gate. |
| `use_for_eval` | CSV | benchmark_contract | evaluacion | boolean_int | phase==steady_state y no init | fila | evaluation gate | No | No | keep | Gate, no score. |
| `stall_flag` | CSV | media events/Player | auditoria | boolean_int | agregado por segmento | flush fila | media engine event | No | No | keep | No QoE final. |
| `stall_duration` | CSV | media events/Player | auditoria | seconds | duracion agregada | flush fila | media engine event | No | No | keep | No contar drain terminal. |
| `last_fragment_size` | `evaluation_segments.csv` | Player | evaluacion futura | bytes | copia compacta | fila | downloader measurement | Con cautela | No | keep | No training final. |
| `last_download_time` | `evaluation_segments.csv` | Player | evaluacion futura | seconds | copia compacta | fila | downloader measurement | Con cautela | No | keep | No throughput final. |
| `fragment_duration` | `evaluation_segments.csv` | Player | evaluacion futura | seconds | copia compacta | fila | controller input | Si | No | keep | Contexto. |

## Parametros runtime relevantes

| Parametro | Donde aparece | Unidad | Estado | Decision |
|---|---|---:|---|---|
| `playback.initial_quality` | config/player | representation_index | runtime config | keep |
| `playback.initial_controller_decision` | config/player | boolean | compatibilidad legacy | keep documented |
| `playback.max_buffer_seconds` | config/player | seconds | runtime policy | keep |
| `playback.drain_buffer_sleep_seconds` | config/player | seconds | runtime policy | keep |
| `playback.preroll_seconds` | config/player | seconds | pending methodology | keep |
| `media_engine.min_queue_time` | config/media engines | seconds | runtime policy | keep |
| `downloader.max_retries` | config/downloader | count | runtime policy | keep |

Ninguna de estas senales es resultado final de benchmark en Phase 1.
