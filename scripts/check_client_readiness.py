#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_DOCS = (
    "docs/architecture/phase1_acceptance.md",
    "docs/architecture/telemetry_column_provenance.md",
    "docs/architecture/runtime_console_output_contract.md",
    "docs/architecture/output_artifact_contract.md",
    "docs/architecture/client_architecture_audit.md",
    "docs/architecture/baseline_entry_contract.md",
    "docs/architecture/client_readiness_report.md",
    "docs/architecture/hardening_step_14_client_readiness.md",
    "docs/runbooks/gstreamer_playback.md",
    "docs/roadmap/gui_frontend_dashboard.md",
)

REQUIRED_IMPORTS = (
    "main",
    "player",
    "progress_bar",
    "core.client_config",
    "core.run_context",
    "core.output_artifacts",
    "core.dataset_schema",
    "core.benchmark_contract",
    "core.runtime_feedback",
    "core.controller.contract",
    "core.controller.registry",
    "core.controller.fixed_quality",
    "core.controller.scripted_quality",
    "core.controller.max_quality_controller",
    "core.media_engine.fake",
    "core.media_engine.gst_media_engine",
    "scripts.check_environment",
)

CURRENT_DOCS = (
    "README.md",
    "docs/architecture/phase1_acceptance.md",
    "docs/architecture/output_artifact_contract.md",
    "docs/architecture/telemetry_column_provenance.md",
    "docs/architecture/runtime_console_output_contract.md",
    "docs/architecture/client_architecture_audit.md",
    "docs/architecture/baseline_entry_contract.md",
    "docs/architecture/client_readiness_report.md",
    "docs/architecture/hardening_step_14_client_readiness.md",
    "docs/architecture/phase1_status.md",
    "docs/runbooks/environment.md",
    "docs/runbooks/gstreamer_playback.md",
    "docs/runbooks/run_client.md",
    "docs/runbooks/run_layout.md",
    "docs/roadmap/gui_frontend_dashboard.md",
)

FORBIDDEN_POSITIVE_CLAIMS = (
    "final benchmark exists",
    "final qoe exists",
    "final reward exists",
    "final training dataset exists",
    "academic baselines are implemented",
    "ai controller is implemented",
)

STRICT_ALLOWED_WARN_CODES = frozenset()


@dataclass
class Result:
    status: str
    code: str
    message: str


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check DashClientModular4 client-readiness gate.")
    parser.add_argument("--strict", action="store_true", help="Fail on any non-allowlisted warning.")
    args = parser.parse_args(argv)
    return run_checks(strict=args.strict)


def run_checks(strict: bool = False, stream: Optional[TextIO] = None) -> int:
    if stream is None:
        stream = sys.stdout
    _ensure_repo_on_path()

    checks: Sequence[Callable[[], List[Result]]] = (
        check_required_docs,
        check_required_imports,
        check_artifact_constants,
        check_legacy_artifact_boundaries,
        check_telemetry_provenance,
        check_benchmark_neutrality,
        check_controller_baseline_entry,
        check_runtime_console_contract,
        check_gstreamer_boundary,
        check_gui_boundary,
        check_forbidden_premature_claims,
    )

    results: List[Result] = []
    for check in checks:
        results.extend(check())

    oks = [r for r in results if r.status == "OK"]
    warns = [r for r in results if r.status == "WARN"]
    fails = [r for r in results if r.status == "FAIL"]
    unallowlisted_warns = [r for r in warns if r.code not in STRICT_ALLOWED_WARN_CODES]

    _write(stream, "DashClientModular4 client readiness check")
    _write(stream, "Strict: {0}".format("yes" if strict else "no"))
    _write(stream, "")
    for result in results:
        _write(stream, "{0:<4} {1}: {2}".format(result.status, result.code, result.message))
    _write(stream, "")
    _write(stream, "Summary")
    _write(stream, "OK: {0}  WARN: {1}  FAIL: {2}".format(len(oks), len(warns), len(fails)))

    if warns:
        _write(stream, "Warnings:")
        for result in warns:
            _write(stream, "- {0}: {1}".format(result.code, result.message))
    if fails:
        _write(stream, "Failures:")
        for result in fails:
            _write(stream, "- {0}: {1}".format(result.code, result.message))

    if fails:
        _write(stream, "Verdict: FAIL")
        return 1
    if strict and unallowlisted_warns:
        _write(stream, "Verdict: FAIL (strict warnings)")
        return 2

    _write(stream, "Verdict: PASS")
    return 0


