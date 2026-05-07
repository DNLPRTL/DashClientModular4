from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from core.client_config import (
    ClientConfig,
    ConfigError,
    load_client_config,
    validate_config_for_run,
)
from core.controller.registry import available_controllers, create_controller
from core.downloader import SegmentDownloader
from core.media_engine.fake import FakeMediaEngine
from core.parser.dash import DashParser
from core.run_context import create_run_context
from player import Player

try:
    from core.media_engine.gst_media_engine import GST_AVAILABLE, GstMediaEngine
except Exception:
    GstMediaEngine = None
    GST_AVAILABLE = False


def main(argv: Optional[List[str]] = None) -> int:
    command_args = list(argv) if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Config-driven DASH client runner.")
    parser.add_argument(
        "--config",
        "-c",
        default=None,
        help="Path to a YAML config. Defaults to config/client.local.yaml when present.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run the manual demo prompts instead of the benchmark/dev config path.",
    )
    args = parser.parse_args(argv)

    try:
        if args.interactive:
            config = _prompt_for_manual_config()
        else:
            config = load_client_config(args.config)
        validate_config_for_run(config)
        run_client(config, command_args=command_args)
        return 0
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2
    except Exception:
        logging.exception("Client run failed")
        return 1


def run_client(config: ClientConfig, command_args: Optional[List[str]] = None) -> None:
    run_context = create_run_context(config, command_args=command_args)
    _configure_logging(config, run_context.log_path)
    run_context.write_resolved_config(config)
    run_context.write_environment()
    run_context.write_manifest(config, status="created")

    logging.info("=== DASH CLIENT CONFIG RUNNER ===")
    logging.info("Config source: %s", config.source_path or "<in-memory>")
    logging.info("Run directory: %s", run_context.run_dir)
    logging.info("Controller: %s", config.controller.name)
    logging.info("Media engine: %s", config.media_engine.name)
    logging.info("Headless: %s", config.playback.headless)

    try:
        try:
            controller = create_controller(config.controller.name, config.controller.params)
        except (TypeError, ValueError) as exc:
            raise ConfigError(str(exc)) from exc
        media_engine = _create_media_engine(config)
        downloader = SegmentDownloader(
            max_retries=config.downloader.max_retries,
            verbose=config.downloader.verbose,
        )
        parser_dash = DashParser()

        player = Player(
            parser=parser_dash,
            media_engine=media_engine,
            downloader=downloader,
            controller=controller,
            log_path=str(run_context.dataset_path),
            mpd_url=config.mpd_url,
            initial_level=config.playback.initial_quality,
            use_initial_controller_decision=config.playback.initial_controller_decision,
            run_dir=str(run_context.run_dir),
        )
        _apply_runtime_config(player, config)

        run_context.write_manifest(config, status="running")
        if config.playback.headless:
            player.run()
        else:
            _run_with_progress_window(player, parser_dash, media_engine, config)

        if config.analysis.enabled:
            _run_legacy_analysis(config, controller)

        run_context.write_manifest(config, status="completed")
    except Exception:
        run_context.write_manifest(config, status="failed")
        raise


def _configure_logging(config: ClientConfig, log_path: Path) -> None:
    if not config.logging.enabled:
        logging.disable(logging.CRITICAL)
        return

    logging.disable(logging.NOTSET)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, config.logging.level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
        force=True,
    )


def _create_media_engine(config: ClientConfig):
    engine_name = config.media_engine.name
    if engine_name == "fake":
        return FakeMediaEngine(min_queue_time=config.media_engine.min_queue_time)

    if engine_name == "gst":
        if not GST_AVAILABLE or GstMediaEngine is None:
            raise ConfigError(
                "media_engine.name is 'gst', but GStreamer/PyGObject is not available. "
                "Use media_engine.name: fake for import tests and headless benchmark development."
            )
        return GstMediaEngine(
            min_queue_time=config.media_engine.min_queue_time,
            decode_video=config.media_engine.decode_video,
            sink_name=config.media_engine.sink_name,
        )

    raise ConfigError("media_engine.name must be either 'fake' or 'gst'.")


