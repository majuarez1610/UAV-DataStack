from functools import wraps
from flask import request, current_app, jsonify
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from app.models import User
from app.extensions import db
from werkzeug.security import check_password_hash

def require_token(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get('Authorization', '')
        token = None
        if auth.startswith('Bearer '):
            token = auth.split(' ', 1)[1].strip()
        else:
            token = request.args.get('access_token')
        # allow either static ACCESS_TOKEN or user token
        if not token:
            return jsonify({'ok': False, 'error': 'Unauthorized'}), 401

        # static token check
        if token == current_app.config.get('ACCESS_TOKEN') and token != '':
            return fn(*args, **kwargs)

        # otherwise validate signed user token
        s = Serializer(current_app.config.get('SECRET_KEY'), expires_in=3600)
        try:
            data = s.loads(token)
            uid = data.get('user_id')
            if not uid:
                return jsonify({'ok': False, 'error': 'Unauthorized'}), 401
            # optional: attach current_user to flask.g
            return fn(*args, **kwargs)
        except SignatureExpired:
            return jsonify({'ok': False, 'error': 'Token expired'}), 401
        except BadSignature:
            return jsonify({'ok': False, 'error': 'Unauthorized'}), 401
        return fn(*args, **kwargs)
    return wrapper


def generate_user_token(user_id, expires_sec=3600):
    s = Serializer(current_app.config.get('SECRET_KEY'), expires_in=expires_sec)
    return s.dumps({'user_id': user_id}).decode('utf-8')
