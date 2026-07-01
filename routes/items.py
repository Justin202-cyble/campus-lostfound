"""物品路由（拾物/寻物/交换）"""

import os
from flask import Blueprint, request, jsonify
from services.item_service import (
    get_items, get_item_by_id, create_item, update_item, delete_item,
    get_recent_items, get_home_stats,
)
from services.match_service import find_matches_for_item, notify_high_matches
from utils.decorators import login_required, get_current_user_id, get_current_user_role
from utils.validators import validate_item_data
from utils.upload import save_photo

items_bp = Blueprint('items', __name__, url_prefix='/api/items')


# ===== 辅助函数 =====

def _parse_pagination():
    """解析分页参数"""
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    try:
        per_page = min(50, max(1, int(request.args.get('per_page', 12))))
    except ValueError:
        per_page = 12
    return page, per_page


# ===== 列表接口 =====

@items_bp.route('/found', methods=['GET'])
def list_found():
    """拾物列表"""
    page, per_page = _parse_pagination()
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    q = request.args.get('q')

    result = get_items('found', page=page, per_page=per_page,
                       category_id=category_id, status=status, q=q)
    return jsonify(result), 200


@items_bp.route('/lost', methods=['GET'])
def list_lost():
    """寻物列表"""
    page, per_page = _parse_pagination()
    category_id = request.args.get('category_id', type=int)
    status = request.args.get('status')
    q = request.args.get('q')

    result = get_items('lost', page=page, per_page=per_page,
                       category_id=category_id, status=status, q=q)
    return jsonify(result), 200


@items_bp.route('/exchange', methods=['GET'])
def list_exchange():
    """交换物品列表"""
    page, per_page = _parse_pagination()
    category_id = request.args.get('category_id', type=int)
    condition = request.args.get('condition')
    q = request.args.get('q')

    result = get_items('exchange', page=page, per_page=per_page,
                       category_id=category_id, condition=condition, q=q)
    return jsonify(result), 200


# ===== 详情接口 =====

@items_bp.route('/found/<int:item_id>', methods=['GET'])
def detail_found(item_id):
    """拾物详情"""
    item = get_item_by_id('found', item_id)
    if not item:
        return jsonify({'error': '物品不存在'}), 404
    return jsonify({'item': item}), 200


@items_bp.route('/lost/<int:item_id>', methods=['GET'])
def detail_lost(item_id):
    """寻物详情"""
    item = get_item_by_id('lost', item_id)
    if not item:
        return jsonify({'error': '物品不存在'}), 404
    return jsonify({'item': item}), 200


@items_bp.route('/exchange/<int:item_id>', methods=['GET'])
def detail_exchange(item_id):
    """交换物品详情"""
    item = get_item_by_id('exchange', item_id)
    if not item:
        return jsonify({'error': '物品不存在'}), 404
    return jsonify({'item': item}), 200


# ===== 创建接口 =====

@items_bp.route('/found', methods=['POST'])
@login_required
def create_found():
    """发布拾物信息"""
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    ok, msg = validate_item_data(data, 'found')
    if not ok:
        return jsonify({'error': msg}), 400

    # 处理图片上传
    if 'photo_file' in request.files:
        photo_path, error = save_photo(request.files['photo_file'])
        if error:
            return jsonify({'error': error}), 400
        data['photo'] = photo_path

    item = create_item('found', get_current_user_id(), data)
    if not item:
        return jsonify({'error': '发布失败'}), 500

    # 触发智能匹配
    try:
        find_matches_for_item('found', item)
    except Exception:
        pass  # 匹配失败不影响发布

    return jsonify({'item': item, 'message': '发布成功'}), 201


@items_bp.route('/lost', methods=['POST'])
@login_required
def create_lost():
    """发布寻物信息"""
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    ok, msg = validate_item_data(data, 'lost')
    if not ok:
        return jsonify({'error': msg}), 400

    # 处理图片上传
    if 'photo_file' in request.files:
        photo_path, error = save_photo(request.files['photo_file'])
        if error:
            return jsonify({'error': error}), 400
        data['photo'] = photo_path

    item = create_item('lost', get_current_user_id(), data)
    if not item:
        return jsonify({'error': '发布失败'}), 500

    # 触发智能匹配
    try:
        find_matches_for_item('lost', item)
    except Exception:
        pass

    return jsonify({'item': item, 'message': '发布成功'}), 201


