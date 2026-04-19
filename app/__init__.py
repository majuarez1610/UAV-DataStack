import os
from flask import Flask

def create_app(config_object=None):
    from .config import DevConfig, ProdConfig, TestConfig
    from .extensions import db, socketio, cors
    from .api.routes import api_bp
    from .sockets.handlers import register_socket_handlers

    app = Flask(__name__, static_folder="static", template_folder="templates")

    # Config selection by env or explicit param
    cfg = config_object or os.getenv('FLASK_CONFIG', 'development')
    if cfg == 'production':
        app.config.from_object(ProdConfig)
    elif cfg == 'testing':
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(DevConfig)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get('CORS_ORIGINS', '*')}})
    socketio.init_app(app, cors_allowed_origins=app.config.get('CORS_ORIGINS', '*'))

    # Register Blueprints
    app.register_blueprint(api_bp)

    # Register socket handlers (pass socketio later)
    register_socket_handlers(app)

    # Ensure DB tables exist (safe in dev)
    with app.app_context():
        try:
            db.create_all()
        except Exception:
            app.logger.exception("DB create_all failed")

    return app
