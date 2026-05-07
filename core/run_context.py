from __future__ import annotations

import importlib
from importlib import metadata as importlib_metadata
import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from core.client_config import ClientConfig


SCHEMA_VERSION = "1.0"
REPO_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_MODULES = ("requests",)
ANALYSIS_MODULES = ("numpy", "pandas", "matplotlib")
GST_TOOLS = ("gst-launch-1.0", "gst-inspect-1.0")


@dataclass(frozen=True)
class RunContext:
    run_id: str
    created_at_local: str
    created_at_utc: str
    output_root: Path
    run_dir: Path
    dataset_path: Path
    training_path: Path
    manifest_path: Path
    resolved_config_path: Path
    environment_path: Path
    log_path: Path
    command_args: List[str]

    def write_resolved_config(self, config: ClientConfig) -> None:
        _write_json(self.resolved_config_path, config.to_dict())

    def write_environment(self) -> Dict[str, Any]:
        environment = build_environment_snapshot()
        _write_json(self.environment_path, environment)
        return environment

    def write_manifest(self, config: ClientConfig, status: str = "created") -> Dict[str, Any]:
        manifest = build_run_manifest(self, config, status=status)
        _write_json(self.manifest_path, manifest)
        return manifest


def create_run_context(config: ClientConfig, command_args: Optional[Iterable[str]] = None) -> RunContext:
    now_local = datetime.now().astimezone()
    now_utc = now_local.astimezone(timezone.utc)
    output_root = Path(config.output.root_dir)
    run_id, run_dir = _create_unique_run_dir(output_root, now_local)

    dataset_name = _dataset_filename(config.output.dataset_filename)
    training_name = _training_filename(dataset_name)

    return RunContext(
        run_id=run_id,
        created_at_local=now_local.isoformat(),
        created_at_utc=now_utc.isoformat().replace("+00:00", "Z"),
        output_root=output_root,
        run_dir=run_dir,
        dataset_path=run_dir / dataset_name,
        training_path=run_dir / training_name,
        manifest_path=run_dir / "run_manifest.json",
        resolved_config_path=run_dir / "config.resolved.json",
        environment_path=run_dir / "environment.json",
        log_path=run_dir / "run.log",
        command_args=list(command_args or []),
    )


def build_run_manifest(context: RunContext, config: ClientConfig, status: str = "created") -> Dict[str, Any]:
    git = git_metadata()
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "run_id": context.run_id,
        "created_at_local": context.created_at_local,
        "created_at_utc": context.created_at_utc,
        "output_root": str(context.output_root),
        "run_dir": str(context.run_dir),
        "config_source": config.source_path,
        "command_line_args": list(context.command_args),
        "python": _python_info(),
        "platform": _platform_info(),
        "cwd": os.getcwd(),
        "git": git,
        "controller": {
            "name": config.controller.name,
            "params": dict(config.controller.params),
        },
        "media_engine": {
            "name": config.media_engine.name,
            "min_queue_time": config.media_engine.min_queue_time,
            "decode_video": config.media_engine.decode_video,
            "sink_name": config.media_engine.sink_name,
        },
        "headless": config.playback.headless,
        "mpd_url": config.mpd_url,
        "outputs": {
            "manifest": _relative_to_run(context.manifest_path, context.run_dir),
            "resolved_config": _relative_to_run(context.resolved_config_path, context.run_dir),
            "environment": _relative_to_run(context.environment_path, context.run_dir),
            "dataset": _relative_to_run(context.dataset_path, context.run_dir),
            "training": _relative_to_run(context.training_path, context.run_dir),
            "log": _relative_to_run(context.log_path, context.run_dir),
        },
    }


def build_environment_snapshot() -> Dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "python": _python_info(),
        "platform": _platform_info(),
        "cwd": os.getcwd(),
        "package_versions": _module_versions(RUNTIME_MODULES),
        "optional_analysis": _module_availability(ANALYSIS_MODULES),
        "optional_gstreamer": _gstreamer_availability(),
        "git": git_metadata(),
    }


