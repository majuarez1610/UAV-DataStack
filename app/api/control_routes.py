from flask import Blueprint, jsonify, request, current_app
from app.utils.auth import require_token
import app.extensions as _ext

control_bp = Blueprint('control', __name__, url_prefix='/api/uav')

@control_bp.route('/arm', methods=['POST'])
@require_token
def arm():
    cs = getattr(_ext, 'control_service', None)
    if not cs:
        return jsonify({'ok': False, 'message': 'control service unavailable'}), 503
    res = cs.arm()
    status = 200 if res.get('ok') else 500
    return jsonify(res), status

@control_bp.route('/disarm', methods=['POST'])
@require_token
def disarm():
    cs = getattr(_ext, 'control_service', None)
    if not cs:
        return jsonify({'ok': False, 'message': 'control service unavailable'}), 503
    res = cs.disarm()
    status = 200 if res.get('ok') else 500
    return jsonify(res), status

@control_bp.route('/mode', methods=['POST'])
@require_token
def set_mode():
    payload = request.get_json() or {}
    mode = payload.get('mode')
    if not mode:
        return jsonify({'ok': False, 'message': 'mode required'}), 400
    cs = getattr(_ext, 'control_service', None)
    if not cs:
        return jsonify({'ok': False, 'message': 'control service unavailable'}), 503
    res = cs.set_mode(mode)
    status = 200 if res.get('ok') else 500
    return jsonify(res), status
