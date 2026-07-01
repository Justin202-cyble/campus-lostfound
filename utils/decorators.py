"""认证与权限装饰器"""

from functools import wraps
from flask import session, jsonify


def login_required(f):
    """要求用户已登录"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """要求管理员权限"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': '请先登录'}), 401
        if session.get('role') != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    return decorated


def get_current_user_id():
    """获取当前登录用户ID"""
    return session.get('user_id')


def get_current_user_role():
    """获取当前登录用户角色"""
    return session.get('role', 'student')
