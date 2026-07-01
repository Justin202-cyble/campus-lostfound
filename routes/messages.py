"""留言互动路由"""

from flask import Blueprint, request, jsonify
from models.database import get_db
from services.notification_service import create_notification
from utils.decorators import login_required, get_current_user_id
from utils.validators import sanitize_html

messages_bp = Blueprint('messages', __name__, url_prefix='/api/messages')


@messages_bp.route('/conversations', methods=['GET'])
@login_required
def list_conversations():
    """获取当前用户的所有对话列表"""
    user_id = get_current_user_id()
    db = get_db()

    # 1. 先获取所有涉及我的对话（去重）
    rows = db.execute('''
        SELECT DISTINCT
            CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END as other_user_id,
            item_id,
            item_type
        FROM messages
        WHERE sender_id = ? OR receiver_id = ?
        ORDER BY item_id
    ''', (user_id, user_id, user_id)).fetchall()

    # 2. 为每个对话补充用户信息和统计
    conversations = []
    for row in rows:
        other_id = row['other_user_id']
        item_id = row['item_id']
        item_type = row['item_type']

        # 获取对方用户信息
        other_user = db.execute(
            'SELECT id, username, avatar FROM users WHERE id = ?',
            (other_id,)
        ).fetchone()
        if not other_user:
            continue

        # 未读消息数
        unread = db.execute(
            '''SELECT COUNT(*) FROM messages
               WHERE receiver_id = ? AND sender_id = ?
                 AND item_id = ? AND item_type = ?
                 AND is_read = 0''',
            (user_id, other_id, item_id, item_type)
        ).fetchone()[0]

        # 最后一条消息
        last_msg = db.execute(
            '''SELECT content, created_at FROM messages
               WHERE item_id = ? AND item_type = ?
                 AND ((sender_id = ? AND receiver_id = ?)
                      OR (sender_id = ? AND receiver_id = ?))
               ORDER BY created_at DESC LIMIT 1''',
            (item_id, item_type, user_id, other_id, other_id, user_id)
        ).fetchone()

        conversations.append({
            'other_user_id': other_id,
            'item_id': item_id,
            'item_type': item_type,
            'username': other_user['username'],
            'avatar': other_user['avatar'],
            'unread_count': unread,
            'last_message': last_msg['content'] if last_msg else '',
            'last_time': last_msg['created_at'] if last_msg else '',
        })

    # 按最后消息时间排序
    conversations.sort(key=lambda c: c['last_time'], reverse=True)

    return jsonify({'conversations': conversations}), 200


@messages_bp.route('', methods=['GET'])
@login_required
def get_thread():
    """获取与指定用户关于指定物品的对话"""
    user_id = get_current_user_id()
    other_user_id = request.args.get('user_id', type=int)
    item_id = request.args.get('item_id', type=int)
    item_type = request.args.get('item_type', '')

    if not other_user_id or not item_id or not item_type:
        return jsonify({'error': '参数不完整'}), 400

    db = get_db()
    messages = db.execute('''
        SELECT m.*, u.username as sender_name, u.avatar as sender_avatar
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.item_id = ? AND m.item_type = ?
          AND ((m.sender_id = ? AND m.receiver_id = ?)
               OR (m.sender_id = ? AND m.receiver_id = ?))
        ORDER BY m.created_at ASC
    ''', (item_id, item_type, user_id, other_user_id, other_user_id, user_id)).fetchall()

    # 标记对方发来的消息为已读
    db.execute('''
        UPDATE messages SET is_read = 1
        WHERE receiver_id = ? AND sender_id = ? AND item_id = ? AND item_type = ?
    ''', (user_id, other_user_id, item_id, item_type))
    db.commit()

    return jsonify({'messages': [dict(m) for m in messages]}), 200


@messages_bp.route('', methods=['POST'])
@login_required
def send_message():
    """发送留言"""
    user_id = get_current_user_id()
    data = request.get_json(silent=True)

    if not data:
        return jsonify({'error': '请提供留言内容'}), 400

    receiver_id = data.get('receiver_id')
    item_id = data.get('item_id')
    item_type = data.get('item_type')
    content = data.get('content', '').strip()

    if not receiver_id or not item_id or not item_type:
        return jsonify({'error': '参数不完整，缺少 receiver_id/item_id/item_type'}), 400

    if not content:
        return jsonify({'error': '留言内容不能为空'}), 400

    if len(content) > 1000:
        return jsonify({'error': '留言内容最多1000个字符'}), 400

    content = sanitize_html(content)

    db = get_db()
    cursor = db.execute(
        '''INSERT INTO messages (sender_id, receiver_id, item_id, item_type, content)
           VALUES (?, ?, ?, ?, ?)''',
        (user_id, receiver_id, item_id, item_type, content)
    )
    db.commit()

    # 获取刚创建的消息
    message = db.execute('''
        SELECT m.*, u.username as sender_name, u.avatar as sender_avatar
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.id = ?
    ''', (cursor.lastrowid,)).fetchone()

    # 给接收方发通知
    sender = db.execute('SELECT username FROM users WHERE id = ?', (user_id,)).fetchone()
    item_label = {'found': '拾物', 'lost': '寻物', 'exchange': '交换'}.get(item_type, '物品')

    table_map = {'found': 'found_items', 'lost': 'lost_items', 'exchange': 'exchange_items'}
    item_title = f'{item_label}#{item_id}'
    if item_type in table_map:
        item_row = db.execute(
            f"SELECT title FROM {table_map[item_type]} WHERE id = ?", (item_id,)
        ).fetchone()
        if item_row:
            item_title = item_row['title']

    create_notification(
        user_id=receiver_id,
        title='收到新留言',
        content=f"{sender['username']} 在您的{item_label}「{item_title}」下留言了",
        notification_type='message',
        related_item_id=item_id,
        related_item_type=item_type,
    )

    return jsonify({'message': dict(message), 'info': '发送成功'}), 201


@messages_bp.route('/unread-count', methods=['GET'])
@login_required
def unread_count():
    """获取未读消息数"""
    user_id = get_current_user_id()
    db = get_db()
    count = db.execute(
        'SELECT COUNT(*) FROM messages WHERE receiver_id = ? AND is_read = 0',
        (user_id,)
    ).fetchone()[0]
    return jsonify({'count': count}), 200
