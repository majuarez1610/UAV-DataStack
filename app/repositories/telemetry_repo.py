from app.extensions import db
from app.models import Telemetry
from datetime import datetime

def save_telemetry(mission_id, data: dict):
    t = Telemetry(
        mission_id=mission_id,
        timestamp=data.get('timestamp', datetime.utcnow()),
        lat=data.get('lat'),
        lon=data.get('lon'),
        alt=data.get('alt'),
        mode=data.get('mode'),
        voltage=data.get('voltage'),
        current=data.get('current'),
        speed=data.get('speed'),
        heading=data.get('heading'),
        connection_state=data.get('connection_state'),
        source=data.get('source'),
        raw=data.get('raw'),
    )
    db.session.add(t)
    db.session.commit()
    return t.id

def latest(limit=10):
    return Telemetry.query.order_by(Telemetry.timestamp.desc()).limit(limit).all()
