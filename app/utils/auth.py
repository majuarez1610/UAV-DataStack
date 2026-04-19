from functools import wraps
from flask import request, current_app, jsonify

def require_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        token = None
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()
        else:
            token = request.args.get('access_token')
        if not token or token != current_app.config.get('ACCESS_TOKEN'):
            return jsonify({'ok': False, 'error': 'Unauthorized'}), 401
        return fn(*args, **kwargs)
    return wrapper
