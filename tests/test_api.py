import pytest
from app import create_app
from app.extensions import db
from app.config import TestConfig
import os

@pytest.fixture
def client():
    os.environ['ACCESS_TOKEN'] = 'testtoken'
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        client = app.test_client()
        yield client

def test_system_status(client):
    res = client.get('/api/system/status')
    assert res.status_code == 200

def test_start_mission_requires_token(client):
    res = client.post('/api/missions/start', json={'name': 'X'})
    assert res.status_code == 401
    res2 = client.post('/api/missions/start', headers={'Authorization': 'Bearer testtoken'}, json={'name': 'X'})
    assert res2.status_code == 201
