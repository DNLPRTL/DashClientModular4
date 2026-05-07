#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib
import os
import platform
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, TextIO, Tuple


MIN_PYTHON = (3, 8)
REPO_ROOT = Path(__file__).resolve().parents[1]

DEV_REQUIRED_MODULES = ("requests",)
DEV_PROJECT_IMPORTS = (
    "main",
    "core.client_config",
    "core.controller.registry",
    "player",
)
ANALYSIS_MODULES = ("numpy", "pandas", "matplotlib")
GST_TOOLS = ("gst-launch-1.0", "gst-inspect-1.0")


@dataclass
class CheckResult:
    profile: str
    name: str
    status: str
    message: str
    required: bool = False


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check DashClientModular4 environment readiness.")
    parser.add_argument(
        "--profile",
        choices=("dev", "analysis", "gst", "all"),
        default="dev",
        help="Environment profile to check.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat optional profile failures as required failures.",
    )
    args = parser.parse_args(argv)
    return run_profile(args.profile, strict=args.strict)


def run_profile(profile: str, strict: bool = False, stream: Optional[TextIO] = None) -> int:
    if stream is None:
        stream = sys.stdout

    _ensure_repo_on_path()

    results: List[CheckResult] = []
    selected = _expand_profiles(profile)
    _write(stream, "DashClientModular4 environment check")
    _write(stream, "Profile: {0}  Strict: {1}".format(profile, "yes" if strict else "no"))
    _write(stream, "")

    for selected_profile in selected:
        _write(stream, "== {0} ==".format(selected_profile))
        if selected_profile == "dev":
            profile_results = check_dev_profile()
        elif selected_profile == "analysis":
            profile_results = check_analysis_profile(strict=strict)
        elif selected_profile == "gst":
            profile_results = check_gst_profile(strict=strict)
        else:
            profile_results = [
                CheckResult(selected_profile, "profile", "FAIL", "Unknown profile", required=True)
            ]

        results.extend(profile_results)
        for result in profile_results:
            _write_result(stream, result)
        _write(stream, "")

    required_failures = [r for r in results if r.required and r.status == "FAIL"]
    failures = [r for r in results if r.status == "FAIL"]
    warnings = [r for r in results if r.status == "WARN"]
    oks = [r for r in results if r.status == "OK"]

    _write(stream, "Summary")
    _write(stream, "OK: {0}  WARN: {1}  FAIL: {2}".format(len(oks), len(warnings), len(failures)))
    if required_failures:
        _write(stream, "Required failures: {0}".format(len(required_failures)))
        return 1

    _write(stream, "Required checks passed.")
    return 0


def check_dev_profile() -> List[CheckResult]:
    results = [
        CheckResult("dev", "Python executable", "OK", sys.executable, required=True),
        _check_python_version(),
    ]
    results.extend(_check_modules("dev", DEV_REQUIRED_MODULES, required=True))
    results.extend(_check_project_imports())
    return results


def check_analysis_profile(strict: bool = False) -> List[CheckResult]:
    return _check_modules("analysis", ANALYSIS_MODULES, required=bool(strict))


def check_gst_profile(strict: bool = False) -> List[CheckResult]:
    required = bool(strict)
    results: List[CheckResult] = []

    try:
        gi = importlib.import_module("gi")
        gi_path = getattr(gi, "__file__", "<built-in>")
        results.append(CheckResult("gst", "PyGObject import", "OK", "gi imported from {0}".format(gi_path), required=required))
    except Exception as exc:
        status = "FAIL" if required else "WARN"
        results.append(CheckResult("gst", "PyGObject import", status, _format_exc(exc), required=required))
        results.append(_gst_skip_result("Gst require/import", "PyGObject import failed", required))
        results.append(_gst_skip_result("Gst.init(None)", "Gst import failed", required))
        results.extend(_check_gst_tools(required=required))
        return results

    gst = None
    try:
        gi.require_version("Gst", "1.0")
        gst = _import_gst()
        results.append(CheckResult("gst", "Gst require/import", "OK", "Gst 1.0 import succeeded", required=required))
    except Exception as exc:
        status = "FAIL" if required else "WARN"
        results.append(CheckResult("gst", "Gst require/import", status, _format_exc(exc), required=required))

    if gst is None:
        results.append(_gst_skip_result("Gst.init(None)", "Gst import failed", required))
    else:
        try:
            gst.init(None)
            results.append(CheckResult("gst", "Gst.init(None)", "OK", "GStreamer initialized", required=required))
        except Exception as exc:
            status = "FAIL" if required else "WARN"
            results.append(CheckResult("gst", "Gst.init(None)", status, _format_exc(exc), required=required))

    results.extend(_check_gst_tools(required=required))
    return results


