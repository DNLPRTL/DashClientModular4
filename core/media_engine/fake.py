import time
import threading
from .base import BaseMediaEngine

perf_now = time.perf_counter

class FakeMediaEngine(BaseMediaEngine):
    """
    Motor multimedia simulado:
      - Reproducción con reloj monotónico (paso real).
      - Bytes en cola decrecen proporcionalmente al tiempo consumido.
      - Arranca cuando queued_time >= min_queue_time; pausa cuando ~0.
      - Eventos con timestamps monotónicos: 'event_ts' en todos.
      - 'stall' y 'stall_recovered' emparejados con 'stall_id' y 'stall_duration'
        (duración medida en reloj monotónico, no tiempo de media).
    """
    def __init__(self, min_queue_time=1.0, on_event=None):
        super().__init__(min_queue_time)
        self.status = self.PAUSED
        self.current_time = 0.0
        self._playback_thread = None
        self._running = False
        self.on_event = on_event

        # Cada entrada del buffer: {'data': bytes, 'bytes_left': int, 'duration_left': float, 'full_duration': float, 'info': any}
        self._buffer = []
        self._lock = threading.Lock()
        self._cv = threading.Condition(self._lock)

        self._stalled = True
        self._all_segments_played = False
        self._total_duration = 0.0

        # Umbral de pausa para evitar parpadeo
        self._pause_threshold = 0.01

        # Para medir stalls con reloj monotónico
        self._stall_counter = 0
        self._last_stall_start_ts = None  # perf_now() en inicio de stall

    def __repr__(self):
        return f'<FakeMediaEngine-{id(self)}>'

    # ---------------------- Ciclo de vida ----------------------

    def start(self):
        super().start()
        with self._lock:
            self._running = True
            self.status = self.PAUSED
            self._stalled = True
            self.current_time = 0.0
            self._total_duration = 0.0
            self._all_segments_played = False
            self._last_stall_start_ts = None
            if not self._playback_thread or not self._playback_thread.is_alive():
                self._playback_thread = threading.Thread(target=self._play_loop, daemon=True)
                self._playback_thread.start()
            self._cv.notify_all()

    def stop(self):
        super().stop()
        with self._lock:
            self._running = False
            self._cv.notify_all()
        if self._playback_thread and self._playback_thread.is_alive():
            self._playback_thread.join(timeout=1.0)
        with self._lock:
            self.status = self.PAUSED

    # ---------------------- Reproducción ----------------------

    def _play_loop(self):
        last = perf_now()
        while True:
            with self._lock:
                if not self._running:
                    return

                now = perf_now()
                dt = max(0, now - last)
                last = now

                queued_time = self._queued_time_unlocked()

                if self.status == self.PAUSED and queued_time >= self.min_queue_time:
                    self._enter_running_unlocked()

                if self.status == self.PLAYING:
                    if self._buffer:
                        seg = self._buffer[0]
                        if seg['duration_left'] > 0:
                            consume_t = min(dt, seg['duration_left'])
                            seg['duration_left'] -= consume_t
                            self.current_time += consume_t

                            full_dur = max(seg['full_duration'], 1e-9)
                            bytes_total = len(seg['data'])
                            bytes_consume = int(bytes_total * (consume_t / full_dur))
                            seg['bytes_left'] = max(0, seg['bytes_left'] - bytes_consume)

                        if seg['duration_left'] <= 1e-9:
                            popped = self._buffer.pop(0)
                            self._emit('segment-popped', {
                                'size': len(popped['data']),
                                'info': popped['info'],
                                'current_time': self.current_time,
                                'event_ts': now,
                            })

                        if self._queued_time_unlocked() <= self._pause_threshold:
                            self._enter_underrun_unlocked(now)
                    else:
                        # ¡Importante!: si ya consumimos todo, emitimos fin y NO generamos 'stall'
                        if not self._all_segments_played and self._total_duration > 0:
                            self.current_time = self._total_duration
                            self._all_segments_played = True
                            self._emit('playback-finished', {
                                'current_time': self.current_time,
                                'event_ts': now,
                            })
                            # No llamar a _enter_underrun_unlocked() aquí para evitar 'stall' final
                        else:
                            self._enter_underrun_unlocked(now)

                # Espera adaptativa
                if self.status == self.PAUSED and self._queued_time_unlocked() < self.min_queue_time:
                    self._cv.wait(timeout=0.05)
                else:
                    self._cv.wait(timeout=0.01)

    def _enter_running_unlocked(self):
        if self.status != self.PLAYING:
            self.status = self.PLAYING
            if self._stalled:
                self._stalled = False
                now_ts = perf_now()
                stall_dur = 0.0
                if self._last_stall_start_ts is not None:
                    stall_dur = max(0.0, now_ts - self._last_stall_start_ts)
                # Emitimos 'stall_recovered' con duración y mismo stall_id
                self._emit('stall_recovered', {
                    'current_time': self.current_time,    # tiempo de media (no avanza durante el stall)
                    'event_ts': now_ts,                   # reloj monotónico
                    'stall_duration': stall_dur,
                    'stall_id': self._stall_counter if self._stall_counter > 0 else None,
                })
                # limpiamos inicio
                self._last_stall_start_ts = None

    def _enter_underrun_unlocked(self, now_ts=None):
        # FIX: si ya acabamos toda la reproducción, NO emitir 'stall'
        if self._all_segments_played:
            self.status = self.PAUSED
            return

        if self.status != self.PAUSED:
            self.status = self.PAUSED
            if not self._stalled:
                self._stalled = True
                if now_ts is None:
                    now_ts = perf_now()
                # Nuevo stall: incrementa id y guarda ts de inicio
                self._stall_counter += 1
                self._last_stall_start_ts = now_ts
                self._emit('stall', {
                    'current_time': self.current_time,  # tiempo de media
                    'event_ts': now_ts,                 # reloj monotónico
                    'stall_id': self._stall_counter,
                })

    # ---------------------- API usada por Player ----------------------

    def push_data(self, data, fragment_duration, level=None, caps=None, info=None):
        """Inserta un fragmento reproducible. Los INIT (duración 0) se ignoran."""
        if fragment_duration <= 0.0:
            self._emit('segment-pushed', {
                'size': len(data),
                'duration': 0.0,
                'info': info,
                'event_ts': perf_now(),
                'timestamp': int(time.time() * 1000),  # mantenemos ms wall-clock si alguien lo usa
            })
            with self._lock:
                self._cv.notify_all()
            return

        with self._lock:
            self._buffer.append({
                'data': data,
                'bytes_left': len(data),
                'duration_left': float(fragment_duration),
                'full_duration': float(fragment_duration),
                'info': info,
            })
            self._total_duration += float(fragment_duration)

            self._emit('segment-pushed', {
                'size': len(data),
                'duration': float(fragment_duration),
                'info': info,
                'event_ts': perf_now(),
                'timestamp': int(time.time() * 1000),
            })

            self._cv.notify_all()

    def get_queued_time(self):
        with self._lock:
            return self._queued_time_unlocked()

    def get_queued_bytes(self):
        with self._lock:
            return sum(seg['bytes_left'] for seg in self._buffer)

    def get_total_duration(self):
        with self._lock:
            return self._total_duration

    def is_finished(self):
        with self._lock:
            return self._all_segments_played

    # ---------------------- Helpers internos ----------------------

    def _queued_time_unlocked(self):
        """Suma de las duraciones restantes en cola (seg)."""
        return sum(seg['duration_left'] for seg in self._buffer)

    def _emit(self, event, payload):
        if callable(self.on_event):
            try:
                self.on_event(event, payload)
            except Exception:
                pass
