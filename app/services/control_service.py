import logging

from app.extensions import db
from app.models import EventLog

_logger = logging.getLogger(__name__)


class ControlService:
    def __init__(self, provider=None):
        self.provider = provider

    def _log_event(self, level, etype, message, mission_id=None, data=None):
        try:
            ev = EventLog(mission_id=mission_id, level=level, type=etype, message=message, data=data)
            db.session.add(ev)
            db.session.commit()
        except Exception:
            _logger.exception("Failed to write event log")

    def _get_vehicle(self):
        if self.provider is None:
            return None, None
        v = getattr(self.provider, "vehicle", None)
        if v is None:
            return None, {"ok": False, "message": "Vehicle not connected"}
        return v, None

    def arm(self):
        try:
            vehicle, error = self._get_vehicle()
            if error:
                self._log_event("ERROR", "arm", error["message"])
                return error
            if vehicle is None:
                self._log_event("INFO", "arm", "ARM command executed (simulated)")
                return {"ok": True, "message": "Armed (simulated)"}

            if hasattr(vehicle, "is_armable") and not vehicle.is_armable:
                msg = "Vehicle not armable"
                self._log_event("ERROR", "arm", msg)
                return {"ok": False, "message": msg}

            vehicle.armed = True
            try:
                vehicle.flush()
            except Exception:
                pass
            self._log_event("INFO", "arm", "ARM command executed (vehicle)")
            return {"ok": True, "message": "Armed (vehicle)"}
        except Exception as e:
            _logger.exception("Arm failed")
            self._log_event("ERROR", "arm", f"Arm failed: {e}")
            return {"ok": False, "message": str(e)}

    def disarm(self):
        try:
            vehicle, error = self._get_vehicle()
            if error:
                self._log_event("ERROR", "disarm", error["message"])
                return error
            if vehicle is None:
                self._log_event("INFO", "disarm", "DISARM command executed (simulated)")
                return {"ok": True, "message": "Disarmed (simulated)"}

            vehicle.armed = False
            try:
                vehicle.flush()
            except Exception:
                pass
            self._log_event("INFO", "disarm", "DISARM command executed (vehicle)")
            return {"ok": True, "message": "Disarmed (vehicle)"}
        except Exception as e:
            _logger.exception("Disarm failed")
            self._log_event("ERROR", "disarm", f"Disarm failed: {e}")
            return {"ok": False, "message": str(e)}

    def set_mode(self, mode):
        try:
            vehicle, error = self._get_vehicle()
            if error:
                self._log_event("ERROR", "mode", error["message"])
                return error
            if vehicle is None:
                self._log_event("INFO", "mode", f"Set mode: {mode} (simulated)")
                return {"ok": True, "message": f"Mode set to {mode} (simulated)"}

            from dronekit import VehicleMode

            vehicle.mode = VehicleMode(str(mode).upper())
            try:
                vehicle.flush()
            except Exception:
                pass
            self._log_event("INFO", "mode", f"Set mode: {mode} (vehicle)")
            return {"ok": True, "message": f"Mode set to {mode} (vehicle)"}
        except Exception as e:
            _logger.exception("Set mode failed")
            self._log_event("ERROR", "mode", f"Set mode failed: {e}")
            return {"ok": False, "message": str(e)}

    def mission_start(self):
        try:
            vehicle, error = self._get_vehicle()
            if error:
                self._log_event("ERROR", "mission_start", error["message"])
                return error
            if vehicle is None:
                self._log_event("INFO", "mission_start", "Mission start executed (simulated)")
                return {"ok": True, "message": "Mission start enviado (simulated)"}

            from dronekit import VehicleMode
            from pymavlink import mavutil

            vehicle.mode = VehicleMode("AUTO")
            try:
                vehicle.flush()
            except Exception:
                pass

            msg = vehicle.message_factory.command_long_encode(
                0,
                0,
                mavutil.mavlink.MAV_CMD_MISSION_START,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            )
            vehicle.send_mavlink(msg)
            vehicle.flush()

            self._log_event("INFO", "mission_start", "Mission start command executed (vehicle)")
            return {"ok": True, "message": "Mission start enviado (vehicle)"}
        except Exception as e:
            _logger.exception("Mission start failed")
            self._log_event("ERROR", "mission_start", f"Mission start failed: {e}")
            return {"ok": False, "message": str(e)}
