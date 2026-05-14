import logging
from datetime import datetime

from app.extensions import socketio
from app.repositories.telemetry_repo import save_telemetry

_logger = logging.getLogger(__name__)


def _json_safe(value):
    if isinstance(value, datetime):
        return value.isoformat() + "Z"
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


class TelemetryService:
    def __init__(self, provider, mission_id=None, app=None):
        self.provider = provider
        self.mission_id = mission_id
        self.app = app

    def start(self):
        self.provider.register_callback(self.on_data)
        self.provider.start()

    def stop(self):
        self.provider.stop()

    def on_data(self, data):
        ts = data.get("timestamp")
        if isinstance(ts, str):
            try:
                data["timestamp"] = datetime.fromisoformat(ts.rstrip("Z"))
            except Exception:
                data["timestamp"] = datetime.utcnow()
        elif ts is None:
            data["timestamp"] = datetime.utcnow()

        emit_data = _json_safe(dict(data))

        try:
            if self.app:
                with self.app.app_context():
                    save_telemetry(self.mission_id, data)
                    socketio.emit("telemetry.update", emit_data, namespace="/telemetry")
            else:
                save_telemetry(self.mission_id, data)
                socketio.emit("telemetry.update", emit_data, namespace="/telemetry")
        except Exception:
            _logger.exception("Failed to save or emit telemetry")
