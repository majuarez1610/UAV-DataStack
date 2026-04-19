from .extensions import db
from datetime import datetime

class Mission(db.Model):
    __tablename__ = 'missions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(32), nullable=False, default='planned')
    start_ts = db.Column(db.DateTime, nullable=True)
    end_ts = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Telemetry(db.Model):
    __tablename__ = 'telemetry'
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), index=True, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    alt = db.Column(db.Float)
    mode = db.Column(db.String(64))
    voltage = db.Column(db.Float)
    current = db.Column(db.Float)
    speed = db.Column(db.Float)
    heading = db.Column(db.Float)
    connection_state = db.Column(db.String(32))
    source = db.Column(db.String(64))
    raw = db.Column(db.JSON, nullable=True)

class WaterSample(db.Model):
    __tablename__ = 'water_samples'
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), index=True, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ph = db.Column(db.Float)
    turbidity = db.Column(db.Float)
    dissolved_oxygen = db.Column(db.Float)
    conductivity = db.Column(db.Float)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    notes = db.Column(db.Text)

class EventLog(db.Model):
    __tablename__ = 'event_logs'
    id = db.Column(db.Integer, primary_key=True)
    mission_id = db.Column(db.Integer, db.ForeignKey('missions.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    level = db.Column(db.String(16))
    type = db.Column(db.String(64))
    message = db.Column(db.Text)
    data = db.Column(db.JSON)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
