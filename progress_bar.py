# progress_bar.py
import tkinter as tk

class ProgressBarWindow:
    def __init__(self, media_engine, total_duration_sec, get_current_time, player, poll_interval=200):
        self.media_engine = media_engine
        try:
            self.total_duration_sec = float(total_duration_sec) if total_duration_sec is not None else 0.0
        except Exception:
            self.total_duration_sec = 0.0
        self.get_current_time = get_current_time
        self.player = player
        self.poll_interval = int(max(50, poll_interval))  # mínimo 50 ms para evitar sobrecarga

        self.root = tk.Tk()
        self.root.title("Progreso de reproducción y buffer")
        self.root.resizable(False, False)

        self.width = 500
        self.height = 50
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#222")
        self.canvas.pack()

        self.label_info = tk.Label(self.root, text="", font=("Arial", 12))
        self.label_info.pack()
        self.label_frag = tk.Label(self.root, text="", font=("Arial", 11))
        self.label_frag.pack()

        # Programar la primera actualización (no llamar directamente a update() aquí)
        self.root.after(self.poll_interval, self._update_safe)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    # ---------- utilidades internas ----------
    def _update_safe(self):
        """Llama a update() protegido para que la GUI no se rompa si algo no está listo aún."""
        try:
            self.update()
        except Exception as e:
            try:
                self.root.title(f"Progreso de reproducción y buffer (warn: {e})")
            except Exception:
                pass
        # Reprogramar el siguiente tick siempre
        try:
            self.root.after(self.poll_interval, self._update_safe)
        except Exception:
            pass

    def _get_real_total_duration(self):
        """
        Duración real = suma de duraciones de los fragmentos del nivel actual,
        ignorando INIT (que suele tener 0.0).
        Si no es posible, cae al total pasado por parámetro.
        """
        try:
            lvl = int(getattr(self.player, "cur_level", 0))
            durs = getattr(self.player, "durations_per_level", [[]])[lvl]
            if not durs:
                raise ValueError("Lista de duraciones vacía")
            # ignora el primer item si es INIT (dur=0.0)
            durs_iter = durs[1:] if (len(durs) > 0 and float(durs[0]) == 0.0) else durs
            total = float(sum(float(x) for x in durs_iter)) if durs_iter else 0.0
            return total if total > 0 else float(self.total_duration_sec)
        except Exception:
            try:
                return float(self.total_duration_sec)
            except Exception:
                return 0.0

    # ---------- refresco principal ----------
    def update(self):
        # Tiempo actual reportado por el engine
        try:
            cur_time = float(self.get_current_time() or 0.0)
        except Exception:
            cur_time = 0.0

        # Total REAL basado en los segmentos disponibles (fallback al MPD si no se puede)
        total = self._get_real_total_duration()

        # Buffer en segundos
        try:
            qt_fn = getattr(self.media_engine, "get_queued_time", None)
            buffer_time = float(qt_fn()) if callable(qt_fn) else float(getattr(self.media_engine, "current_buffer", 0.0) or 0.0)
        except Exception:
            buffer_time = 0.0

        # ¿Quedan segmentos por reproducir?
        real_media_total = None
        no_more_segments = False
        try:
            lvl = int(getattr(self.player, "cur_level", 0))
            segs_lvl = getattr(self.player, "segments_per_level", [[]])[lvl]
            has_init = (len(segs_lvl) > 0 and bool(segs_lvl[0].get('is_init')))
            real_media_total = len(segs_lvl) - (1 if has_init else 0)
            cur_idx = int(getattr(self.player, "cur_index", 0))
            no_more_segments = (cur_idx >= len(segs_lvl))
        except Exception:
            pass

        # Fin de reproducción si buffer vacío y no quedan segmentos, o estamos al final del total
        finished = False
        if (buffer_time < 1e-2 and (no_more_segments or (total - cur_time) < 1e-2)) and total > 0:
            finished = True
            cur_time = total

        # Limitar valores y preparar posiciones de dibujo
        cur_time = max(0.0, min(cur_time, total)) if total > 0 else 0.0
        buffer_time = max(0.0, buffer_time)
        buffer_end = cur_time + buffer_time
        if total > 0:
            buffer_end = min(buffer_end, total)

        play_x = int(self.width * (cur_time / total)) if total > 0 else 0
        buffer_x = int(self.width * (buffer_end / total)) if total > 0 else 0

        # Dibujar barra
        self.canvas.delete("all")
        # buffer (celeste) sobre la parte ya reproducida
        if total > 0 and buffer_x > play_x:
            self.canvas.create_rectangle(play_x, 10, buffer_x, self.height - 10, fill="#85e6ff", outline="")
        # progreso (azul)
        if total > 0:
            self.canvas.create_rectangle(0, 10, play_x, self.height - 10, fill="#3897f0", outline="")
        # borde
        self.canvas.create_rectangle(0, 10, self.width, self.height - 10, outline="#aaa")

        def fmt_mmss(s):
            try:
                s = int(float(s))
                return f"{s//60}:{s%60:02d}"
            except Exception:
                return "0:00"

        # Bytes encolados (opcional)
        try:
            qb_fn = getattr(self.media_engine, "get_queued_bytes", None)
            buffer_bytes = int(qb_fn()) if callable(qb_fn) else int(getattr(self.media_engine, "current_buffer_bytes", 0) or 0)
        except Exception:
            buffer_bytes = 0

        # Info de fragmento / nivel / bitrate
        frag = {}
        try:
            frag = self.player.get_current_segment_info() if self.player else {}
        except Exception:
            frag = {}

        dl_idx_show = frag.get("fragment_downloaded", "-")
        play_idx_show = frag.get("fragment_playing", "-")
        lvl = frag.get("current_level", "-")
        br = frag.get("current_bitrate", "-")  # BYTES/s

        # ---- helpers de unidades ----
        def bps_bytes_to_mbps(x):
            try:
                return (float(x) * 8.0) / 1e6
            except Exception:
                return None

        br_mbps_text = "-"
        if br != "-":
            v = bps_bytes_to_mbps(br)
            if v is not None:
                br_mbps_text = f"{v:.2f}"

        # Label principal: tiempos + buffer
        self.label_info.config(
            text=f"Reproducción: {fmt_mmss(cur_time)} / {fmt_mmss(total)}    |    Buffer: {buffer_time:.1f}s ({buffer_bytes} bytes)"
        )

        # Human label for legacy feedback['bwe']; this is not benchmark output.
        fb_dict = {}
        try:
            ctrl = getattr(self.player, "controller", None)
            fb_dict = getattr(ctrl, "feedback", {}) if ctrl else {}
        except Exception:
            fb_dict = {}

        def safe_float(v):
            try:
                return float(v)
            except Exception:
                return None

        bwe_bps = safe_float(fb_dict.get("bwe"))
        measured_rate_mbps_text = f"{bps_bytes_to_mbps(bwe_bps):.2f}" if (bwe_bps is not None and bwe_bps > 0) else "-"

        # Secondary line: level + representation rate + measured download-rate signal.
        self.label_frag.config(
            text=(f"Descargado: {dl_idx_show}   |   Reproduciendo: {play_idx_show}   |   "
                  f"Nivel: {lvl} ({br_mbps_text} Mbps)   |   Tasa descarga medida (bwe): {measured_rate_mbps_text} Mbps")
        )

        # Reprogramar si no ha terminado
        if not finished:
            # (el replan se hace en _update_safe para centralizar try/except)
            return
        else:
            # Mostrar barra completa y mensaje final
            self.canvas.delete("all")
            self.canvas.create_rectangle(0, 10, self.width, self.height - 10, fill="#3897f0", outline="#aaa")
            self.label_info.config(text="¡Reproducción terminada!")

    def close(self):
        try:
            self.root.destroy()
        except Exception:
            pass
