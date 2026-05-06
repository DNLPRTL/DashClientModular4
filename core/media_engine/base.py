# core/media_engine/base.py

class BaseMediaEngine:
    PAUSED = 0
    PLAYING = 1

    def __init__(self, min_queue_time=10):
        """
        min_queue_time: umbral de seguridad para lógica adaptativa (en segundos)
        """
        self.min_queue_time = min_queue_time
        self.is_running = False
        self.status = self.PAUSED
        self.video_container = None

    def __repr__(self):
        return f'<BaseMediaEngine-{id(self)}>'

    def start(self):
        if self.is_running:
            return
        print(f"[MediaEngine] Start: {self}")
        self.is_running = True

    def stop(self):
        if not self.is_running:
            return
        print(f"[MediaEngine] Stop: {self}")
        self.is_running = False

    def on_running(self):
        """Método a implementar por las subclases: cambio de pausa a play."""
        raise NotImplementedError("Subclasses should implement on_running()")

    def push_data(self, data, fragment_duration=None, level=None, caps=None, info=None):
        """
        Añade un segmento al buffer (debe ser implementado por subclases).
        """
        raise NotImplementedError("Subclasses should implement push_data()")

    def get_queued_bytes(self):
        """Devuelve bytes en buffer (subclase debe implementarlo)."""
        raise NotImplementedError("Subclasses should implement get_queued_bytes()")

    def get_queued_time(self):
        """Devuelve segundos acumulados en buffer (subclase debe implementarlo)."""
        raise NotImplementedError("Subclasses should implement get_queued_time()")

    def get_status(self):
        """Estado actual (PLAYING o PAUSED)."""
        return self.status

    def get_video_container(self):
        return self.video_container

    def set_video_container(self, video_container):
        self.video_container = video_container

