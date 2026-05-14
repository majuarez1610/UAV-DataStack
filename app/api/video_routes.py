import time

from flask import Blueprint, Response, abort

from app.utils.auth import require_token

video_bp = Blueprint("video", __name__)


def _get_video_service():
    try:
        from app import extensions as _ext
        return getattr(_ext, "video_service", None)
    except Exception:
        return None


@video_bp.route("/video_feed")
@require_token
def video_feed():
    vs = _get_video_service()
    if not vs:
        abort(503, "Video service not available")

    status = vs.status()
    if not status.get("opened", False):
        abort(503, "Video source not opened")

    deadline = time.time() + 3.0
    first_frame = None
    while time.time() < deadline:
        first_frame = vs.get_frame()
        if first_frame is not None:
            break
        time.sleep(0.1)

    if first_frame is None:
        abort(503, "No frames available")

    def generate():
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + first_frame + b"\r\n"
        while True:
            frame = vs.get_frame()
            if frame is None:
                time.sleep(0.1)
                continue
            yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")
