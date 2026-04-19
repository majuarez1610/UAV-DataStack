import logging
from app.extensions import socketio
from app.repositories.telemetry_repo import save_telemetry
from datetime import datetime

_logger = logging.getLogger(__name__)

class TelemetryService:
    def __init__(self, provider, mission_id=None, app=None):
        self.provider = provider
        self.mission_id = mission_id
        # optional Flask app instance to create application context when running in background threads
        self.app = app

    def start(self):
        self.provider.register_callback(self.on_data)
        self.provider.start()

    def stop(self):
        self.provider.stop()

    def on_data(self, data):
        # Normalize timestamp
        ts = data.get('timestamp')
        if isinstance(ts, str):
            try:
                data['timestamp'] = datetime.fromisoformat(ts.rstrip('Z'))
            except Exception:
                data['timestamp'] = datetime.utcnow()
        elif ts is None:
            data['timestamp'] = datetime.utcnow()

        # Persist and emit inside application context if an app was provided
        try:
            if self.app:
                with self.app.app_context():
                    save_telemetry(self.mission_id, data)
                    socketio.emit('telemetry.update', data, namespace='/telemetry')
            else:
                # best effort without explicit app context
                save_telemetry(self.mission_id, data)
                socketio.emit('telemetry.update', data, namespace='/telemetry')
        except Exception:
            _logger.exception("Failed to save or emit telemetry")
