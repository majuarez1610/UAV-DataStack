from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_cors import CORS

db = SQLAlchemy()
socketio = SocketIO()
cors = CORS()
# runtime service placeholders (to be set by application factory)
video_service = None
control_service = None
