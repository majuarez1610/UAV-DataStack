import logging
from datetime import datetime
from app.repositories import mission_repo
from app.models import EventLog
from app.extensions import db

_logger = logging.getLogger(__name__)

class ControlService:
    def __init__(self, provider=None):
        # provider is a TelemetryProvider that may expose vehicle for control in real provider
        self.provider = provider

    def _log_event(self, level, etype, message, mission_id=None, data=None):
        try:
            ev = EventLog(mission_id=mission_id, level=level, type=etype, message=message, data=data)
            db.session.add(ev)
            db.session.commit()
        except Exception:
            _logger.exception('Failed to write event log')

    def arm(self):
        # In simulated mode we emulate success
        try:
            # real provider would do: self.provider.vehicle.armed = True
            self._log_event('INFO', 'arm', 'ARM command executed (simulated)')
            return {'ok': True, 'message': 'Armed (simulated)'}
        except Exception as e:
            _logger.exception('Arm failed')
            self._log_event('ERROR', 'arm', f'Arm failed: {e}')
            return {'ok': False, 'message': str(e)}

    def disarm(self):
        try:
            self._log_event('INFO', 'disarm', 'DISARM command executed (simulated)')
            return {'ok': True, 'message': 'Disarmed (simulated)'}
        except Exception as e:
            _logger.exception('Disarm failed')
            self._log_event('ERROR', 'disarm', f'Disarm failed: {e}')
            return {'ok': False, 'message': str(e)}

    def set_mode(self, mode):
        try:
            self._log_event('INFO', 'mode', f'Set mode: {mode} (simulated)')
            return {'ok': True, 'message': f'Mode set to {mode} (simulated)'}
        except Exception as e:
            _logger.exception('Set mode failed')
            self._log_event('ERROR', 'mode', f'Set mode failed: {e}')
            return {'ok': False, 'message': str(e)}
