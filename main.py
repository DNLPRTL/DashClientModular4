import os
import logging
import threading
import subprocess
from datetime import datetime

from core.parser.dash import DashParser
from core.downloader import SegmentDownloader
from core.media_engine.fake import FakeMediaEngine
try:
    from core.media_engine.gst_media_engine import GST_AVAILABLE, GstMediaEngine
except Exception:
    GstMediaEngine = None
    GST_AVAILABLE = False

from core.controller.registry import available_controllers

from player import Player
from progress_bar import ProgressBarWindow

# ——— Modo headless: True = sin GUI, False = con ProgressBarWindow ———
HEADLESS = False

def main():
    # ——— Configurar logging ———
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/main.log", encoding="utf-8")
        ]
    )
    logging.info("=== CLIENTE DASH MODULAR ===")

    # ——— Selección del motor ———
    print("Motores de reproducción:")
    print("1. Fake (interno, sin GStreamer)")
    print("2. GStreamer (real)")
    engine_opt = input("Elige motor (1/2): ").strip()

    media_engine_cls = FakeMediaEngine
    media_engine_kwargs = {"min_queue_time": 1.0}
    engine_name = "FakeMediaEngine"

    if engine_opt == "2":
        if GST_AVAILABLE:
            media_engine_cls = GstMediaEngine
            # Ajusta si quieres ver vídeo real: decode_video=True usa autovideosink
            media_engine_kwargs = {"min_queue_time": 1.0, "decode_video": True}
            engine_name = "GstMediaEngine"
        else:
            logging.warning("GStreamer no disponible. Se usará FakeMediaEngine.")

    # ——— Selección del controller ———
    controller_specs = available_controllers()
    if not controller_specs:
        logging.error("No hay controladores disponibles. Saliendo.")
        return
    for i, spec in enumerate(controller_specs, start=1):
        print(f"{i}. {spec.label}")

    opcion = input("Introduce el número: ").strip()
    try:
        controller = controller_specs[int(opcion) - 1].factory()
    except (ValueError, IndexError):
        logging.error("Opción no válida. Saliendo.")
        return

    # ——— URL del MPD y ruta de log por algoritmo ———
    #
    #mpd_url = "http://172.16.0.251/dash/5/1sec/ToS-4k-1920_simple_1s.mpd"
    #mpd_url = "http://172.16.0.251/dash/2/1sec/walk_1s.mpd"
    #mpd_url =
    #
    #
    mpd_url = "http://192.168.1.132/dash/Paseo_Almunecar_10min_60fps/4sec/Paseo_Almunecar_10min_60fps_simple_4s.mpd"
    ctrl_name = controller.__class__.__name__
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", f"{ctrl_name}_metrics.csv")
    logging.info(f"Usando controlador '{ctrl_name}', log en: {log_path}")
    logging.info(f"Motor seleccionado: {engine_name}")

    # ——— Instanciación de componentes ———
    parser_dash = DashParser()
    parser_dash.load(mpd_url)
    media_engine = media_engine_cls(**media_engine_kwargs)
    downloader = SegmentDownloader()

    # ——— Cálculo de duración para la barra de progreso ———
    initial_level = 0
    period = parser_dash.get_periods()[0]
    adap = period['adaptationSets'][0]
    rep = adap['representations'][initial_level]
    if 'segment_durations' in rep and rep['segment_durations']:
        total_sec = sum(rep['segment_durations'])
    else:
        total_sec = len(rep['segments']) * rep.get('fragment_duration', 1.0)
    dur_iso = parser_dash.global_info['mediaPresentationDuration']
    total_mpd_sec = parser_dash.parse_duration(dur_iso)
    # Usamos el mayor para no recortar si el MPD declara más (la ProgressBar ya corrige a real internamente)
    total_sec = max(total_sec, total_mpd_sec)

    get_cur_time = (
        lambda: getattr(media_engine, 'current_time', None)
                or getattr(media_engine, 'get_current_time', lambda: 0)()
    )

    # ——— Crear y lanzar el Player ———
    player = Player(
        parser=parser_dash,
        media_engine=media_engine,
        downloader=downloader,
        controller=controller,
        log_path=log_path,
        mpd_url=mpd_url
    )

    def run_player():
        try:
            player.run()
        except Exception:
            logging.exception("Error en player.run")

    # hilo NO daemon para poder hacer join()
    player_thread = threading.Thread(target=run_player, daemon=False)
    player_thread.start()

    # ——— Mostrar GUI opcional donde se enlace con player ———
    if not HEADLESS:
        try:
            progress_win = ProgressBarWindow(
                media_engine=media_engine,
                total_duration_sec=total_sec,
                get_current_time=get_cur_time,
                player=player
            )
            progress_win.root.mainloop()
        except Exception:
            logging.exception("Error en ProgressBarWindow")

    # Espera a que termine player.run() antes de lanzar el análisis
    player_thread.join()
    logging.info("¡Fin de reproducción! Iniciando análisis automático.")

    # ——— Crear carpeta única para esta ejecución de análisis ———
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = os.path.join("analysis_output", f"{ctrl_name}_{timestamp}")
    os.makedirs(run_dir, exist_ok=True)

    # ——— Ejecutar analysis_metrics.py ———
    try:
        subprocess.run(
            ["python", "analysis_metrics.py", run_dir],
            check=True
        )
        logging.info(f"Análisis finalizado, resultados en: {run_dir}")
    except Exception:
        logging.exception("Error al ejecutar analysis_metrics.py")

if __name__ == "__main__":
    main()
