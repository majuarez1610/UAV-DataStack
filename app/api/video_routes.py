from flask import Blueprint, Response, current_app
from app.services.video_service import VideoService
import time

video_bp = Blueprint('video', __name__)

@video_bp.route('/video_feed')
def video_feed():
    vs = VideoService(current_app.config.get('VIDEO_SOURCE', 0))
    vs.start()

    def generate():
        try:
            while True:
                frame = vs.get_frame()
                if frame is None:
                    # if no frame, wait briefly
                    time.sleep(0.2)
                    continue
                yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        finally:
            vs.stop()

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')
