from app.extensions import db
from app.models import Mission
from datetime import datetime

def create_mission(name: str) -> int:
    m = Mission(name=name, status='active', start_ts=datetime.utcnow())
    db.session.add(m)
    db.session.commit()
    return m.id

def end_mission(mission_id: int) -> bool:
    m = Mission.query.get(mission_id)
    if not m:
        return False
    m.status = 'finished'
    m.end_ts = datetime.utcnow()
    db.session.commit()
    return True

def list_missions():
    return Mission.query.order_by(Mission.created_at.desc()).all()
