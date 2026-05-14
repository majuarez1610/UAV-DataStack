from flask import Blueprint, request, jsonify, current_app
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from itsdangerous import URLSafeTimedSerializer as Serializer

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    payload = request.get_json() or {}
    username = payload.get('username')
    password = payload.get('password')
    if not username or not password:
        return jsonify({'ok': False, 'error': 'username and password required'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'ok': False, 'error': 'username taken'}), 400
    u = User(username=username, password_hash=generate_password_hash(password))
    db.session.add(u)
    db.session.commit()
    return jsonify({'ok': True, 'user_id': u.id}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    payload = request.get_json() or {}
    username = payload.get('username')
    password = payload.get('password')
    if not username or not password:
        return jsonify({'ok': False, 'error': 'username and password required'}), 400
    u = User.query.filter_by(username=username).first()
    if not u or not check_password_hash(u.password_hash, password):
        return jsonify({'ok': False, 'error': 'invalid credentials'}), 401
    s = Serializer(current_app.config.get('SECRET_KEY'))
    token = s.dumps({'user_id': u.id})
    return jsonify({'ok': True, 'token': token}), 200
