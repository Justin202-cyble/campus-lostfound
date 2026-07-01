"""认证路由"""

from flask import Blueprint, request, jsonify, session
from services.auth_service import register_user, authenticate_user, get_user_public_info, update_user
from utils.decorators import login_required, get_current_user_id
from utils.validators import validate_required, validate_email, validate_username, validate_password

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供注册信息'}), 400

    # 验证必填字段
    ok, msg = validate_required(data, ['username', 'password', 'email'])
    if not ok:
        return jsonify({'error': msg}), 400

    # 验证用户名
    ok, msg = validate_username(data['username'])
    if not ok:
        return jsonify({'error': msg}), 400

    # 验证密码
    ok, msg = validate_password(data['password'])
    if not ok:
        return jsonify({'error': msg}), 400

    # 验证邮箱
    ok, msg = validate_email(data['email'])
    if not ok:
        return jsonify({'error': msg}), 400

    user, error = register_user(
        username=data['username'],
        password=data['password'],
        email=data['email'],
        phone=data.get('phone', ''),
        student_id=data.get('student_id', ''),
    )

    if error:
        return jsonify({'error': error}), 400

    # 注册成功，自动登录
    user.pop('password', None)
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']

    return jsonify({'user': user, 'message': '注册成功'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供登录信息'}), 400

    ok, msg = validate_required(data, ['username', 'password'])
    if not ok:
        return jsonify({'error': msg}), 400

    user, error = authenticate_user(data['username'], data['password'])
    if error:
        return jsonify({'error': error}), 401

    user.pop('password', None)
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['role'] = user['role']

    return jsonify({'user': user, 'message': '登录成功'}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({'message': '已退出登录'}), 200


@auth_bp.route('/me', methods=['GET'])
@login_required
def me():
    """获取当前登录用户信息"""
    user = get_user_public_info(get_current_user_id())
    if not user:
        session.clear()
        return jsonify({'error': '用户不存在'}), 401
    return jsonify({'user': user}), 200


@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新个人信息"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供更新信息'}), 400

    user, error = update_user(get_current_user_id(), data)
    if error:
        return jsonify({'error': error}), 400

    return jsonify({'user': user, 'message': '更新成功'}), 200
