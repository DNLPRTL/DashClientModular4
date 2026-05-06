from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXAMPLE_CONFIG = REPO_ROOT / "config" / "client.example.yaml"
DEFAULT_LOCAL_CONFIG = REPO_ROOT / "config" / "client.local.yaml"


class ConfigError(ValueError):
    """Raised when the client configuration is missing or invalid."""


@dataclass(frozen=True)
class MediaEngineConfig:
    name: str = "fake"
    min_queue_time: float = 1.0
    decode_video: bool = False
    sink_name: str | None = None


@dataclass(frozen=True)
class ControllerConfig:
    name: str = "max_quality"
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PlaybackConfig:
    initial_quality: int = 0
    initial_controller_decision: bool = False
    headless: bool = True
    max_buffer_seconds: float = 60.0
    drain_buffer_sleep_seconds: float = 0.5
    preroll_seconds: float = 10.0


@dataclass(frozen=True)
class DownloaderConfig:
    max_retries: int = 3
    verbose: bool = False


@dataclass(frozen=True)
class OutputConfig:
    root_dir: str = "logs"
    dataset_filename: str = "dataset.csv"


@dataclass(frozen=True)
class LoggingConfig:
    enabled: bool = True
    level: str = "INFO"


@dataclass(frozen=True)
class AnalysisConfig:
    enabled: bool = False
    output_root: str = "analysis_output"


@dataclass(frozen=True)
class ClientConfig:
    mpd_url: str = ""
    media_engine: MediaEngineConfig = field(default_factory=MediaEngineConfig)
    controller: ControllerConfig = field(default_factory=ControllerConfig)
    playback: PlaybackConfig = field(default_factory=PlaybackConfig)
    downloader: DownloaderConfig = field(default_factory=DownloaderConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    source_path: str | None = None

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any], source_path: str | None = None) -> "ClientConfig":
        playback_raw = _mapping(raw.get("playback"))
        media_raw = _mapping(raw.get("media_engine", raw.get("engine")))
        controller_raw = raw.get("controller", {})
        output_raw = _mapping(raw.get("output"))
        logging_raw = _mapping(raw.get("logging"))
        downloader_raw = _mapping(raw.get("downloader"))
        analysis_raw = _mapping(raw.get("analysis"))

        if isinstance(controller_raw, str):
            controller_name = controller_raw
            controller_params: dict[str, Any] = {}
        else:
            controller_map = _mapping(controller_raw)
            controller_name = _as_str(controller_map.get("name", controller_map.get("key", "max_quality")))
            controller_params = dict(_mapping(controller_map.get("params")))

        media_name = _as_str(media_raw.get("name", media_raw.get("type", "fake"))).lower()
        min_queue_time = _as_float(
            media_raw.get("min_queue_time", playback_raw.get("min_buffer_seconds", 1.0)),
            "media_engine.min_queue_time",
        )

        return cls(
            mpd_url=_as_str(raw.get("mpd_url", "")),
            media_engine=MediaEngineConfig(
                name=media_name,
                min_queue_time=min_queue_time,
                decode_video=_as_bool(media_raw.get("decode_video", False), "media_engine.decode_video"),
                sink_name=_as_optional_str(media_raw.get("sink_name")),
            ),
            controller=ControllerConfig(
                name=controller_name,
                params=controller_params,
            ),
            playback=PlaybackConfig(
                initial_quality=_as_int(
                    playback_raw.get("initial_quality", playback_raw.get("start_quality", 0)),
                    "playback.initial_quality",
                ),
                initial_controller_decision=_as_bool(
                    playback_raw.get("initial_controller_decision", False),
                    "playback.initial_controller_decision",
                ),
                headless=_as_bool(playback_raw.get("headless", raw.get("headless", True)), "playback.headless"),
                max_buffer_seconds=_as_float(
                    playback_raw.get("max_buffer_seconds", playback_raw.get("buffer_threshold_seconds", 60.0)),
                    "playback.max_buffer_seconds",
                ),
                drain_buffer_sleep_seconds=_as_float(
                    playback_raw.get("drain_buffer_sleep_seconds", 0.5),
                    "playback.drain_buffer_sleep_seconds",
                ),
                preroll_seconds=_as_float(playback_raw.get("preroll_seconds", 10.0), "playback.preroll_seconds"),
            ),
            downloader=DownloaderConfig(
                max_retries=_as_int(downloader_raw.get("max_retries", 3), "downloader.max_retries"),
                verbose=_as_bool(downloader_raw.get("verbose", False), "downloader.verbose"),
            ),
            output=OutputConfig(
                root_dir=_as_str(output_raw.get("root_dir", logging_raw.get("output_dir", "logs"))),
                dataset_filename=_as_str(output_raw.get("dataset_filename", "dataset.csv")),
            ),
            logging=LoggingConfig(
                enabled=_as_bool(logging_raw.get("enabled", True), "logging.enabled"),
                level=_as_str(logging_raw.get("level", "INFO")).upper(),
            ),
            analysis=AnalysisConfig(
                enabled=_as_bool(analysis_raw.get("enabled", False), "analysis.enabled"),
                output_root=_as_str(analysis_raw.get("output_root", "analysis_output")),
            ),
            source_path=source_path,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "mpd_url": self.mpd_url,
            "media_engine": {
                "name": self.media_engine.name,
                "min_queue_time": self.media_engine.min_queue_time,
                "decode_video": self.media_engine.decode_video,
                "sink_name": self.media_engine.sink_name,
            },
            "controller": {
                "name": self.controller.name,
                "params": dict(self.controller.params),
            },
            "playback": {
                "initial_quality": self.playback.initial_quality,
                "initial_controller_decision": self.playback.initial_controller_decision,
                "headless": self.playback.headless,
                "max_buffer_seconds": self.playback.max_buffer_seconds,
                "drain_buffer_sleep_seconds": self.playback.drain_buffer_sleep_seconds,
                "preroll_seconds": self.playback.preroll_seconds,
            },
            "downloader": {
                "max_retries": self.downloader.max_retries,
                "verbose": self.downloader.verbose,
            },
            "output": {
                "root_dir": self.output.root_dir,
                "dataset_filename": self.output.dataset_filename,
            },
            "logging": {
                "enabled": self.logging.enabled,
                "level": self.logging.level,
            },
            "analysis": {
                "enabled": self.analysis.enabled,
                "output_root": self.analysis.output_root,
            },
        }


