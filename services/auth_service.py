"""认证业务逻辑"""

import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from models.database import get_db


def hash_password(password):
    """对密码进行哈希"""
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password(password, password_hash):
    """验证密码"""
    return check_password_hash(password_hash, password)


def register_user(username, password, email, phone='', student_id=''):
    """注册新用户"""
    db = get_db()
    try:
        password_hash = hash_password(password)
        cursor = db.execute(
            '''INSERT INTO users (username, password, email, phone, student_id)
               VALUES (?, ?, ?, ?, ?)''',
            (username, password_hash, email, phone, student_id)
        )
        db.commit()
        user_id = cursor.lastrowid

        user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        return dict(user), None
    except sqlite3.IntegrityError as e:
        error_msg = str(e)
        if 'username' in error_msg:
            return None, '用户名已被注册'
        elif 'email' in error_msg:
            return None, '邮箱已被注册'
        return None, '注册失败，请稍后重试'


def authenticate_user(username, password):
    """认证用户登录"""
    db = get_db()
    user = db.execute(
        'SELECT * FROM users WHERE username = ?', (username,)
    ).fetchone()

    if not user:
        return None, '用户名或密码错误'

    user_dict = dict(user)
    if not verify_password(password, user_dict['password']):
        return None, '用户名或密码错误'

    return user_dict, None


def get_user_by_id(user_id):
    """根据ID获取用户"""
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    return dict(user) if user else None


def get_user_public_info(user_id):
    """获取用户公开信息（不含密码）"""
    user = get_user_by_id(user_id)
    if user:
        user.pop('password', None)
    return user


def update_user(user_id, data):
    """更新用户信息"""
    db = get_db()
    allowed_fields = ['phone', 'student_id', 'avatar']
    updates = []
    values = []

    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = ?")
            values.append(data[field])

    if not updates:
        return None, '没有需要更新的字段'

    values.append(user_id)
    sql = f"UPDATE users SET {', '.join(updates)}, updated_at = datetime('now', 'localtime') WHERE id = ?"
    db.execute(sql, values)
    db.commit()

    return get_user_public_info(user_id), None
