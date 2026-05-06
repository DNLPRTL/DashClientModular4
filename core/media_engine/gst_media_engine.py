#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import threading
import time
from typing import Optional, Callable, List

try:
    import gi
    gi.require_version("Gst", "1.0")
    gi.require_version("GObject", "2.0")
    gi.require_version("GstApp", "1.0")
    from gi.repository import Gst, GObject, GLib, GstApp

    GST_AVAILABLE = True
    GST_IMPORT_ERROR = None
except Exception as exc:
    gi = None
    Gst = None
    GObject = None
    GLib = None
    GstApp = None
    GST_AVAILABLE = False
    GST_IMPORT_ERROR = exc

# ------------------------------------
# Logging simple y configurable
# ------------------------------------
import logging
_LOG_LEVEL = os.getenv("MEDIA_ENGINE_LOG", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, _LOG_LEVEL, logging.INFO),
    format="%(asctime)s.%(msecs)03f [%(levelname)s] %(name)s :: %(message)s",
    datefmt="%H:%M:%S"
)
log = logging.getLogger("GstMediaEngine")


class GstMediaEngine:
    """
    GStreamer media engine con timeline propia para cola lógica:
    appsrc ! qtdemux ! h264parse ! queue(name=queue_v) ! avdec_h264 ! autovideosink
    """

    PAUSED = "PAUSED"
    PLAYING = "PLAYING"

    # margen para considerar “cerca del final” y no pausar por cola=0
    NEAR_END_MARGIN = 2.0     # segundos
    FINISH_CLAMP = 0.050      # ≤50 ms de resto => 0s

    # periodo de log periódico (telemetría)
    TELEMETRY_PERIOD_MS = 200

    # Clamp visual opcional: si estamos en tramo final y la cola REAL ≈ 0, clampa a 0 la cola lógica
    NEAR_END_CLAMP_BY_REAL_QUEUE = True
    NEAR_END_REAL_QUEUE_NS = 10_000_000  # 10 ms

    def __init__(self, decode_video: bool = True, min_queue_time: float = 5.0, sink_name: Optional[str] = None):
        if not GST_AVAILABLE:
            raise RuntimeError(
                "GStreamer/PyGObject is not available; use FakeMediaEngine or install the GStreamer runtime."
            ) from GST_IMPORT_ERROR

        self.decode_video = decode_video
        self.min_queue_time = float(min_queue_time)
        self.sink_name = sink_name if sink_name else ("autovideosink" if decode_video else "fakesink")

        self.pipeline: Optional[Gst.Pipeline] = None
        self.appsrc: Optional[Gst.Element] = None
        self.demux: Optional[Gst.Element] = None
        self.parser: Optional[Gst.Element] = None
        self.queue_v: Optional[Gst.Element] = None
        self.decoder: Optional[Gst.Element] = None
        self.sink: Optional[Gst.Element] = None

        self._main_loop: Optional[GLib.MainLoop] = None
        self._loop_thread: Optional[threading.Thread] = None

        self.status = self.PAUSED
        self._running_check_id = None
        self._last_queued_time = 0.0
        self._in_stall = False

        # Línea de tiempo
        self._segment_edges: List[float] = []  # acumulado de duraciones lógicas
        self._seg_pop_idx = 0
        self._time_offset = 0.0
        self.current_time = 0.0
        self._eos_seen = False
        self._playback_finished_emitted = False

        # telemetría
        self._last_telemetry_monotonic = 0.0

        # estado datos/EOS
        self._pushed_any_data = False
        self._eos_pending = False

        self.on_event: Optional[Callable[[str, dict], None]] = None

        Gst.init(None)
        log.debug("GStreamer iniciado")

    # -------- util eventos --------
    def _emit(self, event: str, info: Optional[dict] = None):
        if self.on_event and callable(self.on_event):
            try:
                self.on_event(event, info or {})
            except Exception:
                pass

    # -------- API pública --------
    def start(self):
        if self.pipeline is not None:
            log.warning("start(): pipeline ya creado")
            return

        self.pipeline = Gst.Pipeline.new("dash-pipeline")
        log.info("Creando pipeline")

        self.appsrc = Gst.ElementFactory.make("appsrc", "src")
        self.appsrc.set_property("is-live", False)
        self.appsrc.set_property("format", Gst.Format.TIME)
        self.appsrc.set_property("block", True)
        self.appsrc.set_property("do-timestamp", True)
        # Consejo: si alimentas fMP4, explícitar caps ayuda a qtdemux a no “dudar”.
        # caps = Gst.Caps.from_string("video/quicktime, variants=iso")
        # self.appsrc.set_property("caps", caps)
        self.pipeline.add(self.appsrc)
        log.debug("appsrc creado y configurado")

        self.demux = Gst.ElementFactory.make("qtdemux", "demux")
        self.pipeline.add(self.demux)

        self.parser = Gst.ElementFactory.make("h264parse", "parser")
        self.queue_v = Gst.ElementFactory.make("queue", "queue_v")
        self.queue_v.set_property("max-size-buffers", 0)
        self.queue_v.set_property("max-size-bytes", 0)
        self.queue_v.set_property("max-size-time", 0)
        self.queue_v.set_property("min-threshold-time", int(self.min_queue_time * 1e9))

        # Señales de la queue para detectar vaciados/llenados reales
        try:
            self.queue_v.connect("underrun", self._on_queue_underrun)
            self.queue_v.connect("overrun", self._on_queue_overrun)
        except Exception:
            pass

        self.decoder = Gst.ElementFactory.make("avdec_h264", "decoder") if self.decode_video else None
        self.sink = Gst.ElementFactory.make(self.sink_name, "sink") or Gst.ElementFactory.make("fakesink", "sink")

        for elem in [self.parser, self.queue_v, self.decoder, self.sink]:
            if elem:
                self.pipeline.add(elem)

        assert self.appsrc.link(self.demux), "No se pudo enlazar appsrc→demux"
        self.demux.connect("pad-added", self._on_demux_pad_added)
        self.demux.connect("no-more-pads", self._on_demux_no_more_pads)

        # Bus: EOS/errores/varios
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._on_bus_message)

        self._main_loop = GLib.MainLoop()
        self._loop_thread = threading.Thread(target=self._main_loop.run, name="GstMainLoop", daemon=True)
        self._loop_thread.start()

        self.pipeline.set_state(Gst.State.PAUSED)
        self.status = self.PAUSED
        log.info("Pipeline en PAUSED (preroll)")

        self._running_check_id = GLib.timeout_add(100, self._on_running)

    def stop(self):
        log.info("Parando pipeline…")
        try:
            if self.pipeline:
                self.pipeline.set_state(Gst.State.NULL)
        finally:
            self.pipeline = None
            self.appsrc = None
            self.demux = None
            self.parser = None
            self.queue_v = None
            self.decoder = None
            self.sink = None

        if self._running_check_id:
            try:
                GLib.source_remove(self._running_check_id)
            except Exception:
                pass
            self._running_check_id = None

        if self._main_loop:
            try:
                self._main_loop.quit()
            except Exception:
                pass
        if self._loop_thread and self._loop_thread.is_alive():
            self._loop_thread.join(timeout=1.0)

        self._main_loop = None
        self._loop_thread = None
        self._in_stall = False
        self._last_queued_time = 0.0
        self._segment_edges.clear()
        self._seg_pop_idx = 0
        self.current_time = 0.0
        self._eos_seen = False
        self._playback_finished_emitted = False
        self._pushed_any_data = False
        self._eos_pending = False
        log.info("Pipeline detenido y estado interno reiniciado")

    def end_of_stream(self):
        """Señaliza fin de stream en appsrc (EOS). Seguro y compatible."""
        if not self.appsrc or self._eos_seen:
            return

        # Si aún no se ha empujado ningún dato, difiere el EOS
        if not self._pushed_any_data:
            log.warning("EOS solicitado antes de empujar datos; se difiere hasta el primer push.")
            self._eos_pending = True
            return

        try:
            log.info("Enviando EOS a appsrc")
            # API de GstApp funciona de forma consistente
            GstApp.AppSrc.end_of_stream(self.appsrc)
        except Exception as e1:
            log.debug(f"GstApp.AppSrc.end_of_stream falló: {e1!r} → intento con action signal")
            try:
                self.appsrc.emit("end-of-stream")
            except Exception as e2:
                log.error(f"No se pudo enviar EOS a appsrc: {e2!r}")

    def push_data(self, data: bytes, fragment_duration: float, info: Optional[dict] = None):
        if not self.appsrc:
            log.warning("push_data(): appsrc no está listo")
            return
        buf = Gst.Buffer.new_allocate(None, len(data), None)
        buf.fill(0, data)
        if fragment_duration and fragment_duration > 0:
            buf.duration = int(fragment_duration * 1e9)
        ret = self.appsrc.emit("push-buffer", buf)
        if ret != Gst.FlowReturn.OK:
            log.warning(f"push-buffer devolvió {ret}, size={len(data)}")

        if fragment_duration and fragment_duration > 0:
            last_edge = self._segment_edges[-1] if self._segment_edges else 0.0
            new_edge = last_edge + float(fragment_duration)
            self._segment_edges.append(new_edge)
            log.debug(f"Segmento lógico añadido: +{fragment_duration:.3f}s → edge={new_edge:.3f}s (N={len(self._segment_edges)})")

        if not self._pushed_any_data:
            self._pushed_any_data = True
            if self._eos_pending:
                # Si nos pidieron EOS antes, envíalo ahora en idle para evitar reentradas
                GLib.idle_add(lambda: (self.end_of_stream(), False)[1])

        self._emit("segment-pushed", info or {})

    # alias de compatibilidad
    pushData = push_data

    def get_queued_time(self) -> float:
        """
        Cola lógica: (último borde) - (pos actual).
        - Si ya vimos EOS, devolvemos 0.
        - Clamp agresivo a 0 cuando el resto ≤ FINISH_CLAMP.
        - (Opcional) si estamos en tramo final y la cola REAL ≈ 0, clampa a 0.
        """
        try:
            if self._eos_seen:
                return 0.0
            last_edge = self._segment_edges[-1] if self._segment_edges else 0.0
            if last_edge > 0.0:
                remaining = last_edge - float(self.current_time)
                if remaining <= self.FINISH_CLAMP:
                    return 0.0

                if self.NEAR_END_CLAMP_BY_REAL_QUEUE and self.queue_v:
                    try:
                        q_ns = int(self.queue_v.get_property("current-level-time"))
                    except Exception:
                        q_ns = 0
                    near_end = (last_edge - self.current_time) <= self.NEAR_END_MARGIN
                    if near_end and q_ns <= self.NEAR_END_REAL_QUEUE_NS and not self._eos_seen:
                        return 0.0

                return max(0.0, remaining)

            if self.queue_v:
                # fallback a cola real si no tenemos edges
                return float(self.queue_v.get_property("current-level-time")) * 1e-9
        except Exception:
            pass
        return 0.0

    def get_queued_bytes(self) -> int:
        try:
            if self.queue_v:
                return int(self.queue_v.get_property("current-level-bytes"))
        except Exception:
            pass
        return 0

    # -------- callbacks internos --------
    def _on_demux_pad_added(self, demux, pad: Gst.Pad):
        caps = pad.get_current_caps() or pad.query_caps()
        name = caps.to_string() if caps else ""
        log.info(f"qtdemux pad-added: {pad.get_name()} caps={name}")
        if "video" not in name:
            return

        # demux:src -> parser:sink
        try:
            sinkpad = self.parser.get_static_pad("sink")
            if sinkpad and not sinkpad.is_linked():
                pad.link(sinkpad)
                log.debug("Enlace demux:src → parser:sink OK")
        except Exception as e:
            log.warning(f"demux→parser link error: {e!r}")
            return

        # parser -> queue
        try:
            srcpad = self.parser.get_static_pad("src")
            if srcpad and not srcpad.is_linked():
                self.parser.link(self.queue_v)
                log.debug("Enlace parser → queue OK")
        except Exception as e:
            log.warning(f"parser→queue link error: {e!r}")

        # queue → decoder|sink
        try:
            if self.decode_video:
                qsrc = self.queue_v.get_static_pad("src")
                dsink = self.decoder.get_static_pad("sink")
                if qsrc and dsink and not qsrc.is_linked() and not dsink.is_linked():
                    self.queue_v.link(self.decoder)
                    log.debug("Enlace queue → decoder OK")

                dsrc = self.decoder.get_static_pad("src")
                ssink = self.sink.get_static_pad("sink")
                if dsrc and ssink and not dsrc.is_linked() and not ssink.is_linked():
                    self.decoder.link(self.sink)
                    log.debug("Enlace decoder → sink OK")
            else:
                qsrc = self.queue_v.get_static_pad("src")
                ssink = self.sink.get_static_pad("sink")
                if qsrc and ssink and not qsrc.is_linked() and not ssink.is_linked():
                    self.queue_v.link(self.sink)
                    log.debug("Enlace queue → sink OK")
        except Exception as e:
            log.warning(f"queue→(decoder|sink) link error: {e!r}")

    def _on_demux_no_more_pads(self, demux):
        log.debug("qtdemux no-more-pads")

    def _on_queue_underrun(self, queue):
        log.info("queue_v UNDERRUN (cola real vacía)")
        self._emit("queue-underrun", {"t": self.current_time})

    def _on_queue_overrun(self, queue):
        log.info("queue_v OVERRUN (cola real llena)")
        self._emit("queue-overrun", {"t": self.current_time})

    def _on_bus_message(self, bus: Gst.Bus, msg: Gst.Message):
        t = msg.type
        src = msg.src.get_name() if msg.src else "?"
        if t == Gst.MessageType.EOS:
            log.info(f"[BUS] EOS recibido desde {src}")
            self._eos_seen = True
            self._maybe_emit_playback_finished()
            if os.getenv("MEDIA_ENGINE_DOT", "0") == "1":
                try:
                    Gst.debug_bin_to_dot_file(self.pipeline, Gst.DebugGraphDetails.ALL, "pipeline_eos")
                    log.info("Dump DOT escrito: pipeline_eos.dot")
                except Exception as e:
                    log.debug(f"No se pudo escribir DOT: {e!r}")

        elif t == Gst.MessageType.ERROR:
            err, dbg = msg.parse_error()
            log.error(f"[BUS] ERROR desde {src}: {err} (debug: {dbg})")
            self._emit("error", {"error": str(err), "debug": dbg})

        elif t == Gst.MessageType.STATE_CHANGED:
            old, new, pend = msg.parse_state_changed()
            if msg.src == self.pipeline:
                log.info(f"[BUS] PIPELINE state: {Gst.Element.state_get_name(old)} → {Gst.Element.state_get_name(new)} (pending={Gst.Element.state_get_name(pend)})")
            else:
                log.debug(f"[BUS] {src} state: {Gst.Element.state_get_name(old)} → {Gst.Element.state_get_name(new)}")

        elif t == Gst.MessageType.QOS:
            try:
                live, running_time, stream_time, timestamp, duration = msg.parse_qos()
                log.debug(f"[BUS] QOS {src}: live={live} run={running_time/1e9:.3f}s ts={timestamp/1e9:.3f}s dur={duration/1e9:.3f}s")
            except Exception:
                pass

        elif t == Gst.MessageType.BUFFERING:
            try:
                percent = msg.parse_buffering()
                log.debug(f"[BUS] BUFFERING {percent}%")
            except Exception:
                pass

        elif t == Gst.MessageType.LATENCY:
            log.debug("[BUS] LATENCY")
            try:
                self.pipeline.recalculate_latency()
            except Exception:
                pass

        else:
            # Evitamos value_nick (no siempre está expuesto en PyGObject)
            log.debug(f"[BUS] {t} de {src}")

    def _maybe_emit_playback_finished(self):
        if self._playback_finished_emitted:
            return
        last_edge = self._segment_edges[-1] if self._segment_edges else 0.0
        almost_done = (self.current_time >= (last_edge - self.FINISH_CLAMP)) if last_edge > 0 else False
        if self._eos_seen or almost_done:
            self._playback_finished_emitted = True
            self._emit("playback-finished", {"eos": self._eos_seen})
            log.info(f"playback-finished (eos={self._eos_seen}, current_time={self.current_time:.3f}, last_edge={last_edge:.3f})")

    def _telemetry_tick(self):
        """Log periódico con métricas clave para cazar el ‘1.1 s’."""
        now = time.monotonic()
        if (now - self._last_telemetry_monotonic) * 1000.0 < self.TELEMETRY_PERIOD_MS:
            return
        self._last_telemetry_monotonic = now

        q_time_ns = 0
        q_bytes = 0
        try:
            if self.queue_v:
                q_time_ns = int(self.queue_v.get_property("current-level-time"))
                q_bytes = int(self.queue_v.get_property("current-level-bytes"))
        except Exception:
            pass

        last_edge = self._segment_edges[-1] if self._segment_edges else 0.0
        qt_logical = self.get_queued_time()

        log.debug(
            "TLM pos=%.3fs last_edge=%.3fs rest_log=%.3fs rest_q=%.3fs bytes_q=%d eos=%s state=%s",
            self.current_time, last_edge, qt_logical, q_time_ns * 1e-9, q_bytes, self._eos_seen, self.status
        )

        # Detector de “atasco cerca del final”: resto lógico > 0 pero cola real ~ 0 y sin EOS
        if (not self._eos_seen) and (qt_logical > 0.5) and (q_time_ns <= 1e7):  # ≤10ms
            log.warning("POSIBLE ATAQUE AL FINAL: resto_log=%.3fs pero cola_real≈0s y sin EOS (¿duración de segmento sobreestimada?)",
                        qt_logical)

    def _on_running(self) -> bool:
        if not self.pipeline or (self._main_loop and not self._main_loop.is_running()):
            return False

        # reloj del pipeline
        try:
            ok, pos_ns = self.pipeline.query_position(Gst.Format.TIME)
            if ok and pos_ns is not None and pos_ns >= 0:
                self.current_time = float(pos_ns) * 1e-9 + self._time_offset
        except Exception:
            pass

        last_edge = self._segment_edges[-1] if self._segment_edges else 0.0
        qt_logical = self.get_queued_time()

        # Gate inicial: arrancar cuando hay suficiente cola
        if self.status == self.PAUSED and qt_logical >= self.min_queue_time:
            self.pipeline.set_state(Gst.State.PLAYING)
            self.status = self.PLAYING
            self._emit("status-changed", {"status": "PLAYING"})
            log.info(f"PLAYING (qt_logical={qt_logical:.3f}s ≥ min_queue={self.min_queue_time:.3f}s)")

        # No pausar por cola=0 si estamos cerca del final (para no congelar el clock)
        near_end = (last_edge > 0) and ((last_edge - self.current_time) <= self.NEAR_END_MARGIN)
        if self.status == self.PLAYING and qt_logical <= 1e-6 and not self._eos_seen and not near_end:
            self.pipeline.set_state(Gst.State.PAUSED)
            self.status = self.PAUSED
            self._emit("status-changed", {"status": "PAUSED"})
            log.info("PAUSED por cola lógica agotada fuera de near_end")

        # stall/recovery (con cola lógica)
        if not self._in_stall and self.status == self.PAUSED and qt_logical <= 1e-6 and self._last_queued_time > 0 and not near_end:
            self._in_stall = True
            self._stall_start_ts = time.perf_counter()
            self._emit("stall", {"stall_id": id(self), "event_ts": self.current_time})
            log.warning("STALL detectado (cola lógica=0)")

        if self._in_stall and self.status == self.PLAYING and qt_logical > 0:
            stall_dur = time.perf_counter() - getattr(self, "_stall_start_ts", time.perf_counter())
            self._in_stall = False
            self._emit("stall_recovered", {"stall_id": id(self), "event_ts": self.current_time, "stall_duration": stall_dur})
            log.info(f"STALL recuperado tras {stall_dur:.3f}s")

        self._last_queued_time = qt_logical

        # segment-popped según edges
        try:
            while self._seg_pop_idx < len(self._segment_edges) and self.current_time >= self._segment_edges[self._seg_pop_idx] - 1e-6:
                edge_val = self._segment_edges[self._seg_pop_idx]
                self._emit("segment-popped", {"segment_edge": edge_val})
                log.debug(f"segment-popped @ {edge_val:.3f}s (current={self.current_time:.3f}s)")
                self._seg_pop_idx += 1
        except Exception:
            pass

        # Fin por EOS o por alcanzar el último borde
        self._maybe_emit_playback_finished()

        # telemetría periódica
        self._telemetry_tick()

        return True


# ------------------------------------
# Modo standalone para pruebas manuales
# ------------------------------------
if __name__ == "__main__":
    """
    Ejemplo mínimo (reproduce si empujas datos fMP4 válidos; aquí solo arranca/para).
    Usa variables de entorno:
      MEDIA_ENGINE_LOG=DEBUG  → logs verbosos
      MEDIA_ENGINE_DOT=1      → volcado pipeline_eos.dot al final
    """
    log.info("Demo mínima: arranque/parada sin datos")
    eng = GstMediaEngine()
    eng.start()
    # Espera breve para ver estados
    time.sleep(1.0)
    eng.stop()
    log.info("Demo terminada")
