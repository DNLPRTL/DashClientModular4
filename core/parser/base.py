# core/parser/base.py

class ParserBase:
    """
    Clase base para parsers de manifests de streaming adaptativo (DASH, HLS, etc).

    Todos los parsers concretos deben heredar de esta clase y sobreescribir
    los métodos principales para:
        - Analizar el manifest y extraer calidades y segmentos disponibles.
        - Proporcionar acceso estructurado a los niveles/representaciones.
        - Exponer listas de segmentos para descarga/reproducción.
    """

    def __init__(self):
        # levels: lista de diccionarios con info de cada representación/calidad.
        self.levels = []
        # playlists: lista de listas de segmentos por nivel.
        self.playlists = []

    def load(self, manifest_path):
        """
        Analiza el manifest del streaming y rellena levels y playlists.

        Args:
            manifest_path (str): Ruta local (o URL) del archivo manifest.

        Raises:
            NotImplementedError: Si el parser base es llamado directamente.
        """
        raise NotImplementedError("Debes implementar este método en el parser concreto.")

    def get_levels(self):
        """
        Devuelve una lista de diccionarios, uno por cada representación/disponible,
        por ejemplo:
            [
                {
                    'id': 'video1',
                    'bandwidth': 2000000,
                    'width': 1280,
                    'height': 720,
                    'init_url': 'init.mp4',
                    # ... otros campos útiles
                },
                ...
            ]

        Returns:
            list[dict]: Lista de niveles/calidades.
        """
        return self.levels

    def get_segments(self, level_idx):
        """
        Devuelve la lista de segmentos para un nivel dado (por índice).

        Args:
            level_idx (int): Índice de la calidad/representación.

        Returns:
            list[str|dict]: Lista de rutas/URLs de los segmentos.
        """
        return self.playlists[level_idx]

    def get_init_segment(self, level_idx):
        """
        Devuelve la URL/ruta del segmento de inicialización para un nivel dado.

        Args:
            level_idx (int): Índice de la calidad/representación.

        Returns:
            str: URL/ruta del segmento init.
        """
        raise NotImplementedError("Debes implementar este método en el parser concreto.")

    def get_duration(self):
        """
        Devuelve la duración total del contenido en segundos.

        Returns:
            float: Duración total (segundos).
        """
        raise NotImplementedError("Debes implementar este método en el parser concreto.")
