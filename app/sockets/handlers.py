from flask import current_app, request
from app.extensions import socketio

def register_socket_handlers(app):
    # Telemetry namespace (public)
    @socketio.on('connect', namespace='/telemetry')
    def telemetry_connect():
        current_app.logger.info("Client connected to /telemetry")

    @socketio.on('disconnect', namespace='/telemetry')
    def telemetry_disconnect():
        current_app.logger.info("Client disconnected from /telemetry")

    # Control namespace (requires token)
    @socketio.on('connect', namespace='/control')
    def control_connect(auth):
        token = None
        # socket.io v3+ passes auth dict
        if isinstance(auth, dict):
            token = auth.get('token')
        else:
            token = request.args.get('token')
        if token != app.config.get('ACCESS_TOKEN'):
            current_app.logger.warning("Unauthorized control socket connection attempt")
            # abort connection
            raise ConnectionRefusedError('unauthorized')
        current_app.logger.info("Client connected to /control (authorized)")
