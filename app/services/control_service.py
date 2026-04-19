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
        try:
            if self.provider and getattr(self.provider, 'vehicle', None):
                v = self.provider.vehicle
                # ensure vehicle is armable
                try:
                    if not getattr(v, 'is_armable', True):
                        msg = 'Vehicle not armable'
                        self._log_event('ERROR', 'arm', msg)
                        return {'ok': False, 'message': msg}
                except Exception:
                    # some vehicle objects may not expose is_armable; proceed cautiously
                    pass
                try:
                    v.armed = True
                    self._log_event('INFO', 'arm', 'ARM command executed (vehicle)')
                    return {'ok': True, 'message': 'Armed (vehicle)'}
                except Exception as e:
                    _logger.exception('Arm command to vehicle failed')
                    self._log_event('ERROR', 'arm', f'Arm failed: {e}')
                    return {'ok': False, 'message': str(e)}

            # fallback: simulated
            self._log_event('INFO', 'arm', 'ARM command executed (simulated)')
            return {'ok': True, 'message': 'Armed (simulated)'}
        except Exception as e:
            _logger.exception('Arm failed')
            self._log_event('ERROR', 'arm', f'Arm failed: {e}')
            return {'ok': False, 'message': str(e)}

    def disarm(self):
        try:
            if self.provider and getattr(self.provider, 'vehicle', None):
                v = self.provider.vehicle
                try:
                    v.armed = False
                    self._log_event('INFO', 'disarm', 'DISARM command executed (vehicle)')
                    return {'ok': True, 'message': 'Disarmed (vehicle)'}
                except Exception as e:
                    _logger.exception('Disarm command to vehicle failed')
                    self._log_event('ERROR', 'disarm', f'Disarm failed: {e}')
                    return {'ok': False, 'message': str(e)}

            self._log_event('INFO', 'disarm', 'DISARM command executed (simulated)')
            return {'ok': True, 'message': 'Disarmed (simulated)'}
        except Exception as e:
            _logger.exception('Disarm failed')
            self._log_event('ERROR', 'disarm', f'Disarm failed: {e}')
            return {'ok': False, 'message': str(e)}

    def set_mode(self, mode):
        try:
            if self.provider and getattr(self.provider, 'vehicle', None):
                v = self.provider.vehicle
                try:
                    # DroneKit allows setting v.mode = 'GUIDED' (assignment may be different per API)
                    v.mode = mode
                    self._log_event('INFO', 'mode', f'Set mode: {mode} (vehicle)')
                    return {'ok': True, 'message': f'Mode set to {mode} (vehicle)'}
                except Exception as e:
                    _logger.exception('Set mode to vehicle failed')
                    self._log_event('ERROR', 'mode', f'Set mode failed: {e}')
                    return {'ok': False, 'message': str(e)}

            self._log_event('INFO', 'mode', f'Set mode: {mode} (simulated)')
            return {'ok': True, 'message': f'Mode set to {mode} (simulated)'}
        except Exception as e:
            _logger.exception('Set mode failed')
            self._log_event('ERROR', 'mode', f'Set mode failed: {e}')
            return {'ok': False, 'message': str(e)}
