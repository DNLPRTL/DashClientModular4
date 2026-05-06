# analysis_metrics.py
import os
import sys
import glob
import logging
import traceback
from typing import Tuple, Dict, Optional, List

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt

# ——— Salida ———
OUTPUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "analysis_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ——— Logging ———
log_path = os.path.join(OUTPUT_DIR, "analysis.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(log_path, encoding="utf-8")]
)
logging.info(f"Salida de análisis en: {OUTPUT_DIR}")

# ——— Entradas ———
CSV_DIR = "logs"
PATTERN = os.path.join(CSV_DIR, "*_metrics.csv")

REQUIRED_COLS = [
    "segment_index", "is_init", "cur_rate", "wall_time_elapsed",
    "segment_start_time", "segment_end_time",
    "stall_flag", "stall_duration",
    "last_fragment_size", "last_download_time", "fragment_duration"
]

# ==========================
# Lectura y métricas base
# ==========================
def _coerce_types(df: pd.DataFrame) -> pd.DataFrame:
    defaults = {
        "segment_index": -1,
        "is_init": 0,
        "cur_rate": np.nan,
        "wall_time_elapsed": np.nan,
        "segment_start_time": np.nan,
        "segment_end_time": np.nan,
        "stall_flag": 0,
        "stall_duration": 0.0,
        "last_fragment_size": 0,
        "last_download_time": np.nan,
        "fragment_duration": np.nan,
        "level": np.nan,  # puede no venir; lo añadimos
    }
    for c, d in defaults.items():
        if c not in df.columns:
            df[c] = d

    int_cols = ["segment_index", "is_init", "stall_flag"]
    float_cols = [
        "cur_rate", "wall_time_elapsed",
        "segment_start_time", "segment_end_time",
        "stall_duration", "last_download_time", "fragment_duration", "level"
    ]
    int_like_cols = ["last_fragment_size"]

    for c in int_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(defaults[c]).astype(int)
    for c in float_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in int_like_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(defaults[c]).astype(int)

    # Orden por índice de segmento por si acaso
    if "segment_index" in df.columns:
        df = df.sort_values("segment_index").reset_index(drop=True)
    return df

def _estimate_startup_delay(df: pd.DataFrame) -> float:
    non_init = df[df["is_init"] == 0]
    if non_init.empty:
        return float(df["wall_time_elapsed"].iloc[0]) if "wall_time_elapsed" in df.columns else 0.0
    t_first_req = df["segment_start_time"].min()
    t_first_noninit_done = non_init["segment_end_time"].iloc[0]
    if np.isnan(t_first_req) or np.isnan(t_first_noninit_done):
        return float(df["wall_time_elapsed"].iloc[0]) if "wall_time_elapsed" in df.columns else 0.0
    return max(0.0, float(t_first_noninit_done - t_first_req))

def _count_switches_series(series: pd.Series) -> Tuple[int, float, int, int]:
    """
    Cuenta cambios sobre una serie discreta (level o cur_rate cuantizado):
      - n_switches: total de cambios
      - mean_abs_delta: media de |delta| entre muestras consecutivas
      - up_switches / down_switches: desglose
    """
    if series.isna().all() or series.shape[0] <= 1:
        return 0, 0.0, 0, 0
    diffs = series.diff().fillna(0)
    switches_mask = diffs != 0
    n_switches = int(switches_mask.sum())
    mean_abs_delta = float(diffs.abs().replace(0, np.nan).mean() or 0.0)
    up = int((diffs > 0).sum())
    down = int((diffs < 0).sum())
    return n_switches, mean_abs_delta, up, down

def _quality_switches(df: pd.DataFrame) -> Tuple[int, float, int, int]:
    """
    Cambios de calidad en NO INIT:
      - usa 'level' si existe (preferido)
      - si no, usa 'cur_rate' (tratando como niveles discretos).
    """
    non_init = df[df["is_init"] == 0].copy()
    if non_init.empty:
        return 0, 0.0, 0, 0

    if non_init["level"].notna().any():
        series = non_init["level"].round().astype("Int64")
    else:
        # Agrupar por valores de cur_rate "discretos"
        # Redondeamos a entero para evitar pequeñas variaciones flotantes
        series = non_init["cur_rate"].round().astype("Int64")

    return _count_switches_series(series)

def _playback_time(df: pd.DataFrame) -> float:
    non_init = df[df["is_init"] == 0]
    if "fragment_duration" not in df.columns or non_init.empty:
        return float("nan")
    return float(non_init["fragment_duration"].fillna(0.0).sum())

