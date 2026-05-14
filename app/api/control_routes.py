from flask import Blueprint, jsonify, request

import app.extensions as _ext
from app.utils.auth import require_token

control_bp = Blueprint("control", __name__, url_prefix="/api/uav")


@control_bp.route("/arm", methods=["POST"])
@require_token
def arm():
    cs = getattr(_ext, "control_service", None)
    if not cs:
        return jsonify({"ok": False, "message": "control service unavailable"}), 503
    res = cs.arm()
    status = 200 if res.get("ok") else 503
    return jsonify(res), status


@control_bp.route("/disarm", methods=["POST"])
@require_token
def disarm():
    cs = getattr(_ext, "control_service", None)
    if not cs:
        return jsonify({"ok": False, "message": "control service unavailable"}), 503
    res = cs.disarm()
    status = 200 if res.get("ok") else 503
    return jsonify(res), status


@control_bp.route("/mode", methods=["POST"])
@require_token
def set_mode():
    payload = request.get_json() or {}
    mode = payload.get("mode")
    if not mode:
        return jsonify({"ok": False, "message": "mode required"}), 400
    cs = getattr(_ext, "control_service", None)
    if not cs:
        return jsonify({"ok": False, "message": "control service unavailable"}), 503
    res = cs.set_mode(mode)
    status = 200 if res.get("ok") else 503
    return jsonify(res), status


@control_bp.route("/mission_start", methods=["POST"])
@require_token
def mission_start():
    cs = getattr(_ext, "control_service", None)
    if not cs:
        return jsonify({"ok": False, "message": "control service unavailable"}), 503
    res = cs.mission_start()
    status = 200 if res.get("ok") else 503
    return jsonify(res), status