def _check_python_version() -> CheckResult:
    version = sys.version_info
    version_text = "{0}.{1}.{2}".format(version.major, version.minor, version.micro)
    min_text = "{0}.{1}".format(*MIN_PYTHON)
    if (version.major, version.minor) >= MIN_PYTHON:
        return CheckResult(
            "dev",
            "Python version",
            "OK",
            "{0} on {1} (minimum {2})".format(version_text, platform.platform(), min_text),
            required=True,
        )
    return CheckResult(
        "dev",
        "Python version",
        "FAIL",
        "{0} is below supported minimum {1}".format(version_text, min_text),
        required=True,
    )


def _check_modules(profile: str, module_names: Iterable[str], required: bool) -> List[CheckResult]:
    results: List[CheckResult] = []
    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
            version = getattr(module, "__version__", None)
            detail = "installed"
            if version:
                detail = "version {0}".format(version)
            results.append(CheckResult(profile, "Python module {0}".format(module_name), "OK", detail, required=required))
        except Exception as exc:
            status = "FAIL" if required else "WARN"
            results.append(CheckResult(profile, "Python module {0}".format(module_name), status, _format_exc(exc), required=required))
    return results


def _check_project_imports() -> List[CheckResult]:
    results: List[CheckResult] = []
    for module_name in DEV_PROJECT_IMPORTS:
        try:
            importlib.import_module(module_name)
            results.append(CheckResult("dev", "Project import {0}".format(module_name), "OK", "imported", required=True))
        except Exception as exc:
            results.append(CheckResult("dev", "Project import {0}".format(module_name), "FAIL", _format_exc(exc), required=True))
    return results


def _check_gst_tools(required: bool) -> List[CheckResult]:
    results: List[CheckResult] = []
    for tool in GST_TOOLS:
        path = shutil.which(tool)
        if path:
            results.append(CheckResult("gst", "Tool {0}".format(tool), "OK", path, required=required))
        else:
            status = "FAIL" if required else "WARN"
            results.append(CheckResult("gst", "Tool {0}".format(tool), status, "not found on PATH", required=required))
    return results


def _import_gst():
    repository = __import__("gi.repository", fromlist=["Gst"])
    return repository.Gst


def _gst_skip_result(name: str, reason: str, required: bool) -> CheckResult:
    status = "FAIL" if required else "WARN"
    return CheckResult("gst", name, status, "skipped: {0}".format(reason), required=required)


def _expand_profiles(profile: str) -> Tuple[str, ...]:
    if profile == "all":
        return ("dev", "analysis", "gst")
    return (profile,)


def _ensure_repo_on_path() -> None:
    repo_root = str(REPO_ROOT)
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    try:
        os.chdir(repo_root)
    except OSError:
        pass


def _format_exc(exc: BaseException) -> str:
    message = str(exc)
    if message:
        return "{0}: {1}".format(exc.__class__.__name__, message)
    return exc.__class__.__name__


def _write_result(stream: TextIO, result: CheckResult) -> None:
    _write(stream, "{0:<4} {1}: {2}".format(result.status, result.name, result.message))


def _write(stream: TextIO, text: str) -> None:
    stream.write(text + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
