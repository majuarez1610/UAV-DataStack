from flask import Blueprint, jsonify, request, current_app
from app.utils.auth import require_token
from app.repositories import mission_repo, telemetry_repo

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/system/status', methods=['GET'])
def system_status():
    status = {
        'ok': True,
        'uav': current_app.config.get('TELEMETRY_PROVIDER', 'simulated'),
        'db': 'ok',
        'video': False,
    }
    return jsonify(status), 200

@api_bp.route('/missions', methods=['GET'])
def list_missions():
    ms = mission_repo.list_missions()
    out = [{'id': m.id, 'name': m.name, 'status': m.status, 'start_ts': m.start_ts, 'end_ts': m.end_ts} for m in ms]
    return jsonify({'ok': True, 'data': out}), 200

@api_bp.route('/missions/start', methods=['POST'])
@require_token
def start_mission():
    payload = request.get_json() or {}
    name = payload.get('name', 'Misión')
    mid = mission_repo.create_mission(name)
    return jsonify({'ok': True, 'mission_id': mid}), 201

@api_bp.route('/missions/stop', methods=['POST'])
@require_token
def stop_mission():
    payload = request.get_json() or {}
    mission_id = payload.get('mission_id')
    if not mission_id:
        return jsonify({'ok': False, 'error': 'mission_id required'}), 400
    ok = mission_repo.end_mission(mission_id)
    if not ok:
        return jsonify({'ok': False, 'error': 'mission not found'}), 404
    return jsonify({'ok': True}), 200
