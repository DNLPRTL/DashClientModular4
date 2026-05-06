# controllers/max_quality_controller.py
# -*- coding: utf-8 -*-
from __future__ import annotations

import time
from .base import BaseController


class MaxQualityController(BaseController):
    """
    Controlador que siempre selecciona el máximo nivel de calidad (máximo índice).
    - No introduce esperas (idle = 0.0): en cuanto termina un segmento, pide el siguiente.
    - Usa el `bwe` de tu Player sólo para estimar el tiempo de descarga esperado y loguearlo.
    - Modo debug opcional para entender exactamente por qué decide lo que decide.
    """

    name = "MaxQuality"

    def __init__(self, debug: bool = True):
        super().__init__()
        self.debug = bool(debug)
        self.last_metrics = {}
        self._last_decision_ts = None  # para medir decision→buffer (previo)

    # ---------- helpers ----------
    @staticmethod
    def _to_mbps(x_bps: float) -> float:
        return 8.0 * float(x_bps) / 1e6

    def _log(self, msg: str):
        if self.debug:
            print(f"[MAXQ-DBG] {msg}")

    # ---------- núcleo ----------
    def calcControlAction(self):
        fb = self.feedback or {}

        # 1) Datos básicos del feedback
        rates = fb.get("rates", []) or []
        if not rates:
            # Fallback robusto si no hay lista de rates
            r = float(fb.get("cur_bitrate", 0.0) or 0.0)
            self.setIdleDuration(0.0)
            self.setControlAction(r)
            return r

        max_level_fb = fb.get("max_level", len(rates) - 1)
        try:
            max_level = int(max(0, min(int(max_level_fb), len(rates) - 1)))
        except Exception:
            max_level = len(rates) - 1

        cur_level = int(fb.get("level", 0) or 0)
        cur_level = max(0, min(cur_level, len(rates) - 1))

        B = float(fb.get("queued_time", 0.0) or 0.0)                 # s de buffer
        p = float(fb.get("fragment_duration", 0.0) or 0.0) or 1.0    # s
        bwe = float(fb.get("bwe", 0.0) or 0.0)                        # B/s (del Player)
        seg_idx = fb.get("segment_index", None)

        # Métricas del último segmento (para diagnosticar)
        last_size = float(fb.get("last_fragment_size", 0.0) or 0.0)
        last_time = float(fb.get("last_download_time", 0.0) or 0.0)
        tp_obs = (last_size / last_time) if (last_size > 0 and last_time > 0) else 0.0

        # 2) Decisión: siempre escoger el nivel máximo permitido
        chosen_level = max_level
        chosen_rate = float(rates[chosen_level])  # B/s

        # 3) Estimaciones útiles (para logs)
        est_chunk_bytes = chosen_rate * p
        est_T_dl = (est_chunk_bytes / bwe) if bwe > 0 else float("inf")

        # Tiempo real desde la decisión previa hasta que el último segmento se metió en buffer
        decision_to_buffer_prev = None
        stop_ts = fb.get("stop_segment_request", None)  # lo publica tu Player
        if self._last_decision_ts is not None and stop_ts is not None:
            try:
                decision_to_buffer_prev = float(stop_ts) - float(self._last_decision_ts)
                if decision_to_buffer_prev < 0:
                    decision_to_buffer_prev = None
            except Exception:
                decision_to_buffer_prev = None

        # 4) Logging detallado
        if self.debug:
            self._log("===== Nueva decisión MaxQuality =====")
            self._log(f"segment_index={seg_idx}  p={p:.2f}s  B={B:.2f}s")
            self._log(f"cur_level={cur_level}  max_level={max_level}")
            self._log(f"rates (B/s)={rates}")
            self._log(f"rates (Mb/s)={[round(self._to_mbps(r), 2) for r in rates]}")
            self._log(f"bwe={self._to_mbps(bwe):.2f} Mb/s  "
                      f"tp_obs_prev={self._to_mbps(tp_obs):.2f} Mb/s "
                      f"(size={int(last_size)} B, time={last_time:.3f} s)")
            self._log(f"→ chosen_level={chosen_level}  chosen_rate={self._to_mbps(chosen_rate):.2f} Mb/s")
            self._log(f"est_chunk_bytes={int(est_chunk_bytes)} B  est_T_dl={est_T_dl:.3f} s (usando bwe)")
            if decision_to_buffer_prev is not None:
                self._log(f"real_decision→buffer(prev) ≈ {decision_to_buffer_prev:.3f} s")
            self._log("------------------------------------")

        # 5) Persistimos métricas útiles (por si exportas a CSV u otros)
        self.last_metrics = {
            "segment_index": seg_idx,
            "buffer_s": B,
            "frag_dur_s": p,
            "cur_level": cur_level,
            "max_level": max_level,
            "chosen_level": chosen_level,
            "chosen_rate_Bps": chosen_rate,
            "chosen_rate_Mbps": self._to_mbps(chosen_rate),
            "bwe_Bps": bwe,
            "bwe_Mbps": self._to_mbps(bwe),
            "prev_size_B": last_size,
            "prev_time_s": last_time,
            "prev_tp_Bps": tp_obs,
            "prev_tp_Mbps": self._to_mbps(tp_obs),
            "est_chunk_bytes": est_chunk_bytes,
            "est_T_dl_s": est_T_dl,
            "decision_to_buffer_prev_s": decision_to_buffer_prev,
        }

        # 6) Acción: sin idle y fijar tasa
        self.setIdleDuration(0.0)
        self.setControlAction(chosen_rate)
        self._last_decision_ts = time.time()
        return chosen_rate

    def __repr__(self):
        return f"<MaxQualityController debug={self.debug}>"
