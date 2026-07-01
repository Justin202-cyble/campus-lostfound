"""通知路由"""

from flask import Blueprint, request, jsonify
from services.notification_service import (
    get_notifications, get_unread_count,
    mark_as_read, mark_all_as_read,
)
from utils.decorators import login_required, get_current_user_id

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


@notifications_bp.route('', methods=['GET'])
@login_required
def list_notifications():
    """获取通知列表"""
    user_id = get_current_user_id()
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    try:
        per_page = min(50, max(1, int(request.args.get('per_page', 20))))
    except ValueError:
        per_page = 20

    result = get_notifications(user_id, page=page, per_page=per_page)
    return jsonify(result), 200


@notifications_bp.route('/unread-count', methods=['GET'])
@login_required
def unread_count():
    """获取未读通知数"""
    user_id = get_current_user_id()
    count = get_unread_count(user_id)
    return jsonify({'count': count}), 200


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@login_required
def read_notification(notification_id):
    """标记单个通知为已读"""
    user_id = get_current_user_id()
    mark_as_read(notification_id, user_id)
    return jsonify({'message': 'ok'}), 200


@notifications_bp.route('/read-all', methods=['PUT'])
@login_required
def read_all_notifications():
    """标记所有通知为已读"""
    user_id = get_current_user_id()
    mark_all_as_read(user_id)
    return jsonify({'message': 'ok'}), 200