def check_required_docs() -> List[Result]:
    results = []
    for relative_path in REQUIRED_DOCS:
        path = REPO_ROOT / relative_path
        if path.is_file():
            results.append(Result("OK", "doc_exists", relative_path))
        else:
            results.append(Result("FAIL", "doc_missing", relative_path))
    return results


def check_required_imports() -> List[Result]:
    results = []
    for module_name in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module_name)
            results.append(Result("OK", "import", module_name))
        except Exception as exc:
            results.append(Result("FAIL", "import_failed", "{0}: {1}".format(module_name, _format_exc(exc))))
    return results


def check_artifact_constants() -> List[Result]:
    from core import output_artifacts

    expected = {
        "SEGMENT_TELEMETRY_FILENAME": "segment_telemetry.csv",
        "EVALUATION_SEGMENTS_FILENAME": "evaluation_segments.csv",
        "RUN_MANIFEST_FILENAME": "run_manifest.json",
        "RESOLVED_CONFIG_FILENAME": "config.resolved.json",
        "ENVIRONMENT_FILENAME": "environment.json",
        "RUN_LOG_FILENAME": "run.log",
    }
    results = []
    for name, expected_value in expected.items():
        actual = getattr(output_artifacts, name, None)
        if actual == expected_value:
            results.append(Result("OK", "artifact_constant", "{0}={1}".format(name, actual)))
        else:
            results.append(Result("FAIL", "artifact_constant", "{0} expected {1}, got {2}".format(name, expected_value, actual)))

    canonical_keys = set(output_artifacts.CANONICAL_OUTPUT_KEYS)
    if {"dataset", "training"} & canonical_keys:
        results.append(Result("FAIL", "artifact_keys", "legacy dataset/training key is canonical"))
    else:
        results.append(Result("OK", "artifact_keys", "manifest keys are canonical"))
    return results


def check_legacy_artifact_boundaries() -> List[Result]:
    from core.client_config import ClientConfig
    from core.output_artifacts import LEGACY_OUTPUT_FILENAMES
    from core.run_context import create_run_context

    results = []
    if tuple(LEGACY_OUTPUT_FILENAMES) == ("dataset.csv", "dataset_training.csv"):
        results.append(Result("OK", "legacy_artifact_names", "legacy names are explicit compatibility names"))
    else:
        results.append(Result("FAIL", "legacy_artifact_names", "unexpected legacy artifact tuple"))

    with tempfile.TemporaryDirectory() as tmp:
        config = ClientConfig.from_dict(
            {
                "mpd_url": "memory://readiness.mpd",
                "output": {
                    "root_dir": tmp,
                    "segment_telemetry_filename": "dataset.csv",
                    "evaluation_segments_filename": "dataset_training.csv",
                },
            },
            source_path="<readiness>",
        )
        context = create_run_context(config, command_args=["readiness"])
        if context.segment_telemetry_path.name == "segment_telemetry.csv" and context.evaluation_segments_path.name == "evaluation_segments.csv":
            results.append(Result("OK", "legacy_artifact_defaults", "legacy output filenames normalize to canonical names"))
        else:
            results.append(Result("FAIL", "legacy_artifact_defaults", "legacy output filenames were preserved in run context"))

    for relative_path in CURRENT_DOCS:
        path = REPO_ROOT / relative_path
        if not path.exists():
            continue
        text = _read_lower(path)
        if "dataset.csv" in text or "dataset_training.csv" in text:
            if "deprecated" in text or "historical" in text or "compatibility" in text:
                results.append(Result("OK", "legacy_doc_boundary", "{0} classifies legacy dataset names".format(relative_path)))
            else:
                results.append(Result("FAIL", "legacy_doc_boundary", "{0} mentions legacy dataset names without classification".format(relative_path)))
    return results


