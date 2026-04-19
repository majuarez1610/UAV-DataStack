from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.extensions import socketio
from app.services.providers.simulated_provider import SimulatedProvider
from app.services.telemetry_service import TelemetryService
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
        telemetry_service = TelemetryService(provider=provider, mission_id=None)
        telemetry_service.start()
        app.logger.info("Simulated telemetry provider started (development)")
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
