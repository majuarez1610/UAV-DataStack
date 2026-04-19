from flask import Blueprint, jsonify, request, current_app
from app.utils.auth import require_token
from app.repositories import mission_repo, telemetry_repo
from flask import current_app, Response
from app.utils.auth import require_token

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


@api_bp.route('/telemetry/latest', methods=['GET'])
def telemetry_latest():
    try:
        t = telemetry_repo.latest(limit=20)
        out = []
        for item in t:
            out.append({
                'id': item.id,
                'mission_id': item.mission_id,
                'timestamp': item.timestamp.isoformat() if item.timestamp else None,
                'lat': item.lat,
                'lon': item.lon,
                'alt': item.alt,
                'mode': item.mode,
                'voltage': item.voltage,
                'current': item.current,
                'speed': item.speed,
                'heading': item.heading,
                'source': item.source,
            })
        return jsonify({'ok': True, 'data': out}), 200
    except Exception:
        current_app.logger.exception('Failed to get latest telemetry')
        return jsonify({'ok': False, 'error': 'internal error'}), 500

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


@api_bp.route('/video/status', methods=['GET'])
def video_status():
    # Report status of singleton VideoService if present
    try:
        from app import extensions as _ext
        vs = getattr(_ext, 'video_service', None)
        if not vs:
            return jsonify({'ok': True, 'video': {'available': False}}), 200
        st = vs.status()
        return jsonify({'ok': True, 'video': st}), 200
    except Exception:
        current_app.logger.exception('video_status check failed')
        return jsonify({'ok': True, 'video': {'available': False}}), 200