def _total_bytes(df: pd.DataFrame) -> int:
    non_init = df[df["is_init"] == 0]
    return int(non_init["last_fragment_size"].fillna(0).sum())

def _mean_throughput_bps(df: pd.DataFrame) -> float:
    non_init = df[df["is_init"] == 0]
    if non_init.empty or "last_download_time" not in df.columns:
        return float("nan")
    size = non_init["last_fragment_size"].fillna(0).sum()
    t = non_init["last_download_time"].fillna(0).sum()
    return float(size * 8 / t) if t > 0 else float("nan")

def load_and_summarize(csv_path: str):
    try:
        logging.info(f"Cargando CSV: {csv_path}")
        df = pd.read_csv(csv_path)
        df = _coerce_types(df)
    except Exception:
        logging.error(f"Error al leer {csv_path}:\n{traceback.format_exc()}")
        return None, None

    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        logging.warning(f"Faltan columnas en {csv_path}: {missing}")

    try:
        startup_delay = _estimate_startup_delay(df)
        rebuffer_duration = float(df["stall_duration"].sum())
        rebuffer_count = int(df["stall_flag"].sum())

        # Medias de bitrate (B/s) y en Mbps (informativo)
        bitrate_mean = float(df[df["is_init"] == 0]["cur_rate"].mean())
        bitrate_std = float(df[df["is_init"] == 0]["cur_rate"].std())
        bitrate_mean_mbps = bitrate_mean * 8 / 1e6 if not np.isnan(bitrate_mean) else float("nan")

        switches, mean_switch_delta, up_sw, down_sw = _quality_switches(df)
        play_time = _playback_time(df)
        total_bytes = _total_bytes(df)
        avg_dl_time = float(df[df["is_init"] == 0]["last_download_time"].mean()) if "last_download_time" in df.columns else float("nan")
        thr_bps = _mean_throughput_bps(df)
        thr_mbps = thr_bps / 1e6 if not np.isnan(thr_bps) else float("nan")

        # rebuffer ratio
        if np.isnan(play_time):
            rebuffer_ratio = float("nan")
        else:
            denom = play_time + rebuffer_duration
            rebuffer_ratio = float(rebuffer_duration / denom) if denom > 0 else 0.0

        # switches por minuto de vídeo reproducido (mejor comparabilidad)
        switch_rate_per_min = float(switches / (play_time / 60.0)) if play_time and play_time > 0 else float("nan")

        metrics = {
            "startup_delay":       startup_delay,            # s (↓ mejor)
            "rebuffer_duration":   rebuffer_duration,        # s (↓)
            "rebuffer_count":      rebuffer_count,           # (↓)
            "rebuffer_ratio":      rebuffer_ratio,           # (↓)
            "bitrate_mean":        bitrate_mean,             # B/s (↑)
            "bitrate_mean_mbps":   bitrate_mean_mbps,        # Mbps (↑)
            "bitrate_stddev":      bitrate_std,              # B/s
            "quality_switches":    switches,                 # (↓)
            "avg_switch_delta":    mean_switch_delta,        # niveles o B/s
            "up_switches":         up_sw,
            "down_switches":       down_sw,
            "switch_rate_per_min": switch_rate_per_min,      # (↓)
            "playback_time":       play_time,                # s
            "avg_segment_download_time": avg_dl_time,        # s
            "throughput_mean_mbps": thr_mbps,                # Mbps
            "total_bytes_mb":      total_bytes / (1024 * 1024),
        }
        return df, pd.Series(metrics)
    except Exception:
        logging.error(f"Error al resumir métricas de {csv_path}:\n{traceback.format_exc()}")
        return df, None

# ==========================
# Visualizaciones
# ==========================
def _save_bar(summary_df: pd.DataFrame, metric: str, ylabel: str, title: str, out_dir: str):
    try:
        plt.figure(figsize=(10, 5))
        vals = summary_df[metric]
        vals.plot(kind="bar", rot=45)
        plt.ylabel(ylabel)
        plt.title(title)
        plt.tight_layout()
        path = os.path.join(out_dir, f"bar_{metric}.png")
        plt.savefig(path)
        plt.close()
        logging.info(f"Gráfico de barras '{metric}' guardado en: {path}")
    except Exception:
        logging.error(f"Error al graficar '{metric}':\n{traceback.format_exc()}")