def _apply_runtime_config(player: Player, config: ClientConfig) -> None:
    player.BUFFER_THRESH = config.playback.max_buffer_seconds
    player.DRAIN_BUFFER_SLEEP_TIME = config.playback.drain_buffer_sleep_seconds
    player.PREROLL_SECONDS = config.playback.preroll_seconds


def _run_with_progress_window(player: Player, parser_dash: DashParser, media_engine, config: ClientConfig) -> None:
    parser_dash.load(config.mpd_url)
    total_sec = _estimate_total_duration(parser_dash, config.playback.initial_quality)

    def get_cur_time():
        return getattr(media_engine, "current_time", None) or getattr(media_engine, "get_current_time", lambda: 0)()

    def run_player():
        try:
            player.run()
        except Exception:
            logging.exception("Error in player.run")

    player_thread = threading.Thread(target=run_player, daemon=False)
    player_thread.start()

    try:
        from progress_bar import ProgressBarWindow

        progress_win = ProgressBarWindow(
            media_engine=media_engine,
            total_duration_sec=total_sec,
            get_current_time=get_cur_time,
            player=player,
        )
        progress_win.root.mainloop()
    except Exception:
        logging.exception("Error in ProgressBarWindow")

    player_thread.join()


def _estimate_total_duration(parser_dash: DashParser, initial_level: int) -> float:
    period = parser_dash.get_periods()[0]
    adap = period["adaptationSets"][0]
    reps = adap["representations"]
    level = min(max(0, initial_level), len(reps) - 1)
    rep = reps[level]
    if rep.get("segment_durations"):
        total_sec = sum(rep["segment_durations"])
    else:
        total_sec = len(rep.get("segments", [])) * rep.get("fragment_duration", 1.0)

    dur_iso = parser_dash.global_info.get("mediaPresentationDuration")
    total_mpd_sec = parser_dash.parse_duration(dur_iso) if dur_iso else 0.0
    return max(total_sec, total_mpd_sec)


def _run_legacy_analysis(config: ClientConfig, controller) -> None:
    ctrl_name = controller.__class__.__name__
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = Path(config.analysis.output_root) / f"{ctrl_name}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [sys.executable, "analysis_metrics.py", str(run_dir)],
        check=True,
    )
    logging.info("Analysis finished: %s", run_dir)


def _prompt_for_manual_config() -> ClientConfig:
    print("Manual demo mode")
    print("Media engines:")
    print("1. Fake (internal, no GStreamer)")
    print("2. GStreamer (real)")
    engine_opt = input("Choose engine (1/2): ").strip()
    engine_name = "gst" if engine_opt == "2" else "fake"

    specs = available_controllers()
    if not specs:
        raise ConfigError("No controllers are available.")

    print("Controllers:")
    for index, spec in enumerate(specs, start=1):
        print(f"{index}. {spec.label} [{spec.key}]")

    option = input("Choose controller number: ").strip()
    try:
        controller_name = specs[int(option) - 1].key
    except (ValueError, IndexError) as exc:
        raise ConfigError("Invalid controller selection.") from exc

    mpd_url = input("MPD URL or local MPD path: ").strip()
    headless_raw = input("Headless? (Y/n): ").strip().lower()
    headless = headless_raw not in {"n", "no"}

    return ClientConfig.from_dict(
        {
            "mpd_url": mpd_url,
            "media_engine": {
                "name": engine_name,
                "min_queue_time": 1.0,
                "decode_video": engine_name == "gst" and not headless,
            },
            "controller": {
                "name": controller_name,
                "params": {"debug": False},
            },
            "playback": {
                "initial_quality": 0,
                "initial_controller_decision": False,
                "headless": headless,
                "max_buffer_seconds": 60.0,
                "drain_buffer_sleep_seconds": 0.5,
                "preroll_seconds": 10.0,
            },
            "downloader": {
                "max_retries": 3,
                "verbose": False,
            },
            "output": {
                "root_dir": "logs",
                "dataset_filename": "dataset.csv",
            },
            "analysis": {
                "enabled": False,
            },
        },
        source_path="<interactive>",
    )


if __name__ == "__main__":
    raise SystemExit(main())
