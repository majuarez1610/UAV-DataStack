import threading
import time
import logging
import cv2
from datetime import datetime

_logger = logging.getLogger(__name__)

class VideoService:
    def __init__(self, source=0):
        self.source = int(source) if isinstance(source, (str, int)) and str(source).isdigit() else source
        self._lock = threading.Lock()
        self._capture = None
        self._running = False
        self._last_frame = None
        self._thread = None

    def start(self):
        if self._running:
            return
        try:
            self._capture = cv2.VideoCapture(self.source)
            if not self._capture or not self._capture.isOpened():
                _logger.warning(f"Video source {self.source} not available")
                self._capture = None
                return
        except Exception:
            _logger.exception("Failed to open video source")
            self._capture = None
            return

        self._running = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()

    def _reader(self):
        while self._running and self._capture:
            try:
                ret, frame = self._capture.read()
                if not ret:
                    _logger.warning("Failed to read frame from capture")
                    time.sleep(0.5)
                    continue
                with self._lock:
                    self._last_frame = frame.copy()
            except Exception:
                _logger.exception("Exception reading video frame")
                break

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)
        if self._capture:
            try:
                self._capture.release()
            except Exception:
                pass
        self._capture = None

    def get_frame(self):
        with self._lock:
            if self._last_frame is None:
                return None
            ret, buf = cv2.imencode('.jpg', self._last_frame)
            if not ret:
                return None
            return buf.tobytes()

    def status(self):
        return {
            'available': self._capture is not None,
            'source': str(self.source),
            'last_frame_ts': datetime.utcnow().isoformat() + 'Z' if self._last_frame is not None else None
        }
