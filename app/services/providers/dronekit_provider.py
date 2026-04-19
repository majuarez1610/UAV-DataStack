import threading
import time
import logging
from datetime import datetime
from app.services.providers.base import TelemetryProvider

_logger = logging.getLogger(__name__)


class DroneKitProvider(TelemetryProvider):
    def __init__(self, connection_string, interval=0.5, autoreconnect=True):
        self.connection_string = connection_string
        self.interval = interval
        self.autoreconnect = autoreconnect
        self._callbacks = []
        self._running = False
        self._thread = None
        self.vehicle = None
        self._lock = threading.Lock()

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
        try:
            if self.vehicle:
                # attempt graceful close
                try:
                    self.vehicle.close()
                except Exception:
                    pass
        finally:
            self.vehicle = None

    @property
    def status(self):
        return 'connected' if self.vehicle is not None else 'disconnected'

    def _connect(self):
        try:
            # lazy import to avoid hard dependency if not used
            from dronekit import connect
            _logger.info(f"Connecting to vehicle at {self.connection_string}")
            v = connect(self.connection_string, wait_ready=True, heartbeat_timeout=30)
            return v
        except Exception:
            _logger.exception('DroneKit connect failed')
            return None

    def _loop(self):
        backoff = 1
        while self._running:
            if not self.vehicle:
                v = self._connect()
                if v:
                    with self._lock:
                        self.vehicle = v
                    backoff = 1
                    _logger.info('DroneKit vehicle connected')
                else:
                    _logger.warning(f'DroneKit connect failed, retrying in {backoff}s')
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 30)
                    continue

            # read telemetry and send to callbacks
            try:
                with self._lock:
                    v = self.vehicle
                if not v:
                    time.sleep(self.interval)
                    continue
                # gather common fields, guard for attribute access
                lat = getattr(v.location.global_frame, 'lat', None)
                lon = getattr(v.location.global_frame, 'lon', None)
                alt = getattr(v.location.global_frame, 'alt', None)
                mode = getattr(v, 'mode', None)
                voltage = None
                current = None
                # attempt to read battery info
                try:
                    batt = getattr(v, 'battery', None)
                    if batt:
                        voltage = getattr(batt, 'voltage', None)
                except Exception:
                    pass

                payload = {
                    'timestamp': datetime.utcnow().isoformat() + 'Z',
                    'lat': lat,
                    'lon': lon,
                    'alt': alt,
                    'mode': str(mode) if mode is not None else None,
                    'voltage': voltage,
                    'current': current,
                    'speed': getattr(v, 'airspeed', None) or getattr(v, 'groundspeed', None),
                    'heading': getattr(v, 'heading', None) if hasattr(v, 'heading') else None,
                    'connection_state': 'connected',
                    'source': 'dronekit',
                }

                for cb in list(self._callbacks):
                    try:
                        cb(payload)
                    except Exception:
                        _logger.exception('DroneKitProvider callback error')

                time.sleep(self.interval)
            except Exception:
                _logger.exception('Error in DroneKitProvider loop; clearing vehicle and attempting reconnect')
                try:
                    with self._lock:
                        if self.vehicle:
                            try:
                                self.vehicle.close()
                            except Exception:
                                pass
                            self.vehicle = None
                finally:
                    time.sleep(1)
