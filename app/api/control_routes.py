from flask import Blueprint, jsonify, request, current_app
from app.utils.auth import require_token
from app.extensions import control_service

control_bp = Blueprint('control', __name__, url_prefix='/api/uav')

@control_bp.route('/arm', methods=['POST'])
@require_token
def arm():
    res = control_service.arm()
    status = 200 if res.get('ok') else 500
    return jsonify(res), status

@control_bp.route('/disarm', methods=['POST'])
@require_token
def disarm():
    res = control_service.disarm()
    status = 200 if res.get('ok') else 500
    return jsonify(res), status

@control_bp.route('/mode', methods=['POST'])
@require_token
def set_mode():
    payload = request.get_json() or {}
    mode = payload.get('mode')
    if not mode:
        return jsonify({'ok': False, 'message': 'mode required'}), 400
    res = control_service.set_mode(mode)
    status = 200 if res.get('ok') else 500
    return jsonify(res), status
