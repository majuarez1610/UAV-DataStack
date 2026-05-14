import logging
import os

from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app import extensions as _ext
from app.extensions import socketio
from app.services.telemetry_service import TelemetryService
from app.services.providers.dronekit_provider import DroneKitProvider
from app.services.providers.simulated_provider import SimulatedProvider

app = create_app()


def start_background_services(app):
    if not app.config.get("DEBUG", False):
        app.logger.info("Non-development environment: skipping auto-start of telemetry providers")
        return

    provider_name = app.config.get("TELEMETRY_PROVIDER", "simulated")
    interval = float(app.config.get("TELEMETRY_PERSIST_INTERVAL", 1))

    if provider_name == "simulated":
        provider = SimulatedProvider(interval=interval)
        telemetry_service = TelemetryService(provider=provider, mission_id=None, app=app)
        telemetry_service.start()
        app.logger.info("Simulated telemetry provider started (development)")
        return

    if provider_name == "dronekit":
        conn = app.config.get("UAV_CONNECTION")
        provider = DroneKitProvider(connection_string=conn, interval=interval)
        telemetry_service = TelemetryService(provider=provider, mission_id=None, app=app)
        telemetry_service.start()
        try:
            _ext.control_service.provider = provider
        except Exception:
            app.logger.exception("Failed to attach dronekit provider to control_service")
        app.logger.info("DroneKit telemetry provider started (development) -> %s", conn)
        return

    app.logger.info("Telemetry provider set to %s; not auto-started here.", provider_name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    should_start_services = True
    if app.config.get("DEBUG", False):
        should_start_services = os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    if should_start_services:
        start_background_services(app)

    socketio.run(
        app,
        host=app.config.get("HOST", "0.0.0.0"),
        port=int(app.config.get("PORT", 5000)),
        debug=app.config.get("DEBUG", False),
        allow_unsafe_werkzeug=True,
    )