def git_metadata() -> Dict[str, Any]:
    return {
        "commit": _git_command(["rev-parse", "HEAD"]),
        "branch": _git_command(["rev-parse", "--abbrev-ref", "HEAD"]),
        "dirty": _git_dirty(),
    }


def _create_unique_run_dir(output_root: Path, now_local: datetime) -> Tuple[str, Path]:
    output_root.mkdir(parents=True, exist_ok=True)
    base_run_id = "run_{0}".format(now_local.strftime("%Y%m%d_%H%M%S"))
    for index in range(1000):
        run_id = base_run_id if index == 0 else "{0}_{1:03d}".format(base_run_id, index)
        run_dir = output_root / run_id
        try:
            run_dir.mkdir(parents=False, exist_ok=False)
            return run_id, run_dir
        except FileExistsError:
            continue
    raise RuntimeError("Could not create a unique run directory under {0}".format(output_root))


def _dataset_filename(name: str) -> str:
    text = str(name or "").strip()
    if not text:
        return "dataset.csv"
    return Path(text).name


def _training_filename(dataset_name: str) -> str:
    if dataset_name.lower().endswith(".csv"):
        return "{0}_training.csv".format(dataset_name[:-4])
    return "{0}_training.csv".format(dataset_name)


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def _python_info() -> Dict[str, Any]:
    return {
        "executable": sys.executable,
        "version": platform.python_version(),
        "version_info": {
            "major": sys.version_info.major,
            "minor": sys.version_info.minor,
            "micro": sys.version_info.micro,
        },
    }


def _platform_info() -> Dict[str, str]:
    return {
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def _module_versions(module_names: Iterable[str]) -> Dict[str, Optional[str]]:
    versions: Dict[str, Optional[str]] = {}
    for module_name in module_names:
        status = _module_status(module_name)
        versions[module_name] = status.get("version")
    return versions


def _module_availability(module_names: Iterable[str]) -> Dict[str, Dict[str, Any]]:
    availability: Dict[str, Dict[str, Any]] = {}
    for module_name in module_names:
        availability[module_name] = _module_status(module_name)
    return availability


def _module_status(module_name: str) -> Dict[str, Any]:
    if importlib.util.find_spec(module_name) is None:
        return {
            "available": False,
            "version": None,
            "error": "not found",
        }
    return {
        "available": True,
        "version": _package_version(module_name),
        "error": None,
    }


def _package_version(package_name: str) -> Optional[str]:
    try:
        return importlib_metadata.version(package_name)
    except Exception:
        return None


def _gstreamer_availability() -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "pygobject": {"available": False, "error": None},
        "gst": {"available": False, "error": None},
        "tools": {},
    }

    try:
        gi = importlib.import_module("gi")
        data["pygobject"] = {
            "available": True,
            "error": None,
            "path": getattr(gi, "__file__", None),
        }
    except Exception as exc:
        data["pygobject"] = {"available": False, "error": _format_exc(exc)}
        data["tools"] = _tool_paths(GST_TOOLS)
        return data

    try:
        gi.require_version("Gst", "1.0")
        __import__("gi.repository", fromlist=["Gst"])
        data["gst"] = {"available": True, "error": None}
    except Exception as exc:
        data["gst"] = {"available": False, "error": _format_exc(exc)}

    data["tools"] = _tool_paths(GST_TOOLS)
    return data


def _tool_paths(tool_names: Iterable[str]) -> Dict[str, Optional[str]]:
    return {tool: shutil.which(tool) for tool in tool_names}


def _git_command(args: List[str]) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    text = result.stdout.strip()
    return text or None


def _git_dirty() -> Optional[bool]:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return bool(result.stdout.strip())


def _relative_to_run(path: Path, run_dir: Path) -> str:
    try:
        return str(path.relative_to(run_dir))
    except ValueError:
        return str(path)


def _format_exc(exc: BaseException) -> str:
    message = str(exc)
    if message:
        return "{0}: {1}".format(exc.__class__.__name__, message)
    return exc.__class__.__name__
