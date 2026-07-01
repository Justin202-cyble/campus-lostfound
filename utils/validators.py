"""输入校验工具"""

import re


def validate_required(data, fields):
    """验证必填字段"""
    missing = []
    for field in fields:
        if field not in data or not str(data[field]).strip():
            missing.append(field)
    if missing:
        return False, f"缺少必填字段: {', '.join(missing)}"
    return True, ""


def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "邮箱格式不正确"
    return True, ""


def validate_username(username):
    """验证用户名"""
    if len(username) < 2:
        return False, "用户名至少2个字符"
    if len(username) > 20:
        return False, "用户名最多20个字符"
    if not re.match(r'^[\w一-鿿]+$', username):
        return False, "用户名只能包含中文、字母、数字和下划线"
    return True, ""


def validate_password(password):
    """验证密码"""
    if len(password) < 6:
        return False, "密码至少6个字符"
    if len(password) > 50:
        return False, "密码最多50个字符"
    return True, ""


def sanitize_html(text):
    """简易HTML转义"""
    if not text:
        return text
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#x27;')
    return text


def validate_item_data(data, item_type):
    """验证物品数据"""
    errors = []

    if not data.get('title', '').strip():
        errors.append('标题不能为空')
    elif len(data['title']) > 100:
        errors.append('标题最多100个字符')

    if not data.get('category_id'):
        errors.append('请选择分类')
    else:
        try:
            if int(data['category_id']) < 1:
                errors.append('无效的分类')
        except (ValueError, TypeError):
            errors.append('无效的分类')

    if not data.get('description', '').strip():
        errors.append('描述不能为空')

    if item_type == 'found':
        if not data.get('location_found', '').strip():
            errors.append('拾取地点不能为空')
        if not data.get('found_time', '').strip():
            errors.append('拾取时间不能为空')
    elif item_type == 'lost':
        if not data.get('location_lost', '').strip():
            errors.append('丢失地点不能为空')
        if not data.get('lost_time', '').strip():
            errors.append('丢失时间不能为空')
    elif item_type == 'exchange':
        if not data.get('item_condition'):
            errors.append('请选择物品新旧程度')
        if not data.get('desired_exchange', '').strip():
            errors.append('期望交换物品不能为空')

    if errors:
        return False, '; '.join(errors)
    return True, ""