def plot_summary_tables(summary_df: pd.DataFrame, out_dir: str):
    # — Gráfico "todo junto" (puede aplastar escalas, se deja como referencia)
    try:
        ax = summary_df.plot.bar(rot=45, figsize=(14, 7))
        ax.set_ylabel("Valor (mezcla de escalas)")
        ax.set_title("Comparativa de métricas por algoritmo (todas)")
        plt.tight_layout()
        path = os.path.join(out_dir, "bar_comparison_all_metrics.png")
        plt.savefig(path)
        plt.close()
        logging.info(f"Gráfico de barras (todas) guardado en: {path}")
    except Exception:
        logging.error("Error en gráfico de barras global:\n" + traceback.format_exc())

    # — Gráficos por métrica (para que 'quality_switches' y otros se vean claros)
    singles = [
        ("bitrate_mean_mbps", "Mbps", "Bitrate medio (Mbps)"),
        ("throughput_mean_mbps", "Mbps", "Throughput medio (descarga)"),
        ("rebuffer_duration", "segundos", "Rebuffer total (s)"),
        ("rebuffer_ratio", "ratio", "Ratio de rebuffer"),
        ("rebuffer_count", "cuenta", "Número de stalls"),
        ("startup_delay", "segundos", "Startup delay (s)"),
        ("quality_switches", "cambios", "Cambios de calidad (conteo)"),
        ("switch_rate_per_min", "cambios/min", "Cambios de calidad por minuto"),
        ("avg_switch_delta", "nivel/valor", "Intensidad media del cambio de calidad"),
        ("total_bytes_mb", "MB", "Total descargado (MB)"),
    ]
    for metric, ylabel, title in singles:
        if metric in summary_df.columns:
            _save_bar(summary_df, metric, ylabel, title, out_dir)

    # — Trade-off calidad vs rebuffer
    try:
        plt.figure(figsize=(7, 6))
        x = summary_df["bitrate_mean_mbps"].values
        y = summary_df["rebuffer_duration"].values
        plt.scatter(x, y)
        for i, name in enumerate(summary_df.index):
            plt.annotate(name, (x[i], y[i]), textcoords="offset points", xytext=(5, -5))
        plt.xlabel("Bitrate medio (Mbps)")
        plt.ylabel("Rebuffer total (s)")
        plt.title("Trade-off: Calidad vs Rebuffering")
        plt.tight_layout()
        path = os.path.join(out_dir, "scatter_quality_vs_rebuffer.png")
        plt.savefig(path)
        plt.close()
        logging.info(f"Scatter guardado en: {path}")
    except Exception:
        logging.error("Error en scatter calidad vs rebuffer:\n" + traceback.format_exc())

def plot_timelines(per_run_data: Dict[str, Optional[pd.DataFrame]], out_dir: str):
    """
    Línea temporal de bitrate/level por algoritmo y marcadores de stalls + switches.
    """
    try:
        for name, df in per_run_data.items():
            if df is None:
                continue
            non_init = df[df["is_init"] == 0].copy()
            if non_init.empty:
                continue

            x = non_init["segment_index"].values
            # Preferimos LEVEL si existe
            if non_init["level"].notna().any():
                y = non_init["level"].round()
                y_label = "Nivel"
                title = f"Evolución de nivel y stalls — {name}"
            else:
                y = non_init["cur_rate"]
                y_label = "Bitrate (B/s)"
                title = f"Evolución de bitrate y stalls — {name}"

            plt.figure(figsize=(12, 4))
            plt.plot(x, y, marker="o", linewidth=1.2)

            # Marcar stalls
            stalled = non_init[non_init["stall_flag"] == 1]
            if not stalled.empty:
                xs = stalled["segment_index"].values
                ys = y[non_init["stall_flag"] == 1]
                plt.scatter(xs, ys, marker="x")

            # Marcar switches (líneas verticales finas)
            if len(non_init) > 1:
                series = (non_init["level"].round()
                          if non_init["level"].notna().any()
                          else non_init["cur_rate"].round())
                diffs = series.diff().fillna(0)
                switch_pos = non_init.loc[diffs != 0, "segment_index"].values
                for sp in switch_pos:
                    plt.axvline(sp, linestyle="--", linewidth=0.6, alpha=0.6)

            plt.xlabel("Segmento")
            plt.ylabel(y_label)
            plt.title(title)
            plt.tight_layout()
            path = os.path.join(out_dir, f"{name}_timeline.png")
            plt.savefig(path)
            plt.close()
            logging.info(f"Timeline guardado en: {path}")
    except Exception:
        logging.error("Error al generar timelines:\n" + traceback.format_exc())