def load_client_config(
    path: str | Path | None = None,
    *,
    defaults_path: str | Path | None = DEFAULT_EXAMPLE_CONFIG,
) -> ClientConfig:
    """Load the example config and overlay a local/user config when available."""
    merged: dict[str, Any] = {}

    if defaults_path is not None:
        defaults = Path(defaults_path)
        if defaults.exists():
            merged = _deep_merge(merged, _load_yaml_file(defaults))

    selected_path = _select_config_path(path)
    if selected_path is not None:
        if not selected_path.exists():
            raise ConfigError(f"Config file not found: {selected_path}")
        merged = _deep_merge(merged, _load_yaml_file(selected_path))

    source_path = str(selected_path) if selected_path is not None else str(defaults_path)
    return ClientConfig.from_dict(merged, source_path=source_path)


def validate_config_for_run(config: ClientConfig) -> None:
    if not config.mpd_url.strip():
        raise ConfigError(
            "mpd_url is empty. Copy config/client.example.yaml to "
            "config/client.local.yaml, set mpd_url, then run python main.py --config config/client.local.yaml."
        )
    if config.media_engine.name not in {"fake", "gst"}:
        raise ConfigError("media_engine.name must be either 'fake' or 'gst'.")
    if config.playback.initial_quality < 0:
        raise ConfigError("playback.initial_quality must be >= 0.")
    if config.media_engine.min_queue_time < 0:
        raise ConfigError("media_engine.min_queue_time must be >= 0.")
    if config.playback.max_buffer_seconds <= 0:
        raise ConfigError("playback.max_buffer_seconds must be > 0.")
    if config.playback.drain_buffer_sleep_seconds <= 0:
        raise ConfigError("playback.drain_buffer_sleep_seconds must be > 0.")
    if config.downloader.max_retries < 1:
        raise ConfigError("downloader.max_retries must be >= 1.")


def _select_config_path(path: str | Path | None) -> Path | None:
    if path is not None:
        return Path(path)
    if DEFAULT_LOCAL_CONFIG.exists():
        return DEFAULT_LOCAL_CONFIG
    return None


def _load_yaml_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8-sig")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text) or {}
        if not isinstance(loaded, dict):
            raise ConfigError(f"Config root must be a mapping: {path}")
        return loaded
    except ModuleNotFoundError:
        return _parse_simple_yaml(text, path)


def _parse_simple_yaml(text: str, path: Path) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if "\t" in raw_line:
            raise ConfigError(f"Tabs are not supported in {path}:{line_no}")

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()
        key, sep, value = line.partition(":")
        if not sep or not key.strip():
            raise ConfigError(f"Invalid YAML line in {path}:{line_no}: {raw_line}")

        while stack and indent <= stack[-1][0]:
            stack.pop()
        if not stack:
            raise ConfigError(f"Invalid indentation in {path}:{line_no}")

        parent = stack[-1][1]
        key = key.strip()
        value = value.strip()

        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = _parse_scalar(value)

    return root


def _parse_scalar(value: str) -> Any:
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]

    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none", "~"}:
        return None

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        return value


def _deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def _as_optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _as_bool(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "yes", "1", "on"}:
            return True
        if lowered in {"false", "no", "0", "off"}:
            return False
    raise ConfigError(f"{field_name} must be true or false.")


def _as_int(value: Any, field_name: str) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{field_name} must be an integer.") from exc


def _as_float(value: Any, field_name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"{field_name} must be a number.") from exc
