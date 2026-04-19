import os
from dotenv import load_dotenv
load_dotenv()

class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'changeme')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///telemetria.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', '')  # intentionally may be empty
    UAV_CONNECTION = os.getenv('UAV_CONNECTION', 'tcp:127.0.0.1:5763')
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    DEBUG = os.getenv('FLASK_DEBUG', '0') == '1'
    TELEMETRY_PROVIDER = os.getenv('TELEMETRY_PROVIDER', 'simulated')
    VIDEO_SOURCE = os.getenv('VIDEO_SOURCE', '0')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')
    TELEMETRY_PERSIST_INTERVAL = float(os.getenv('TELEMETRY_PERSIST_INTERVAL', '1'))
    SOCKETIO_ASYNC_MODE = os.getenv('SOCKETIO_ASYNC_MODE', None)

class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False

class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_TEST_URL', 'sqlite:///:memory:')
