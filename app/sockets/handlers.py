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

    # Allow control commands via socket (authorized clients)
    @socketio.on('control.command', namespace='/control')
    def on_control_command(data):
        # Basic acknowledgement; actual control service will handle commands in next phase
        current_app.logger.info(f"Received control.command: {data}")
        try:
            action = data.get('action')
            socketio.emit('control.ack', {'ok': True, 'action': action, 'message': 'Received'}, namespace='/control')
        except Exception as e:
            current_app.logger.exception('Error handling control.command')
            socketio.emit('control.ack', {'ok': False, 'message': str(e)}, namespace='/control')