# ==========================
# QoE compuesto (ranking)
# ==========================
def _minmax_norm(s: pd.Series, invert: bool = False) -> pd.Series:
    s = s.astype(float)
    if s.isna().all():
        return s.fillna(0.0)
    lo, hi = s.min(), s.max()
    if hi - lo == 0:
        n = s - lo
    else:
        n = (s - lo) / (hi - lo)
    return 1.0 - n if invert else n

def build_qoe_score(summary_df: pd.DataFrame) -> pd.Series:
    """
    QoE (↑ mejor) combinando métricas normalizadas:
      + bitrate_mean_mbps (peso 0.40)
      - rebuffer_ratio     (0.30)
      - switch_rate_per_min(0.20)
      - startup_delay      (0.10)
    """
    w = dict(bitrate=0.40, rebuf=0.30, switches=0.20, startup=0.10)

    bitrate = _minmax_norm(summary_df["bitrate_mean_mbps"], invert=False) if "bitrate_mean_mbps" in summary_df else 0.0
    rebuf = _minmax_norm(summary_df["rebuffer_ratio"], invert=True) if "rebuffer_ratio" in summary_df else 0.0
    switches = _minmax_norm(summary_df["switch_rate_per_min"], invert=True) if "switch_rate_per_min" in summary_df else 0.0
    startup = _minmax_norm(summary_df["startup_delay"], invert=True) if "startup_delay" in summary_df else 0.0

    score = (w["bitrate"] * bitrate.fillna(0.0) +
             w["rebuf"]   * rebuf.fillna(0.0) +
             w["switches"]* switches.fillna(0.0) +
             w["startup"] * startup.fillna(0.0))
    score.name = "qoe_score"
    return score

def main():
    per_run_data: Dict[str, Optional[pd.DataFrame]] = {}
    all_summaries: List[pd.Series] = []

    # 1) Leer y resumir
    for path in glob.glob(PATTERN):
        name = os.path.splitext(os.path.basename(path))[0]
        df, series = load_and_summarize(path)
        per_run_data[name] = df
        if series is not None:
            series.name = name
            all_summaries.append(series)
        else:
            logging.warning(f"Se omitió {path} por errores previos")

    if not all_summaries:
        logging.error("No se cargó ningún CSV válido. Termina la ejecución.")
        return

    summary_df = pd.DataFrame(all_summaries)
    summary_df.index.name = "algorithm"
    logging.info("Tabla resumen construida correctamente.")

    # 2) QoE score + ranking
    try:
        qoe = build_qoe_score(summary_df)
        summary_df = summary_df.copy()
        summary_df["qoe_score"] = qoe
        ranking = summary_df.sort_values("qoe_score", ascending=False)
        rank_csv = os.path.join(OUTPUT_DIR, "ranking.csv")
        ranking.to_csv(rank_csv, float_format="%.6f")
        logging.info(f"Ranking guardado en: {rank_csv}")

        # Barra del score
        _save_bar(ranking, "qoe_score", "score (0..1)", "QoE Score (↑ mejor)", OUTPUT_DIR)
    except Exception:
        logging.error("Error al calcular/guardar ranking:\n" + traceback.format_exc())

    # 3) Guardar CSV resumen
    try:
        summary_csv = os.path.join(OUTPUT_DIR, "summary_metrics.csv")
        summary_df.to_csv(summary_csv, float_format="%.6f")
        logging.info(f"Resumen guardado en: {summary_csv}")
    except Exception:
        logging.error("Error al guardar resumen CSV:\n" + traceback.format_exc())

    # 4) Gráficos por métrica y comparativas claras
    plot_summary_tables(summary_df, OUTPUT_DIR)

    # 5) Timelines por algoritmo (nivel/bitrate + stalls + marcas de switches)
    plot_timelines(per_run_data, OUTPUT_DIR)

    # 6) Guardar también CSVs “limpios” por algoritmo
    try:
        clean_dir = os.path.join(OUTPUT_DIR, "runs_clean")
        os.makedirs(clean_dir, exist_ok=True)
        for name, df in per_run_data.items():
            if df is None:
                continue
            out = os.path.join(clean_dir, f"{name}.csv")
            df.to_csv(out, index=False)
        logging.info(f"CSVs normalizados por run en: {clean_dir}")
    except Exception:
        logging.error("Error al guardar CSVs normalizados:\n" + traceback.format_exc())

if __name__ == "__main__":
    main()
