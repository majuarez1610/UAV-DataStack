import threading
import time
import random
import math
import logging
from datetime import datetime
from .base import TelemetryProvider

_logger = logging.getLogger(__name__)

class SimulatedProvider(TelemetryProvider):
    def __init__(self, interval=0.5, start_lat=19.8221, start_lon=-99.2473, seed=None):
        self.interval = interval
        self._callbacks = []
        self._running = False
        self._thread = None
        self.lat = float(start_lat)
        self.lon = float(start_lon)
        self.alt = 2.0
        self.heading = 0.0
        self.speed = 0.0
        self.voltage = 12.6
        if seed is not None:
            random.seed(seed)

    def register_callback(self, cb):
        self._callbacks.append(cb)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=1)

    @property
    def status(self):
        return 'simulated' if self._running else 'stopped'

    def _loop(self):
        while self._running:
            # small random walk but realistic scale
            dlat = random.uniform(-0.00006, 0.00006)
            dlon = random.uniform(-0.00006, 0.00006)
            self.lat += dlat
            self.lon += dlon
            # approximate meters/sec from degrees (rough)
            self.speed = math.hypot(dlat, dlon) * 111320  # meters per degree
            self.heading = (self.heading + random.uniform(-10, 10)) % 360
            # voltage decay
            self.voltage = max(10.0, self.voltage - random.uniform(0.0005, 0.002))
            payload = {
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'lat': round(self.lat, 6),
                'lon': round(self.lon, 6),
                'alt': round(self.alt + random.uniform(-0.5, 0.5), 2),
                'mode': 'SIMULATED',
                'voltage': round(self.voltage, 2),
                'current': round(random.uniform(0.5, 3.0), 2),
                'speed': round(self.speed, 2),
                'heading': round(self.heading, 2),
                'connection_state': 'simulated',
                'source': 'simulated',
            }
            for cb in list(self._callbacks):
                try:
                    cb(payload)
                except Exception:
                    _logger.exception("SimulatedProvider callback exception")
            time.sleep(self.interval)