def check_telemetry_provenance() -> List[Result]:
    from core.controller.contract import CURRENT_FEEDBACK_KEYS
    from core.dataset_schema import (
        DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS,
        build_default_segment_telemetry_header,
        build_evaluation_segments_header,
    )

    results = []
    if tuple(DEFAULT_SEGMENT_TELEMETRY_FEEDBACK_KEYS) == tuple(CURRENT_FEEDBACK_KEYS):
        results.append(Result("OK", "feedback_key_source", "default telemetry keys use current controller feedback keys"))
    else:
        results.append(Result("FAIL", "feedback_key_source", "default telemetry keys diverge from current controller feedback keys"))

    docs = []
    for relative_path in (
        "docs/architecture/telemetry_column_provenance.md",
        "docs/architecture/metric_catalog.md",
    ):
        path = REPO_ROOT / relative_path
        if path.exists():
            docs.append(path.read_text(encoding="utf-8").lower())
    combined = "\n".join(docs)
    if not combined:
        return [Result("FAIL", "telemetry_provenance", "no telemetry provenance document found")]

    columns = sorted(set(build_default_segment_telemetry_header() + build_evaluation_segments_header()))
    missing = [column for column in columns if "`{0}`".format(column.lower()) not in combined]
    if missing:
        results.append(Result("FAIL", "telemetry_provenance_columns", "missing columns: {0}".format(", ".join(missing))))
    else:
        results.append(Result("OK", "telemetry_provenance_columns", "{0} current CSV columns documented".format(len(columns))))

    for term in ("deprecated/legacy alias", "pending methodology", "direct benchmark use now?", "producer module/function"):
        if term in combined:
            results.append(Result("OK", "telemetry_provenance_term", term))
        else:
            results.append(Result("FAIL", "telemetry_provenance_term", "missing {0}".format(term)))
    return results


def check_benchmark_neutrality() -> List[Result]:
    from core.client_config import ClientConfig
    from core.run_context import build_run_manifest, create_run_context

    with tempfile.TemporaryDirectory() as tmp:
        config = ClientConfig.from_dict({"mpd_url": "memory://readiness.mpd", "output": {"root_dir": tmp}}, source_path="<readiness>")
        context = create_run_context(config, command_args=["readiness"])
        neutrality = build_run_manifest(context, config, status="created")["benchmark_neutrality"]

    expected = {
        "outputs_are_benchmark_results": False,
        "row_eval_gate": "use_for_eval",
        "eval_phase_column": "eval_phase",
        "final_qoe_reward_defined": False,
        "final_training_dataset_defined": False,
        "terminal_drain_stall_is_rebuffering": False,
    }
    results = []
    for key, value in expected.items():
        if neutrality.get(key) == value:
            results.append(Result("OK", "benchmark_neutrality", "{0}={1}".format(key, json.dumps(value))))
        else:
            results.append(Result("FAIL", "benchmark_neutrality", "{0} expected {1}, got {2}".format(key, value, neutrality.get(key))))
    return results


def check_controller_baseline_entry() -> List[Result]:
    from core.controller import contract

    results = []
    if contract.TARGET_RATE_UNIT == "bytes_per_second":
        results.append(Result("OK", "controller_target_rate_unit", contract.TARGET_RATE_UNIT))
    else:
        results.append(Result("FAIL", "controller_target_rate_unit", str(contract.TARGET_RATE_UNIT)))
    if contract.QUALITY_LEVEL_UNIT == "representation_index":
        results.append(Result("OK", "controller_quality_level_unit", contract.QUALITY_LEVEL_UNIT))
    else:
        results.append(Result("FAIL", "controller_quality_level_unit", str(contract.QUALITY_LEVEL_UNIT)))
    if "bwe" in contract.LEGACY_FEEDBACK_KEYS and contract.FEEDBACK_CANONICAL_ALIASES.get("bwe") == "measured_download_rate":
        results.append(Result("OK", "controller_legacy_aliases", "bwe classified with measured_download_rate alias"))
    else:
        results.append(Result("FAIL", "controller_legacy_aliases", "bwe legacy alias missing"))

    text = _read_lower(REPO_ROOT / "docs/architecture/baseline_entry_contract.md")
    required_phrases = (
        "target rates are bytes per second",
        "quality levels are representation indices",
        "representation ladder source is mpd",
        "fixed_quality and scripted_quality are test/debug only",
        "max_quality is legacy/debug/stress",
        "current dict-based api",
        "legacy keys are classified",
        "must not depend on console output",
    )
    for phrase in required_phrases:
        if phrase in text:
            results.append(Result("OK", "baseline_entry_doc", phrase))
        else:
            results.append(Result("FAIL", "baseline_entry_doc", "missing phrase: {0}".format(phrase)))
    return results


