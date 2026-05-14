import logging
import os
import threading
import time
from datetime import datetime

import cv2

_logger = logging.getLogger(__name__)


class VideoService:
    def __init__(self, source=0):
        if isinstance(source, str) and source.strip().isdigit():
            self.source = int(source.strip())
        elif isinstance(source, int):
            self.source = source
        else:
            self.source = source

        self._lock = threading.Lock()
        self._capture = None
        self._running = False
        self._last_frame = None
        self._last_frame_ts = None
        self._thread = None
        self._consecutive_failures = 0

    def _open_capture(self):
        cap = None
        try:
            if os.name == "nt" and isinstance(self.source, int):
                for backend in (cv2.CAP_DSHOW, cv2.CAP_MSMF):
                    cap = cv2.VideoCapture(self.source, backend)
                    if cap and cap.isOpened():
                        try:
                            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        except Exception:
                            pass
                        for _ in range(5):
                            ok, _frame = cap.read()
                            if ok:
                                break
                            time.sleep(0.1)
                        return cap
                    if cap:
                        cap.release()

            cap = cv2.VideoCapture(self.source)
            if cap and cap.isOpened():
                try:
                    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                except Exception:
                    pass
                for _ in range(5):
                    ok, _frame = cap.read()
                    if ok:
                        break
                    time.sleep(0.1)
                return cap
        except Exception:
            _logger.exception("Failed to open video source")

        if cap:
            try:
                cap.release()
            except Exception:
                pass
        return None

    def start(self):
        if self._running:
            return
        self._capture = self._open_capture()
        if not self._capture:
            _logger.warning("Video source %s not available", self.source)
            return

        self._running = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()

    def _reopen_capture(self):
        old = self._capture
        self._capture = None
        if old:
            try:
                old.release()
            except Exception:
                pass
        time.sleep(0.3)
        self._capture = self._open_capture()

    def _reader(self):
        while self._running:
            if not self._capture:
                self._reopen_capture()
                if not self._capture:
                    time.sleep(1.0)
                    continue

            try:
                ret, frame = self._capture.read()
                if not ret or frame is None:
                    self._consecutive_failures += 1
                    _logger.warning("Failed to read frame from capture")
                    if self._consecutive_failures >= 5:
                        _logger.warning("Reopening video capture after repeated frame failures")
                        self._reopen_capture()
                        self._consecutive_failures = 0
                    time.sleep(0.2)
                    continue

                self._consecutive_failures = 0
                with self._lock:
                    self._last_frame = frame.copy()
                    self._last_frame_ts = datetime.utcnow()
            except Exception:
                _logger.exception("Exception reading video frame")
                self._reopen_capture()
                time.sleep(0.3)

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
        self._thread = None

    def get_frame(self):
        with self._lock:
            if self._last_frame is None:
                return None
            ret, buf = cv2.imencode(".jpg", self._last_frame)
            if not ret:
                return None
            return buf.tobytes()

    def status(self):
        with self._lock:
            last_ts = self._last_frame_ts.isoformat() + "Z" if self._last_frame_ts else None
            has_frame = self._last_frame is not None
        return {
            "available": bool(self._capture is not None and has_frame),
            "opened": bool(self._capture is not None),
            "source": str(self.source),
            "last_frame_ts": last_ts,
        }
