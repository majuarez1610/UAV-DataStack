from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import socketio
from app.services.telemetry_service import TelemetryService
from app import extensions as _ext
from app.services.providers.simulated_provider import SimulatedProvider
from app.services.providers.dronekit_provider import DroneKitProvider
import logging

app = create_app()

def start_background_services(app):
    # Autoarranca providers solo en development (DEBUG True)
    if not app.config.get('DEBUG', False):
        app.logger.info("Non-development environment: skipping auto-start of telemetry providers")
        return

    provider_name = app.config.get('TELEMETRY_PROVIDER', 'simulated')
    if provider_name == 'simulated':
        provider = SimulatedProvider(interval=float(app.config.get('TELEMETRY_PERSIST_INTERVAL', 1)))
        telemetry_service = TelemetryService(provider=provider, mission_id=None, app=app)
        telemetry_service.start()
        app.logger.info("Simulated telemetry provider started (development)")
    else:
        # If configured for dronekit and in development, auto-start provider to ease testing
        if provider_name == 'dronekit':
            conn = app.config.get('UAV_CONNECTION')
            provider = DroneKitProvider(connection_string=conn, interval=float(app.config.get('TELEMETRY_PERSIST_INTERVAL', 1)))
            telemetry_service = TelemetryService(provider=provider, mission_id=None, app=app)
            telemetry_service.start()
            # attach provider to control_service so it can access vehicle
            try:
                _ext.control_service.provider = provider
            except Exception:
                app.logger.exception('Failed to attach dronekit provider to control_service')
            app.logger.info(f"DroneKit telemetry provider started (development) -> {conn}")
        else:
            app.logger.info(f"Telemetry provider set to {provider_name}; not auto-started here.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    start_background_services(app)
    socketio.run(
        app,
        host=app.config.get('HOST', '0.0.0.0'),
        port=int(app.config.get('PORT', 5000)),
        debug=app.config.get('DEBUG', False),
    )
