import pytest
from app import create_app
from app.extensions import db
from app.repositories import mission_repo, telemetry_repo

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app

def test_create_mission_and_save_telemetry(app):
    mid = mission_repo.create_mission('Test')
    assert mid is not None
    payload = {'lat': 1.0, 'lon': 2.0, 'alt': 3.0, 'mode': 'SIM', 'voltage': 12.0}
    tid = telemetry_repo.save_telemetry(mid, payload)
    assert tid is not None
    latest = telemetry_repo.latest(1)
    assert len(latest) == 1
