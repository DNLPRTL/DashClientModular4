# base_controller.py

from .contract import quantize_rate_to_level


class BaseController:
    """
    Clase base para cualquier controlador de adaptación de bitrate.
    Proporciona métodos para recibir feedback del player,
    calcular la acción de control y gestionar el estado de espera (idle).
    """

    def __init__(self):
        self.idle_duration = 1.0  # Segundos de espera entre descargas (por defecto)
        self.control_action = None  # Última acción de control calculada (bitrate B/s)
        self.feedback = None  # Diccionario con el feedback más reciente del player

    def __repr__(self):
        return f'<BaseController-{id(self)}>'

    def calcControlAction(self):
        """
        Debe ser implementado por subclases.
        Calcula el próximo bitrate (en B/s) que se debe seleccionar.
        """
        raise NotImplementedError("Subclasses must implement calcControlAction()")

    def setControlAction(self, rate):
        """
        Guarda la acción de control calculada (bitrate deseado en B/s).
        """
        self.control_action = rate

    def getControlAction(self):
        """
        Devuelve la última acción de control calculada.
        """
        return self.control_action

    def isBuffering(self):
        """
        Devuelve True si el player está bufferizando (es decir, el buffer está por debajo de lo recomendado).
        """
        # Si tienes un parámetro "max_buffer_time" en el feedback, úsalo.
        if self.feedback is None:
            return True
        # Puedes ajustar esta lógica si tu player decide buffering de otra forma.
        return self.feedback.get('queued_time', 0) < self.feedback.get('max_buffer_time', 10)

    def getIdleDuration(self):
        """
        Devuelve el tiempo de espera entre descargas (idle) en segundos.
        """
        return self.idle_duration

    def setIdleDuration(self, idle):
        """
        Permite ajustar el tiempo de espera (idle) entre descargas.
        """
        if idle < 0:
            idle = 0
        self.idle_duration = idle

    def onPlaying(self):
        """
        Hook opcional: llamado cuando el estado cambia a PLAYING.
        Las subclases pueden sobrescribir este método si lo necesitan.
        """
        pass

    def onPaused(self):
        """
        Hook opcional: llamado cuando el estado cambia a PAUSED (stalling/buffering).
        Las subclases pueden sobrescribir este método si lo necesitan.
        """
        pass

    def setPlayerFeedback(self, feedback_dict):
        """
        Recibe y almacena el feedback del player (diccionario con métricas).
        Debe llamarse antes de calcular la acción de control.
        """
        self.feedback = feedback_dict

    def quantizeRate(self, rate):
        """
        Devuelve el índice del mayor nivel (de la lista de rates) que NO excede el rate dado.
        Por ejemplo, si tus rates son [50000, 100000, 200000] y pides 150000,
        devuelve 1 (correspondiente a 100000).
        """
        if self.feedback is None or 'rates' not in self.feedback:
            return 0
        return quantize_rate_to_level(rate, self.feedback['rates'])
