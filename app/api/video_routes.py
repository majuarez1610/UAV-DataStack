from flask import Blueprint, Response, current_app, request, abort
from app.utils.auth import require_token
import time

video_bp = Blueprint('video', __name__)


def _get_video_service():
    # prefer extension-held singleton
    try:
        from app import extensions as _ext
        return getattr(_ext, 'video_service', None)
    except Exception:
        return None


@video_bp.route('/video_feed')
@require_token
def video_feed():
    # Stream MJPEG frames from the singleton VideoService. If not available, return 503.
    vs = _get_video_service()
    if not vs:
        abort(503, 'Video service not available')

    def generate():
        try:
            while True:
                frame = vs.get_frame()
                if frame is None:
                    # if no frame yet, wait briefly
                    time.sleep(0.2)
                    continue
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        finally:
            # do not stop shared singleton here
            return

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
