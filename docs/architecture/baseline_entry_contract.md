# Contrato de entrada para futuros baselines ABR

Fecha: 2026-05-12

Este documento responde a la pregunta: si despues de Phase 0 se implementan BBA, BOLA, MPC, rate-based u otros baselines, que proporciona el cliente al controlador, que debe devolver el controlador y que no debe tocarse.

Este contrato no implementa baselines. Tampoco define QoE final, reward final, trazas ni scripts de benchmark.

## Frases de puerta

- target rates are bytes per second.
- quality levels are representation indices.
- representation ladder source is MPD.
- fixed_quality and scripted_quality are test/debug only.
- max_quality is legacy/debug/stress.
- current dict-based API.
- legacy keys are classified.
- must not depend on console output.

## Ciclo de vida del controlador

1. `main.py` carga `ClientConfig`, valida la configuracion y crea un `RunContext`.
2. `core.controller.registry.create_controller()` instancia el controlador por nombre.
3. `Player` construye feedback con `core.runtime_feedback.build_controller_feedback()`.
4. `Player` llama a `controller.setPlayerFeedback(feedback_dict)`.
5. Cuando toca decidir, `Player` llama a `controller.calcControlAction()`.
6. El controlador devuelve una tasa objetivo en bytes por segundo.
7. `Player` llama a `controller.quantizeRate(target_rate)` para mapear la tasa al indice de representacion.
8. `Player` descarga el siguiente segmento del nivel seleccionado.

El controlador no descarga segmentos, no parsea MPD, no escribe CSV, no calcula `eval_phase`, no clasifica stalls y no decide que filas son benchmark-elegibles.

## Registro de controladores

El registro actual esta en `core/controller/registry.py`:

| Nombre | Estado | Uso permitido |
|---|---|---|
| `min_rate` | sanity/control | Seleccionar siempre la representacion minima; valida contrato, registro y fake smoke sin claim academico. |
| `fixed_rate` | sanity/control | Seleccionar nivel/tasa fija configurada y clampada a la ladder; valida parametros y unidades. |
| `max_rate` | sanity/control | Seleccionar siempre la representacion maxima permitida; valida contrato y ruta de maximo nivel sin usar `max_quality` legacy. |
| `rate_based` | academic baseline | Primer baseline ABR academico implementado; selecciona la representacion mas alta bajo una estimacion conservadora de throughput de aplicacion. |
| `bba` | academic baseline | Segundo baseline ABR academico implementado; selecciona representacion mediante mapa de buffer reservoir/cushion. |
| `bola` | academic baseline | Tercer baseline ABR academico implementado; selecciona representacion mediante score BOLA-basic de buffer, utilidad y tamano de segmento. |
| `fixed_quality` | test/debug | Smoke tests, invariantes de ruta, validacion determinista. |
| `scripted_quality` | test/debug | Trazas deterministas de cambio de nivel. |
| `max_quality` | legacy/debug/stress | Estresar la ruta de seleccion maxima; no comparar academicamente. |

`min_rate`, `fixed_rate` y `max_rate` son controles tecnicos de cordura. No son baselines academicos y sus smoke tests no son resultados de benchmark.

`rate_based` se registra despues de cerrar su paper card, source evidence, implementation spec, API mapping, acceptance tests y notes for memory. Usa throughput de capa de aplicacion (`bwe` o `last_fragment_size / last_download_time`) y puede usar `queued_time` solo como guardia de seguridad. No usa TCP RTT, packet loss, congestion window, estado de servidor, oraculos externos, consola ni QoE final.

`bba` se registra despues de cerrar su paper card, source evidence, implementation spec, API mapping, acceptance tests y notes for memory. Usa `queued_time` como senal primaria de buffer y los parametros `reservoir_s` y `cushion_s` para mapear el buffer a una representacion. No usa throughput como regla primaria, ni TCP RTT, packet loss, congestion window, estado de servidor, oraculos externos, consola ni QoE final.

`bola` se registra despues de cerrar su paper card, source evidence, implementation spec, API mapping, acceptance tests y notes for memory. Usa `queued_time`, `fragment_duration`, `rates`, utilidad logaritmica interna y tamano de segmento exacto si se proporciona o aproximado como `rate * fragment_duration`. No requiere prediccion explicita de throughput, no implementa DYNAMIC, FAST SWITCHING, BOLA-E ni comportamiento completo de dash.js, y no define QoE final.

Futuros baselines academicos deben registrarse aqui cuando sus papers, evidencias, especificaciones, mappings y tests esten cerrados. El nombre del controlador en el manifest identifica la ejecucion, pero no convierte al controlador en baseline academico por si mismo.

## API actual

La API actual es una current dict-based API por compatibilidad:

- `setPlayerFeedback(feedback_dict)`: recibe el ultimo estado del reproductor.
- `calcControlAction()`: devuelve una tasa objetivo en bytes por segundo.
- `getControlAction()`: expone la ultima accion.
- `quantizeRate(rate)`: convierte tasa objetivo a indice de representacion.
- `getIdleDuration()`: devuelve espera adicional del controlador.

`core/controller/contract.py` contiene `CONTROLLER_CONTRACT_VERSION`, `CURRENT_FEEDBACK_KEYS`, `FEEDBACK_UNITS`, `FEEDBACK_CANONICAL_ALIASES`, `FEEDBACK_SEMANTIC_STATUS`, `TARGET_RATE_UNIT` y `QUALITY_LEVEL_UNIT`.