def check_runtime_console_contract() -> List[Result]:
    results = []
    contract = _read_lower(REPO_ROOT / "docs/architecture/runtime_console_output_contract.md")
    progress = (REPO_ROOT / "progress_bar.py").read_text(encoding="utf-8")
    if "human-facing diagnostics" in contract and "must not be parsed by benchmark scripts" in contract:
        results.append(Result("OK", "runtime_console_contract", "console/progress is non-canonical"))
    else:
        results.append(Result("FAIL", "runtime_console_contract", "console contract does not forbid benchmark parsing"))
    if "BW (bwe)" not in progress:
        results.append(Result("OK", "runtime_progress_label", "progress label avoids BW shorthand"))
    else:
        results.append(Result("FAIL", "runtime_progress_label", "progress label still exposes BW shorthand"))
    return results


def check_gstreamer_boundary() -> List[Result]:
    text = _read_lower(REPO_ROOT / "docs/runbooks/gstreamer_playback.md")
    required = (
        "integration/demo",
        "not benchmark-grade",
        "structural validation only",
        "faster than real time",
        "do not compare fake and gst",
    )
    return _phrase_results("gstreamer_boundary", text, required)


def check_gui_boundary() -> List[Result]:
    text = _read_lower(REPO_ROOT / "docs/roadmap/gui_frontend_dashboard.md")
    required = (
        "roadmap document only",
        "the gui is not benchmark authority",
        "cli/config/run artifacts remain canonical",
        "must not train ai",
        "must not define final qoe or reward",
    )
    return _phrase_results("gui_boundary", text, required)


def check_forbidden_premature_claims() -> List[Result]:
    results = []
    offenders = []
    paths: List[Path] = []
    for relative_path in CURRENT_DOCS:
        path = REPO_ROOT / relative_path
        if path.exists():
            paths.append(path)
    paths.extend([
        REPO_ROOT / "main.py",
        REPO_ROOT / "player.py",
        REPO_ROOT / "progress_bar.py",
    ])

    for path in paths:
        text = _read_lower(path)
        for claim in FORBIDDEN_POSITIVE_CLAIMS:
            if claim in text:
                offenders.append("{0}: {1}".format(path.relative_to(REPO_ROOT), claim))
    if offenders:
        results.append(Result("FAIL", "premature_claims", "; ".join(offenders)))
    else:
        results.append(Result("OK", "premature_claims", "no forbidden positive claims found"))
    return results


def _phrase_results(code: str, text: str, phrases: Iterable[str]) -> List[Result]:
    results = []
    for phrase in phrases:
        if phrase in text:
            results.append(Result("OK", code, phrase))
        else:
            results.append(Result("FAIL", code, "missing phrase: {0}".format(phrase)))
    return results


def _ensure_repo_on_path() -> None:
    root = str(REPO_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def _read_lower(path: Path) -> str:
    return path.read_text(encoding="utf-8").lower()


def _format_exc(exc: BaseException) -> str:
    message = str(exc)
    if message:
        return "{0}: {1}".format(exc.__class__.__name__, message)
    return exc.__class__.__name__


def _write(stream: TextIO, text: str) -> None:
    stream.write(text + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