@items_bp.route('/exchange', methods=['POST'])
@login_required
def create_exchange():
    """发布交换物品"""
    data = request.form.to_dict() if request.form else (request.get_json(silent=True) or {})

    ok, msg = validate_item_data(data, 'exchange')
    if not ok:
        return jsonify({'error': msg}), 400

    # 处理图片上传
    if 'photo_file' in request.files:
        photo_path, error = save_photo(request.files['photo_file'])
        if error:
            return jsonify({'error': error}), 400
        data['photo'] = photo_path

    item = create_item('exchange', get_current_user_id(), data)
    if not item:
        return jsonify({'error': '发布失败'}), 500

    return jsonify({'item': item, 'message': '发布成功'}), 201


# ===== 更新接口 =====

@items_bp.route('/found/<int:item_id>', methods=['PUT'])
@login_required
def update_found(item_id):
    """更新拾物信息"""
    data = request.get_json(silent=True) or {}
    is_admin = get_current_user_role() == 'admin'
    item, error = update_item('found', item_id, get_current_user_id(), data, is_admin)
    if error:
        code = 403 if '权限' in error else 404
        return jsonify({'error': error}), code
    return jsonify({'item': item, 'message': '更新成功'}), 200


@items_bp.route('/lost/<int:item_id>', methods=['PUT'])
@login_required
def update_lost(item_id):
    """更新寻物信息"""
    data = request.get_json(silent=True) or {}
    is_admin = get_current_user_role() == 'admin'
    item, error = update_item('lost', item_id, get_current_user_id(), data, is_admin)
    if error:
        code = 403 if '权限' in error else 404
        return jsonify({'error': error}), code
    return jsonify({'item': item, 'message': '更新成功'}), 200


@items_bp.route('/exchange/<int:item_id>', methods=['PUT'])
@login_required
def update_exchange(item_id):
    """更新交换物品信息"""
    data = request.get_json(silent=True) or {}
    is_admin = get_current_user_role() == 'admin'
    item, error = update_item('exchange', item_id, get_current_user_id(), data, is_admin)
    if error:
        code = 403 if '权限' in error else 404
        return jsonify({'error': error}), code
    return jsonify({'item': item, 'message': '更新成功'}), 200


# ===== 删除接口 =====

@items_bp.route('/found/<int:item_id>', methods=['DELETE'])
@login_required
def delete_found(item_id):
    """删除拾物信息"""
    is_admin = get_current_user_role() == 'admin'
    success, error = delete_item('found', item_id, get_current_user_id(), is_admin)
    if not success:
        code = 403 if '权限' in error else 404
        return jsonify({'error': error}), code
    return jsonify({'message': '删除成功'}), 200


@items_bp.route('/lost/<int:item_id>', methods=['DELETE'])
@login_required
def delete_lost(item_id):
    """删除寻物信息"""
    is_admin = get_current_user_role() == 'admin'
    success, error = delete_item('lost', item_id, get_current_user_id(), is_admin)
    if not success:
        code = 403 if '权限' in error else 404
        return jsonify({'error': error}), code
    return jsonify({'message': '删除成功'}), 200


@items_bp.route('/exchange/<int:item_id>', methods=['DELETE'])
@login_required
def delete_exchange(item_id):
    """删除交换物品信息"""
    is_admin = get_current_user_role() == 'admin'
    success, error = delete_item('exchange', item_id, get_current_user_id(), is_admin)
    if not success:
        code = 403 if '权限' in error else 404
        return jsonify({'error': error}), code
    return jsonify({'message': '删除成功'}), 200


# ===== 首页数据 =====

@items_bp.route('/home/recent', methods=['GET'])
def home_recent():
    """首页最近物品"""
    result = get_recent_items(limit=6)
    return jsonify(result), 200


@items_bp.route('/home/stats', methods=['GET'])
def home_stats():
    """首页统计"""
    result = get_home_stats()
    return jsonify(result), 200
