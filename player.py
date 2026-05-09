import time
import csv
import threading
from collections import deque
from math import sqrt
import os
from datetime import datetime

from core.dataset_schema import build_dataset_header, build_training_header, validate_row_length
from core.runtime_feedback import build_controller_feedback

# reloj monotónico
perf_now = time.perf_counter


def _safe_div(a, b, default=0.0):
    try:
        if b:
            return float(a) / float(b)
        return float(default)
    except Exception:
        return float(default)


class Player:
    # ====== Parámetros (paper-like y features) ======
    PREROLL_SECONDS = 10.0
    # NUEVO: tope de buffer por delante (estilo Pensieve / players reales)
    BUFFER_THRESH = 60.0  # segundos
    DRAIN_BUFFER_SLEEP_TIME = 0.5  # segundos (Pensieve: 500 ms

    # Fases estilo paper (umbrales y smoothing)
    PHASE_STALL_THR = 1.2        # < 1.2 s => stalling
    PHASE_STEADY_BUF = 5.0       # > 5 s y variación baja => steady
    PHASE_STEADY_DELTA = 0.3     # variación del buffer <= 0.3 s
    PHASE_STEADY_MIN_DUR = 15.0  # al menos 15 s en rango para "entrar" en steady
    PHASE_STEADY_STICKY = 10.0   # si sales y vuelves en 10 s, mantenemos steady

    # Features de throughput
    TP_EWMA_ALPHA = 0.6
    TP_WINDOW = 5  # para min/std

    def __init__(self, parser, media_engine, mpd_url, downloader, controller,
                 log_path=None, initial_level=0, use_initial_controller_decision=True, run_dir=None):
        self.parser = parser
        self.media_engine = media_engine
        self.downloader = downloader
        self.controller = controller
        self.cur_level = initial_level
        self.cur_index = 0
        self.log_path = log_path
        self.mpd_url = mpd_url
        self.run_dir = run_dir
        self.dataset_csv_path = None
        self.training_csv_path = None
        self.use_initial_controller_decision = bool(use_initial_controller_decision)

        # estado general
        self.downloaded_bytes = 0
        self.media_downloaded_count = 0  # solo medias (sin INIT)

        # tiempos/estado por segmento
        self.start_segment_request = None
        self.stop_segment_request = None

        # estado para métricas de stall
        self._pending_rows = {}
        self._stall_info_by_segment = {}
        self._open_stalls = {}
        self._play_queue = deque()

        # EOS (fin limpio para motores reales)
        self._eos_sent = False

        # índice del último segmento común (para ignorar su "stall" falso)
        self._last_common_index = -1

        # Throughput / buffer history (para features)
        self._tp_hist = deque(maxlen=max(5, self.TP_WINDOW))
        self._tp_ewma = None
        self._last_buffer = None

        # Detector de fases (paper-like)
        self._phase_detector = self._PhaseDetector(
            stall_thr=self.PHASE_STALL_THR,
            steady_buf=self.PHASE_STEADY_BUF,
            steady_delta=self.PHASE_STEADY_DELTA,
            steady_min=self.PHASE_STEADY_MIN_DUR,
            steady_sticky=self.PHASE_STEADY_STICKY
        )
        self._current_phase_raw = "filling"
        self._current_phase_smooth = "filling"

        # Política / switches
        self._policy_name = getattr(self.controller, "name", self.controller.__class__.__name__)
        self._pending_policy_cols = {}  # seg_idx -> (target_rate, chosen_level, decision_ms, is_upswitch, is_downswitch, mag)
        self._last_level_for_switch = self.cur_level

        # CSV header map (se rellena al abrir CSV)
        self._header = None
        self._col_index = {}
        self._training_header = None

        # NUEVO: ficheros CSV (full + entrenamiento)
        self._csv_file = None
        self._csv_writer = None
        self._csv_train_file = None
        self._csv_train_writer = None

        # hooks
        if hasattr(self.media_engine, "on_event"):
            self.media_engine.on_event = self._on_media_event
        if hasattr(self.downloader, "on_event"):
            self.downloader.on_event = self.on_downloader_event

    # ---------- detector de fases (paper-like) ----------
    class _PhaseDetector:
        def __init__(self, stall_thr, steady_buf, steady_delta, steady_min, steady_sticky):
            self.stall_thr = float(stall_thr)
            self.steady_buf = float(steady_buf)
            self.steady_delta = float(steady_delta)
            self.steady_min = float(steady_min)
            self.steady_sticky = float(steady_sticky)
            self._buf_hist = deque(maxlen=20)  # (t, buffer)
            self._last_t = 0.0
            self._last_buf = 0.0

            self._raw = "filling"
            self._smooth = "filling"

            # smoothing helpers
            self._steady_candidate_start = None
            self._last_left_steady_t = None

        def _buf_std_lastW(self, W=5):
            vals = [b for (_, b) in list(self._buf_hist)[-W:]]
            if len(vals) <= 1:
                return 0.0
            m = sum(vals) / len(vals)
            var = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
            return sqrt(var)

        def update(self, t, buffer_s):
            t = float(t)
            b = float(buffer_s)
            prev_b = self._last_buf

            # prioridad: primeras lecturas
            self._buf_hist.append((t, b))
            self._last_t, self._last_buf = t, b

            # Reglas "raw"
            if b < self.stall_thr:
                raw = "stalling"
            else:
                # Candidato steady si (buffer alto y variación baja)
                is_steady_like = (b > self.steady_buf) and (self._buf_std_lastW(W=5) <= self.steady_delta)
                if is_steady_like:
                    raw = "steady"
                else:
                    # tendencia
                    if (b - prev_b) >= self.steady_delta:
                        raw = "filling"
                    else:
                        raw = "depletion"

            self._raw = raw

            # Smoothing estilo paper
            if raw == "stalling":
                self._smooth = "stalling"
                if self._smooth == "steady":
                    self._last_left_steady_t = t
                self._steady_candidate_start = None
                return self._raw, self._smooth

            if raw == "steady":
                if self._smooth == "steady":
                    return self._raw, self._smooth
                if self._steady_candidate_start is None:
                    self._steady_candidate_start = t
                if self._last_left_steady_t is not None and (t - self._last_left_steady_t) <= self.steady_sticky:
                    self._smooth = "steady"
                    return self._raw, self._smooth
                if (t - self._steady_candidate_start) >= self.steady_min:
                    self._smooth = "steady"
                    return self._raw, self._smooth
            else:
                self._steady_candidate_start = None
                if self._smooth == "steady":
                    self._last_left_steady_t = t

            if self._smooth != "steady":
                self._smooth = raw
            return self._raw, self._smooth

    # ---------- eventos ----------
    def on_downloader_event(self, event, info):
        status = "-"
        try:
            status = info.get('status', info.get('error', '-'))
        except Exception:
            pass
        print(f"[downloader] {event}: {status}")

    def _on_media_event(self, event, info):
        try:
            ct = info.get('current_time', '-')
        except Exception:
            ct = '-'
        print(f"[engine] {event} @ {ct}s")

        if event == "stall":
            stall_id = info.get('stall_id')
            start_ts = info.get('event_ts')
            seg_idx = self._play_queue[0] if self._play_queue else self.cur_index
            if stall_id is not None and start_ts is not None:
                self._open_stalls[stall_id] = {"start_ts": float(start_ts), "segment_index": int(seg_idx)}
                si = self._stall_info_by_segment.setdefault(int(seg_idx), {"flag": 0, "duration": 0.0})
                si["flag"] = 1
                print(f"[metrics] stall start id={stall_id} seg={seg_idx} ts={start_ts}")

        elif event == "stall_recovered":
            stall_id = info.get('stall_id')
            rec_ts = info.get('event_ts')
            supplied = info.get('stall_duration')
            if stall_id in self._open_stalls:
                start_ts = self._open_stalls[stall_id]["start_ts"]
                seg_idx = self._open_stalls[stall_id]["segment_index"]
                dur = float(supplied) if supplied is not None else (float(rec_ts) - float(start_ts))
                si = self._stall_info_by_segment.setdefault(int(seg_idx), {"flag": 0, "duration": 0.0})
                si["duration"] += max(0.0, dur)
                print(f"[metrics] stall end id={stall_id} seg={seg_idx} dur={dur:.6f}s")
                del self._open_stalls[stall_id]

        elif event == "segment-popped":
            if self._play_queue:
                seg_idx = int(self._play_queue.popleft())
                self._flush_segment_row(seg_idx)
            else:
                seg_idx = int(info.get("segment_index", max(0, self.cur_index - 1)))
                self._flush_segment_row(seg_idx)

        elif event == "playback-finished":
            for seg_idx in sorted(list(self._pending_rows.keys())):
                self._flush_segment_row(int(seg_idx))

    # --------------------------- run ---------------------------
    def run(self):
        self.start_time_global = perf_now()
        print("▶️  Inicio de reproducción adaptativa")
        self.parser.load(self.mpd_url)

        # Unir todas las reps de vídeo de todos los AdaptationSet
        period = self.parser.get_periods()[0]
        adapt_sets = period.get('adaptationSets', [])
        video_sets = [
            a for a in adapt_sets
            if (a.get('type') == 'video') or (a.get('mimeType', '').startswith('video'))
        ] or adapt_sets

        reps = []
        for a in video_sets:
            reps.extend(a.get('representations', []))
        if reps:
            reps.sort(key=lambda r: int(r.get('bandwidth', 0)))
        if not reps:
            raise RuntimeError("No se encontraron Representations de vídeo en el MPD")

        # tasas y duraciones por representación
        self.rates = [(r['bandwidth'] / 8.0) for r in reps]  # BYTES/s
        self.frag_durations = [r.get('fragment_duration', 1.0) or 1.0 for r in reps]
        self.max_level = len(reps) - 1

        # construir lista de segmentos por nivel
        segments_per_level, durations_per_level = [], []
        num_items = None
        for rep in reps:
            segs, durs = [], []
            if not rep.get('segment_base_info'):
                if rep.get('init_url'):
                    segs.append({'url': rep['init_url'], 'range': None, 'is_init': True})
                    durs.append(0.0)
                real_d = rep.get('segment_durations', [])
                for i, u in enumerate(rep['segments']):
                    segs.append({'url': u, 'range': None, 'is_init': False})
                    dur = real_d[i] if i < len(real_d) else rep.get('fragment_duration', 1.0)
                    durs.append(dur or 1.0)
            else:
                s = rep['segment_base_info']
                url = s['media_url']
                if s.get('init_range'):
                    segs.append({'url': url, 'range': s['init_range'], 'is_init': True})
                    durs.append(0.0)
                frag = rep.get('fragment_duration', 1.0) or 1.0
                tot = self.parser.parse_duration(self.parser.global_info.get('mediaPresentationDuration', ''))
                n = int(tot // frag) or 1
                end = int(s.get('index_range', '0-0').split('-')[1])
                size = self.downloader.get_file_size(url) or (end + 1 + 100_000_000)
                start = end + 1
                seg_size = (size - start) // n
                for i in range(n):
                    a = start + i * seg_size
                    b = size - 1 if i == n - 1 else a + seg_size - 1
                    segs.append({'url': url, 'range': f"{a}-{b}", 'is_init': False})
                    durs.append(frag)

            # asegurar INIT en todos los niveles
            has_init = (len(segs) > 0 and segs[0]['is_init'])
            if not has_init:
                segs.insert(0, {'url': None, 'range': None, 'is_init': True, 'virtual_init': True})
                durs.insert(0, 0.0)

            segments_per_level.append(segs)
            durations_per_level.append(durs)
            count = len(segs)
            num_items = count if num_items is None else min(num_items, count)

        self.durations_per_level = durations_per_level
        self.segments_per_level = segments_per_level

        # último índice común (incluye INIT si lo hay)
        if num_items is None:
            raise RuntimeError("No hay segmentos en el MPD")
        self._last_common_index = int(num_items - 1)

        # display: SOLO medias reales
        self.display_media_total_by_level = []
        for segs_lvl in self.segments_per_level:
            has_init = (len(segs_lvl) > 0 and segs_lvl[0]['is_init'])
            real_media = len(segs_lvl) - (1 if has_init else 0)
            self.display_media_total_by_level.append(real_media)

        display_media_total_lvl0 = self.display_media_total_by_level[self.cur_level]
        print(f"ℹ️  Representations: {len(self.rates)} | Levels 0..{self.max_level} | "
              f"Medias reales (nivel {self.cur_level}): {display_media_total_lvl0} + INIT")

        # primer feedback + nivel inicial
        fb0 = self.get_feedback(0, 0, 0.0)
        if hasattr(self.controller, "augment_feedback"):
            try:
                fb0 = self.controller.augment_feedback(fb0, context={"phase": "header"})
            except Exception:
                pass

        self._fb_keys = list(fb0.keys())
        self.controller.setPlayerFeedback(fb0)
        if self.use_initial_controller_decision:
            rate0 = self.controller.calcControlAction()
            self.cur_level = min(self.controller.quantizeRate(rate0), self.max_level)
        else:
            self.cur_level = min(max(0, int(self.cur_level)), self.max_level)
        print(f"➡️  Nivel inicial: {self.cur_level} ({self.rates[self.cur_level]} B/s)")

        # warm-up: 1 segmento sin adaptación
        self._warmup = True

        # abrir CSVs (full + entrenamiento) en carpeta por ejecución
        if self.log_path:
            # Resolver carpeta base y nombre base
            if self.run_dir:
                run_dir = self.run_dir
                os.makedirs(run_dir, exist_ok=True)
                if os.path.isdir(self.log_path):
                    base_name = "dataset.csv"
                else:
                    b = os.path.basename(self.log_path)
                    base_name = b if (b and "." in b) else "dataset.csv"
            elif os.path.isdir(self.log_path):
                base_dir = self.log_path
                base_name = "dataset.csv"
                run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                run_dir = os.path.join(base_dir, f"run_{run_stamp}")
                os.makedirs(run_dir, exist_ok=True)
            else:
                d = os.path.dirname(self.log_path)
                b = os.path.basename(self.log_path)
                base_dir = d if d else "."
                base_name = b if (b and "." in b) else "dataset.csv"
                run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                run_dir = os.path.join(base_dir, f"run_{run_stamp}")
                os.makedirs(run_dir, exist_ok=True)

            dataset_csv_path = os.path.join(run_dir, base_name)
            name_wo_ext = base_name[:-4] if base_name.lower().endswith(".csv") else base_name
            training_csv_path = os.path.join(run_dir, f"{name_wo_ext}_training.csv")
            self.run_dir = run_dir
            self.dataset_csv_path = dataset_csv_path
            self.training_csv_path = training_csv_path

            # CSV completo (dataset)
            f = open(dataset_csv_path, 'w', newline='')
            self._csv_file = f
            self._csv_writer = csv.writer(f)

            header = build_dataset_header(self._fb_keys)
            self._header = header
            self._col_index = {name: idx for idx, name in enumerate(header)}
            self._csv_writer.writerow(header)

            # NUEVO: CSV de entrenamiento
            ft = open(training_csv_path, 'w', newline='')
            self._csv_train_file = ft
            self._csv_train_writer = csv.writer(ft)
            train_header = build_training_header()
            self._training_header = train_header
            self._csv_train_writer.writerow(train_header)

            print(f"🧾 Logs en: {run_dir}")
            print(f"   - Dataset:    {os.path.basename(dataset_csv_path)}")
            print(f"   - Entrenamiento: {os.path.basename(training_csv_path)}")

        self.media_engine.start()

        # Bucle principal
        num_items = len(self.segments_per_level[0])  # garantizado por construcción previa
        while self.cur_index < num_items:
            segs_lvl = self.segments_per_level[self.cur_level]
            durs_lvl = self.durations_per_level[self.cur_level]
            seg = segs_lvl[self.cur_index]
            dur = durs_lvl[self.cur_index]
            url, br, is_init = seg['url'], seg['range'], seg['is_init']

            # Denominador de display para el nivel actual (solo medias reales)
            media_total_disp = self.display_media_total_by_level[self.cur_level]
            if is_init:
                print(f"\n[INIT] | nivel {self.cur_level} | dur {dur:.2f}s")
            else:
                media_idx = sum(1 for s in segs_lvl[:self.cur_index + 1] if not s['is_init'])
                print(f"\n[{media_idx}/{media_total_disp}] SEG | nivel {self.cur_level} | dur {dur:.2f}s")

            print(f"    URL: {url}{f'  (Range {br})' if br else ''}")

            if is_init and (url is None or seg.get('virtual_init')):
                # INIT virtual sin descarga
                self.start_segment_request = perf_now()
                self.stop_segment_request = self.start_segment_request
                self.media_engine.push_data(b"", fragment_duration=0.0, info={'status': 'virtual-init'})

                fb = self.get_feedback(0, 0, 0.0, fragment_duration=0.0)
                if hasattr(self.controller, "augment_feedback"):
                    try:
                        fb = self.controller.augment_feedback(fb, context={"phase": "row", "is_init": True})
                    except Exception:
                        pass
                self.controller.setPlayerFeedback(fb)
                wall_time_elapsed = perf_now() - self.start_time_global

                # features derivadas + fases + preroll
                derived = self._compute_derived_features(fb, wall_time_elapsed, is_init=True)

                if self._csv_writer:
                    ts = int(time.time())
                    base_row = (
                        [self.cur_index, ts]
                        + [fb[k] for k in self._fb_keys]
                        + [1, 0, self.start_segment_request, self.stop_segment_request, wall_time_elapsed]
                    )
                    row = base_row + [
                        derived['tp_now'], derived['tp_ewma'], derived['tp_min_last5'], derived['tp_std_last5'],
                        derived['buffer_over_seg'], derived['headroom'],
                        0, 0, 0,  # switches (INIT no decide)
                        derived['phase_raw'], derived['phase_smooth'],
                        self._policy_name, "", "", 0.0,  # policy (no aplica aún)
                        derived['is_preroll'], derived['use_for_eval']
                    ] + [0, 0.0]  # stall_* para INIT
                    validate_row_length(row, self._header, schema_name="dataset.csv")
                    self._csv_writer.writerow(row)
                    self._csv_file.flush()

                # NUEVO: fila de entrenamiento
                self._write_training_row(
                    seg_idx=self.cur_index,
                    is_init=1,
                    use_for_eval=derived['use_for_eval'],
                    last_size=0,
                    last_time=0.0,
                    frag_dur=0.0
                )

                print(f"    ✅ INIT virtual (sin descarga)")
                print(f"    ⏱️  Buffer: {self.media_engine.get_queued_time():.2f}s")

            else:
                # reintentos con descarga clásica
                MAX_RETRIES = 6
                retry_count = 0

                # NUEVO: pacing de buffer — espera si excede el umbral antes de pedir el siguiente MEDIA segment
                # NUEVO: Pensieve-like idle: si el buffer supera el umbral, dormimos en pasos de 500 ms
                if not is_init:
                    qt = float(self.media_engine.get_queued_time() or 0.0)
                    if qt > self.BUFFER_THRESH:
                        drain_buffer_time = qt - self.BUFFER_THRESH
                        # redondea hacia arriba a múltiplos de 500 ms
                        step = self.DRAIN_BUFFER_SLEEP_TIME
                        sleep_time = (int(drain_buffer_time / step + 0.9999)) * step
                        if sleep_time <= 0:
                            sleep_time = step
                        print(
                            f"    💤 Buffer {qt:.2f}s > {self.BUFFER_THRESH:.0f}s: idle {sleep_time:.2f}s (pasos {step:.2f}s)")
                        slept = 0.0
                        while slept < sleep_time:
                            time.sleep(step)
                            slept += step
                            # salida temprana si ya drenamos por debajo del umbral
                            if float(self.media_engine.get_queued_time() or 0.0) <= self.BUFFER_THRESH:
                                break

                while True:
                    self.start_segment_request = perf_now()
                    data, info = self.downloader.download(url, byte_range=br)
                    self.stop_segment_request = perf_now()
                    dt_total = self.stop_segment_request - self.start_segment_request
                    dt_used = info.get('elapsed_total', dt_total) if isinstance(info, dict) else dt_total
                    sz = len(data) if data else 0

                    if data:
                        print(f"    ✅ OK | {sz} bytes en {dt_used:.2f}s")

                        if not is_init:
                            self.media_engine.push_data(data, fragment_duration=dur, info=info)
                            self.downloaded_bytes += sz
                            self.media_downloaded_count += 1

                            fb = self.get_feedback(0, sz, dt_used, fragment_duration=dur)
                            if hasattr(self.controller, "augment_feedback"):
                                try:
                                    fb = self.controller.augment_feedback(fb, context={"phase": "row", "is_init": False})
                                except Exception:
                                    pass
                            self._play_queue.append(self.cur_index)
                        else:
                            self.media_engine.push_data(data, fragment_duration=0.0, info=info)
                            fb = self.get_feedback(0, 0, dt_used, fragment_duration=0.0)
                            if hasattr(self.controller, "augment_feedback"):
                                try:
                                    fb = self.controller.augment_feedback(fb, context={"phase": "row", "is_init": True})
                                except Exception:
                                    pass

                        self.controller.setPlayerFeedback(fb)
                        wall_time_elapsed = perf_now() - self.start_time_global

                        # features derivadas + fases + preroll
                        derived = self._compute_derived_features(fb, wall_time_elapsed, is_init=is_init)

                        if self._csv_writer:
                            ts = int(time.time())
                            base_row = (
                                [self.cur_index, ts]
                                + [fb[k] for k in self._fb_keys]
                                + [int(is_init), retry_count,
                                   self.start_segment_request, self.stop_segment_request, wall_time_elapsed]
                            )
                            row = base_row + [
                                derived['tp_now'], derived['tp_ewma'], derived['tp_min_last5'], derived['tp_std_last5'],
                                derived['buffer_over_seg'], derived['headroom'],
                                0, 0, 0,  # switches → se rellenan tras la decisión
                                derived['phase_raw'], derived['phase_smooth'],
                                self._policy_name, "", "", 0.0,  # policy → se rellena tras decisión
                                derived['is_preroll'], derived['use_for_eval']
                            ]
                            if is_init:
                                # INIT con datos reales (raro), cerramos la fila completa
                                row += [0, 0.0]
                                validate_row_length(row, self._header, schema_name="dataset.csv")
                                self._csv_writer.writerow(row)
                                self._csv_file.flush()
                            else:
                                # guardamos pendiente (stall_* y policy/switch se pueden actualizar luego)
                                self._pending_rows[self.cur_index] = row

                        # NUEVO: fila de entrenamiento (para INIT reales también)
                        self._write_training_row(
                            seg_idx=self.cur_index,
                            is_init=int(is_init),
                            use_for_eval=derived['use_for_eval'],
                            last_size=sz if not is_init else 0,
                            last_time=dt_used if not is_init else 0.0,
                            frag_dur=dur if not is_init else 0.0
                        )

                        print(f"    ⏱️  Buffer: {self.media_engine.get_queued_time():.2f}s")
                        break

                    else:
                        # fallo duro (sin datos)
                        retry_count += 1
                        if retry_count >= MAX_RETRIES:
                            if self.cur_level > 0:
                                self.cur_level -= 1
                                print(f"    ↘️  Fallos repetidos: bajo a nivel {self.cur_level} y reintento…")
                                retry_count = 0
                                continue
                            else:
                                print("    ⛔ Sin niveles más bajos. Sigo con el siguiente segmento.")
                                break
                        backoff = min(0.5 * 2 ** retry_count, 10.0)
                        print(f"    ⚠️  Error (intento {retry_count}/{MAX_RETRIES}). Esperando {backoff:.1f}s…")
                        time.sleep(backoff)

            # adaptación (congelada en INIT) + warm-up 1 segmento
            if not is_init:
                if self._warmup:
                    print(f"    🔧 Warm-up: mantengo nivel {self.cur_level} para el próximo")
                    # seguimos sin decisión (no rellenamos policy/switch)
                    self._warmup = False
                else:
                    # medir latencia de decisión
                    t0 = perf_now()
                    nr = self.controller.calcControlAction()
                    decision_ms = (perf_now() - t0) * 1000.0

                    prev_level = self.cur_level
                    lvl = min(self.controller.quantizeRate(nr), self.max_level)
                    print(f"    🎯 Objetivo {int(nr)} B/s  → nivel {lvl}")
                    self.cur_level = lvl

                    # switches
                    is_up = 1 if (lvl > prev_level) else 0
                    is_down = 1 if (lvl < prev_level) else 0
                    mag = abs(lvl - prev_level)

                    # Rellenar policy/switch en la fila pendiente del segmento actual
                    self._update_pending_policy_and_switch(
                        seg_idx=self.cur_index,
                        target_rate=nr,
                        chosen_level=lvl,
                        decision_ms=decision_ms,
                        is_up=is_up,
                        is_down=is_down,
                        magnitude=mag
                    )

            self.cur_index += 1
            time.sleep(self.controller.getIdleDuration())

        # Enviar EOS SOLO cuando ya hemos encolado el último segmento
        if not self._eos_sent and hasattr(self.media_engine, "end_of_stream"):
            try:
                self.media_engine.end_of_stream()
                self._eos_sent = True
            except Exception:
                pass

        # fin playback con timeout DINÁMICO (evita cortar antes de tiempo)
        print("\n⌛ Esperando a que el buffer se vacíe…")
        qt_now = float(self.media_engine.get_queued_time() or 0.0)
        drain_timeout = max(5.0, qt_now + 5.0)
        timeout_deadline = perf_now() + drain_timeout
        while self.media_engine.get_queued_time() > 0.01 and perf_now() < timeout_deadline:
            time.sleep(0.05)
        if self.media_engine.get_queued_time() > 0.01:
            print("⏱️  Tiempo agotado esperando el buffer. Cierro igualmente.")
        print("✅ Reproducción finalizada")

        # cierre limpio
        if getattr(self, "_csv_file", None):
            try:
                for seg_idx in sorted(list(self._pending_rows.keys())):
                    self._flush_segment_row(int(seg_idx))
                self._csv_file.close()
            except:
                pass
        if getattr(self, "_csv_train_file", None):
            try:
                self._csv_train_file.close()
            except:
                pass
        if hasattr(self.media_engine, "stop"):
            try:
                self.media_engine.stop()
            except:
                pass

    # ------------------------- helpers CSV -------------------------
    def _update_pending_policy_and_switch(self, seg_idx, target_rate, chosen_level, decision_ms, is_up, is_down, magnitude):
        """Rellena en la fila pendiente los campos de policy y switches del segmento seg_idx."""
        row = self._pending_rows.get(seg_idx)
        if not row or not self._header:
            return

        def setcol(name, value):
            i = self._col_index.get(name)
            if i is None:
                return
            # Nota: row no incluye las dos últimas columnas (stall_*),
            # pero todos los índices anteriores coinciden con el header
            if i < len(row):
                row[i] = value

        setcol('policy_name', self._policy_name)
        setcol('policy_target_rate', float(target_rate))
        setcol('policy_chosen_level', int(chosen_level))
        setcol('policy_decision_ms', float(decision_ms))
        setcol('is_upswitch', int(is_up))
        setcol('is_downswitch', int(is_down))
        setcol('switch_magnitude', int(magnitude))

    def _flush_segment_row(self, seg_idx: int):
        if not getattr(self, "_csv_writer", None):
            return
        base_row = self._pending_rows.pop(seg_idx, None)
        if base_row is None:
            return
        si = self._stall_info_by_segment.pop(seg_idx, {"flag": 0, "duration": 0.0})

        # ignorar "stall" del último segmento (falso positivo de cola)
        if seg_idx == getattr(self, "_last_common_index", -1):
            si = {"flag": 0, "duration": 0.0}

        final_row = base_row + [int(si.get("flag", 0)), float(si.get("duration", 0.0))]
        validate_row_length(final_row, self._header, schema_name="dataset.csv")
        self._csv_writer.writerow(final_row)
        self._csv_file.flush()

    def _write_training_row(self, seg_idx, is_init, use_for_eval, last_size, last_time, frag_dur):
        """NUEVO: escribe una fila en el CSV de entrenamiento."""
        if not self._csv_train_writer:
            return
        row = [
            int(seg_idx),
            int(is_init),
            int(use_for_eval),
            int(last_size) if last_size is not None else 0,
            float(last_time) if last_time is not None else 0.0,
            float(frag_dur) if frag_dur is not None else 0.0
        ]
        validate_row_length(row, self._training_header, schema_name="dataset_training.csv")
        self._csv_train_writer.writerow(row)
        self._csv_train_file.flush()

    # ------------------------- features derivadas -------------------------
    def _compute_derived_features(self, fb: dict, wall_time_elapsed: float, is_init: bool):
        # Throughput del último segmento
        tp_now = 0.0
        if not is_init:
            tp_now = _safe_div(fb.get('last_fragment_size', 0), fb.get('last_download_time', 0), default=0.0)

        # EWMA
        if tp_now > 0:
            if self._tp_ewma is None:
                self._tp_ewma = float(tp_now)
            else:
                a = self.TP_EWMA_ALPHA
                self._tp_ewma = a * float(tp_now) + (1 - a) * float(self._tp_ewma)

            self._tp_hist.append(float(tp_now))

        tp_ewma = float(self._tp_ewma) if self._tp_ewma is not None else 0.0

        # Ventana últimos N para min/std
        lastN = list(self._tp_hist)[-self.TP_WINDOW:]
        tp_min_last5 = min(lastN) if lastN else 0.0
        if len(lastN) <= 1:
            tp_std_last5 = 0.0
        else:
            m = sum(lastN) / len(lastN)
            var = sum((x - m) ** 2 for x in lastN) / (len(lastN) - 1)
            tp_std_last5 = sqrt(var)

        # Buffer / fragmento y headroom
        qt = float(fb.get('queued_time', 0.0) or 0.0)
        fd = float(fb.get('fragment_duration', 0.0) or 0.0)
        cur_bitrate = float(fb.get('cur_bitrate', 0.0) or 0.0)

        buffer_over_seg = _safe_div(qt, fd, default=0.0) if fd > 0 else 0.0
        headroom = _safe_div(tp_now, cur_bitrate, default=0.0) if cur_bitrate > 0 else 0.0

        # Fase (raw y smoothed) estilo paper
        raw_phase, smooth_phase = self._phase_detector.update(wall_time_elapsed, qt)
        self._current_phase_raw = raw_phase
        self._current_phase_smooth = smooth_phase

        # Preroll (marcado para evaluación)
        is_preroll = 1 if wall_time_elapsed < self.PREROLL_SECONDS else 0
        use_for_eval = 0 if is_preroll else 1

        return {
            'tp_now': float(tp_now),
            'tp_ewma': float(tp_ewma),
            'tp_min_last5': float(tp_min_last5),
            'tp_std_last5': float(tp_std_last5),
            'buffer_over_seg': float(buffer_over_seg),
            'headroom': float(headroom),
            'phase_raw': raw_phase,
            'phase_smooth': smooth_phase,
            'is_preroll': int(is_preroll),
            'use_for_eval': int(use_for_eval),
        }

    # ------------------------- feedback (incluye BWE) -------------------------
    def get_feedback(self, last_paused, last_size, last_time, fragment_duration=None):
        return build_controller_feedback(
            queued_bytes=self.media_engine.get_queued_bytes(),
            queued_time=self.media_engine.get_queued_time(),
            rates=self.rates,
            fragment_durations=self.frag_durations,
            cur_level=self.cur_level,
            max_level=self.max_level,
            downloaded_bytes=self.downloaded_bytes,
            segment_index=self.cur_index,
            start_segment_request=self.start_segment_request,
            stop_segment_request=self.stop_segment_request,
            last_size=last_size,
            last_time=last_time,
            fragment_duration=fragment_duration,
        )

    # ---------------------- info para la UI ----------------------
    def get_current_segment_info(self):
        try:
            t = getattr(self.media_engine, 'current_time', 0.0)
            segs = self.durations_per_level[self.cur_level]
            acc, playing = 0.0, 0
            for d in segs:
                acc += d
                if t < acc:
                    break
                playing += 1
            return {
                "fragment_downloaded": self.media_downloaded_count,
                "fragment_playing": max(1, playing),
                "current_level": self.cur_level,
                "current_bitrate": self.rates[self.cur_level],
            }
        except:
            return {
                "fragment_downloaded": "-",
                "fragment_playing": "-",
                "current_level": "-",
                "current_bitrate": "-"
            }
