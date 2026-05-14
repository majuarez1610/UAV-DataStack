import collections
import collections.abc
import logging
import threading
import time
from datetime import datetime

from app.services.providers.base import TelemetryProvider

_logger = logging.getLogger(__name__)


def _patch_py313_for_dronekit():
    aliases = [
        "Mapping",
        "MutableMapping",
        "Sequence",
        "MutableSequence",
        "Set",
        "MutableSet",
        "Iterable",
        "Iterator",
    ]
    for name in aliases:
        if not hasattr(collections, name) and hasattr(collections.abc, name):
            setattr(collections, name, getattr(collections.abc, name))

    try:
        import inspect
        if not hasattr(inspect, "getargspec"):
            inspect.getargspec = inspect.getfullargspec
    except Exception:
        pass


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
                try:
                    self.vehicle.close()
                except Exception:
                    pass
        finally:
            self.vehicle = None

    @property
    def status(self):
        return "connected" if self.vehicle is not None else "disconnected"

    def _connect(self):
        try:
            _patch_py313_for_dronekit()
            from dronekit import connect
            _logger.info("Connecting to vehicle at %s", self.connection_string)
            return connect(self.connection_string, wait_ready=True, heartbeat_timeout=60)
        except Exception:
            _logger.exception("DroneKit connect failed")
            return None

    def _payload_from_vehicle(self, v):
        frame = getattr(v.location, "global_relative_frame", None) or getattr(v.location, "global_frame", None)
        lat = getattr(frame, "lat", None) if frame else None
        lon = getattr(frame, "lon", None) if frame else None
        alt = getattr(frame, "alt", None) if frame else None

        batt = getattr(v, "battery", None)
        voltage = getattr(batt, "voltage", None) if batt else None
        current = getattr(batt, "current", None) if batt else None

        mode = getattr(v, "mode", None)
        if hasattr(mode, "name"):
            mode = mode.name
        elif mode is not None:
            mode = str(mode)

        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "mode": mode,
            "voltage": voltage,
            "current": current,
            "speed": getattr(v, "groundspeed", None) or getattr(v, "airspeed", None),
            "heading": getattr(v, "heading", None) if hasattr(v, "heading") else None,
            "connection_state": "connected",
            "source": "dronekit",
        }
        return payload

    def _loop(self):
        backoff = 1
        while self._running:
            if not self.vehicle:
                v = self._connect()
                if v:
                    with self._lock:
                        self.vehicle = v
                    backoff = 1
                    _logger.info("DroneKit vehicle connected")
                else:
                    _logger.warning("DroneKit connect failed, retrying in %ss", backoff)
                    time.sleep(backoff)
                    backoff = min(backoff * 2, 30)
                    continue

            try:
                with self._lock:
                    v = self.vehicle
                if not v:
                    time.sleep(self.interval)
                    continue

                payload = self._payload_from_vehicle(v)
                for cb in list(self._callbacks):
                    try:
                        cb(payload)
                    except Exception:
                        _logger.exception("DroneKitProvider callback error")
                time.sleep(self.interval)
            except Exception:
                _logger.exception("Error in DroneKitProvider loop; clearing vehicle and attempting reconnect")
                with self._lock:
                    if self.vehicle:
                        try:
                            self.vehicle.close()
                        except Exception:
                            pass
                        self.vehicle = None
                time.sleep(1)
