import requests
import threading
import time

perf_now = time.perf_counter

class SegmentDownloader:
    """
    Descargador simple (sin streaming ni abortos).
    Métodos:
      - download(url, byte_range=None, timeout=10, callback=None, save_path=None)
      - download_async(...)
      - download_multiple(urls, max_workers=4, **kwargs)
      - get_file_size(url, timeout=10)
    """
    def __init__(self, session=None, max_retries=3, verbose=True):
        self.session = session or requests.Session()
        self.max_retries = max_retries
        self.verbose = verbose
        self.on_event = None  # Hook opcional: on_event(event, info)

    def _emit(self, event, info):
        try:
            if callable(self.on_event):
                self.on_event(event, info)
        except Exception:
            pass

    # ============================
    #     DESCARGA COMPLETA
    # ============================
    def download(self, url, byte_range=None, timeout=10, callback=None, save_path=None, **kwargs):
        """
        Descarga un recurso completo (sin streaming de chunks).
        Devuelve (data, info) donde:
          - info['elapsed_total'] = tiempo total (s)
          - info['size'] = bytes descargados
          - info['status'] = código HTTP
          - info['ttfb'] = 0.0 (no medido)
        """
        headers = {
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        if byte_range:
            headers['Range'] = f"bytes={byte_range}"

        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            t_start = perf_now()
            try:
                resp = self.session.get(url, headers=headers, timeout=timeout)
                resp.raise_for_status()

                data = resp.content
                size = len(data)
                t_end = perf_now()

                elapsed_total = t_end - t_start
                info = {
                    'url': url,
                    'range': byte_range,
                    'size': size,
                    'status': resp.status_code,
                    'elapsed_total': elapsed_total,
                    'elapsed_payload': elapsed_total,  # mantenido por compatibilidad
                    'ttfb': 0.0,
                    'attempt': attempt,
                    'saved': False,
                    'save_path': None,
                    'content_length_header': resp.headers.get('Content-Length'),
                    'content_range_header': resp.headers.get('Content-Range'),
                    'aborted': False,
                    'bytes_downloaded': size,
                }

                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(data)
                    info['saved'] = True
                    info['save_path'] = save_path

                if callback:
                    try:
                        callback(data, info)
                    except Exception:
                        pass

                self._emit('complete', info)
                return data, info

            except Exception as e:
                last_exception = e
                self._emit('error', {'url': url, 'attempt': attempt, 'error': str(e)})
                if attempt < self.max_retries:
                    time.sleep(0.5)

        # Fallo tras todos los intentos
        error_info = {
            'url': url,
            'range': byte_range,
            'error': str(last_exception),
            'attempt': self.max_retries,
        }
        if callback:
            try:
                callback(None, error_info)
            except Exception:
                pass
        return None, error_info

    def download_async(self, url, byte_range=None, timeout=10, callback=None, save_path=None, **kwargs):
        """Descarga en un hilo. El callback se ejecuta al terminar."""
        thread = threading.Thread(
            target=self.download,
            args=(url, byte_range, timeout, callback, save_path),
            kwargs=kwargs,
            daemon=True,
        )
        thread.start()
        return thread

    def download_multiple(self, urls, max_workers=4, **kwargs):
        """Descarga múltiples urls concurrentemente con un pool de hilos."""
        from concurrent.futures import ThreadPoolExecutor
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.download, url, **kwargs) for url in urls]
            for f in futures:
                results.append(f.result())
        return results

    # ============================
    #        UTILIDADES
    # ============================
    def get_file_size(self, url, timeout=10):
        """
        Devuelve el tamaño del archivo en bytes (Content-Length) o None si falla.
        - HEAD primero
        - Fallback: GET con Range: bytes=0-0 y parsear Content-Range
        """
        try:
            resp = self.session.head(url, timeout=timeout)
            resp.raise_for_status()
            size = resp.headers.get('Content-Length')
            if size is not None:
                return int(size)
        except Exception:
            pass

        try:
            headers = {'Range': 'bytes=0-0', 'Accept-Encoding': 'identity'}
            resp = self.session.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            cr = resp.headers.get('Content-Range')
            if cr and '/' in cr:
                total = cr.split('/')[-1]
                return int(total)
        except Exception:
            pass

        return None