## Campos de feedback

| Campo actual | Alias canonico futuro | Unidad | Productor | Categoria | Estable para baselines futuros? | Notas |
|---|---|---|---|---|---|---|
| `queued_bytes` | `buffer_bytes_estimate` | bytes | media engine | estado runtime | Con cautela | Depende del motor; no comparar fake/GST como equivalentes. |
| `queued_time` | `buffer_seconds` | seconds | media engine | estado runtime | Si | Senal principal de buffer; la metodologia debe definir como se usa. |
| `cur_bitrate` | `representation_rate` | bytes_per_second | Player ladder | deprecated compatibility | Si, preferir alias | Nombre historico: no son bits/s. |
| `bwe` | `measured_download_rate` | bytes_per_second | runtime_feedback | deprecated compatibility | Con cautela | Size/time del ultimo segmento o fallback a tasa actual; no es estimador final. |
| `level` | `selected_level` | representation_index | Player | input controlador | Si | Indice actual en la ladder ordenada por tasa. |
| `max_level` | `max_selectable_level` | representation_index | Player | input controlador | Si | Limite superior del MPD actual. |
| `cur_rate` | `representation_rate` | bytes_per_second | Player ladder | deprecated compatibility | Si, preferir alias | Duplicado de `cur_bitrate`. |
| `max_rate` | `max_representation_rate` | bytes_per_second | MPD ladder | input controlador | Si | Contexto de ladder. |
| `min_rate` | `min_representation_rate` | bytes_per_second | MPD ladder | input controlador | Si | Contexto de ladder. |
| `max_bitrate` | `max_representation_rate` | bytes_per_second | MPD ladder | deprecated compatibility | Si, preferir alias | Duplicado historico. |
| `min_bitrate` | `min_representation_rate` | bytes_per_second | MPD ladder | deprecated compatibility | Si, preferir alias | Duplicado historico. |
| `last_fragment_size` | `last_fragment_size_bytes` | bytes | downloader/player | medicion descarga | Con cautela | Tratamiento de retries pendiente de metodologia. |
| `last_download_time` | `last_download_time_seconds` | seconds | downloader/player | medicion descarga | Con cautela | Tiempo total reportado por downloader. |
| `downloaded_bytes` | `downloaded_media_bytes_total` | bytes | Player | estado runtime | No como decision principal | Contador acumulado de medios descargados. |
| `fragment_duration` | `segment_duration_seconds` | seconds | parser/player | contexto MPD | Si | Duracion del segmento actual. |
| `rates` | `representation_rates` | bytes_per_second_list | MPD ladder | input controlador | Si | Lista ordenada por tasa. |
| `segment_index` | `segment_index` | index | Player | estado runtime | Si | Indice en la secuencia comun actual. |
| `start_segment_request` | `segment_request_start_perf_counter_seconds` | perf_counter_seconds | Player | timing runtime | No para benchmark | Diagnostico local. |
| `stop_segment_request` | `segment_request_stop_perf_counter_seconds` | perf_counter_seconds | Player | timing runtime | No para benchmark | Diagnostico local. |

## Que puede usar un baseline futuro

Un baseline puede depender de:

- `rates` / `representation_rates` como ladder de representaciones del MPD;
- `level` / `selected_level` como indice actual;
- `max_level` como limite de seguridad;
- `queued_time` / `buffer_seconds` como estado de buffer;
- `last_fragment_size` y `last_download_time` para estimar throughput, si su paper lo justifica;
- `fragment_duration` para logica basada en duracion de segmento;
- `segment_index` para estado interno reproducible.

Un baseline no debe depender de:

- texto de consola, Tk/progress bar o `run.log`;
- orden accidental de prints;
- `phase_raw` o `phase_smooth` como fase academica;
- `stall_flag` o `stall_duration` como QoE final;
- eventos internos de GStreamer como si fueran rebuffering final;
- salidas fake y GST mezcladas como datos equivalentes.

## Seleccion de nivel

El controlador devuelve `target_rate` en bytes por segundo. `BaseController.quantizeRate()` usa `core.controller.contract.quantize_rate_to_level()`:

- normaliza la ladder;
- exige tasas numericas positivas;
- selecciona el mayor indice cuya tasa sea menor o igual que `target_rate`;
- devuelve un indice de representacion.

El orden de representaciones lo prepara `Player` a partir del MPD y se ordena por `bandwidth`. La equivalencia entre codecs/adaptation sets queda como riesgo metodologico documentado: no bloquea Phase 1, pero debe revisarse antes de benchmarks formales con contenido heterogeneo.

## Limites para no contaminar metricas

Un baseline futuro:

- no debe escribir directamente `segment_telemetry.csv` ni `evaluation_segments.csv`;
- no debe cambiar `eval_phase` ni `use_for_eval`;
- no debe ocultar stalls ni reescribir resultados;
- no debe modificar el downloader, parser, media engine o run context para favorecer un algoritmo;
- debe registrar parametros en config/manifest;
- debe tener tests deterministas propios;
- debe declarar el paper/spec que implementa.

## Estado de entrada

Con Block 14, la entrada tecnica para baselines queda preparada como contrato. La implementacion de baselines sigue bloqueada hasta Phase 0, porque faltan decisiones de literatura, metodologia, QoE/reward y entorno experimental.
