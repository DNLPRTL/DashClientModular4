# Hardening Step 14: Client Readiness Certification

Fecha: 2026-05-12

## Por que existe

Block 13 documento acceptance, provenance y roadmap. Block 14 es la puerta tecnica final: comprueba que el cliente esta preparado para recibir futuros baselines sin arrastrar nombres legacy como canonicos, sin inventar metricas y sin confundir demos con benchmarks.

## Diferencia frente a Block 13

- Block 13 fue auditoria/documentacion semantica.
- Block 14 anade contrato de entrada para baselines, catalogo de metricas, script objetivo de readiness, tests de flujo fake y reporte final.

## Que se audito

- `main.py`, `player.py`, `progress_bar.py`;
- config/run context/artifacts/schema;
- feedback runtime y contrato de controladores;
- fixed/scripted/max_quality;
- downloader/parser;
- fake/GStreamer engines;
- docs/runbooks/tests;
- terminos legacy y claims prematuros.

## Que se limpio

- Se centralizo la lista real de feedback keys.
- Se agregaron aliases canonicos y clasificacion de legacy keys.
- Se hizo import-safe `progress_bar.py` sin requerir Tkinter en checks headless.
- Se agrego contrato y reporte de readiness.

No se cambiaron formulas de metricas, ABR decisions ni semantica de reproduccion.

## Readiness script

`scripts/check_client_readiness.py` valida:

- docs requeridos;
- imports requeridos;
- constantes de artefactos canonicos;
- boundaries de nombres legacy;
- cobertura de columnas en provenance/catalogo;
- metadata de benchmark neutrality;
- contrato de entrada para baselines;
- consola/progreso como diagnostico humano;
- frontera GStreamer;
- roadmap GUI;
- ausencia de claims prematuros positivos.

## Por que es la puerta final de Phase 1

Tras este bloque, el repositorio no solo pasa tests: tambien tiene una puerta reproducible que falla si se pierden contratos clave. Eso permite cerrar Phase 1 como base tecnica, no como benchmark final.

## Fuera de Phase 1

- Baselines ABR academicos.
- AI/PPO/training.
- QoE/reward final.
- Trace/replay infrastructure.
- Benchmark scripts finales.
- GUI/frontend.
- GStreamer benchmark-grade.

## Validacion

```powershell
git status --short --branch
git rev-parse --short HEAD
git log --oneline -5
git diff --check
python -m unittest discover
python -m py_compile main.py player.py progress_bar.py core\client_config.py core\controller\registry.py core\controller\base.py core\controller\contract.py core\controller\fixed_quality.py core\controller\scripted_quality.py core\controller\max_quality_controller.py core\run_context.py core\runtime_feedback.py core\dataset_schema.py core\benchmark_contract.py core\output_artifacts.py core\media_engine\base.py core\media_engine\fake.py core\media_engine\gst_media_engine.py scripts\check_environment.py scripts\check_client_readiness.py
python scripts\check_environment.py --profile dev
python scripts\check_environment.py --profile gst
python scripts\check_client_readiness.py
python scripts\check_client_readiness.py --strict
```
