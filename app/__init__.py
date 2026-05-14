import os
from flask import Flask, render_template


def create_app(config_object=None):
    from .config import DevConfig, ProdConfig, TestConfig
    from .extensions import db, socketio, cors
    from .api.routes import api_bp
    from .api.auth_routes import auth_bp
    from .sockets.handlers import register_socket_handlers
    from .api.video_routes import video_bp
    from .api.control_routes import control_bp

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    app = Flask(
        __name__,
        static_folder=os.path.join(base_dir, "static"),
        template_folder=os.path.join(base_dir, "templates"),
    )

    cfg = config_object or os.getenv("FLASK_CONFIG", "development")
    if cfg == "production":
        app.config.from_object(ProdConfig)
    elif cfg == "testing":
        app.config.from_object(TestConfig)
    else:
        app.config.from_object(DevConfig)

    async_mode = app.config.get("SOCKETIO_ASYNC_MODE") or ("threading" if os.name == "nt" else None)

    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}})
    socketio.init_app(
        app,
        cors_allowed_origins=app.config.get("CORS_ORIGINS", "*"),
        async_mode=async_mode,
    )

    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(video_bp)
    app.register_blueprint(control_bp)

    register_socket_handlers(app)

    with app.app_context():
        try:
            db.create_all()
        except Exception:
            app.logger.exception("DB create_all failed")

    from .services.video_service import VideoService
    from .services.control_service import ControlService
    import app.extensions as _ext

    vs_inst = VideoService(app.config.get("VIDEO_SOURCE", 0))
    try:
        vs_inst.start()
    except Exception:
        app.logger.exception("Failed to start VideoService")

    _ext.video_service = vs_inst
    _ext.control_service = ControlService()

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
