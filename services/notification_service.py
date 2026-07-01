"""通知服务"""

from models.database import get_db


def create_notification(user_id, title, content, notification_type='system',
                        related_item_id=None, related_item_type=None):
    """创建通知"""
    db = get_db()
    cursor = db.execute(
        '''INSERT INTO notifications (user_id, title, content, notification_type,
            related_item_id, related_item_type)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (user_id, title, content, notification_type,
         related_item_id, related_item_type)
    )
    db.commit()
    return cursor.lastrowid


def get_notifications(user_id, page=1, per_page=20):
    """获取用户通知列表"""
    db = get_db()
    total = db.execute(
        'SELECT COUNT(*) FROM notifications WHERE user_id = ?',
        (user_id,)
    ).fetchone()[0]

    offset = (page - 1) * per_page
    notifications = db.execute(
        '''SELECT * FROM notifications WHERE user_id = ?
           ORDER BY created_at DESC LIMIT ? OFFSET ?''',
        (user_id, per_page, offset)
    ).fetchall()

    pages = max(1, (total + per_page - 1) // per_page)

    return {
        'notifications': [dict(n) for n in notifications],
        'total': total,
        'page': page,
        'pages': pages,
    }


def get_unread_count(user_id):
    """获取未读通知数量"""
    db = get_db()
    count = db.execute(
        'SELECT COUNT(*) FROM notifications WHERE user_id = ? AND is_read = 0',
        (user_id,)
    ).fetchone()[0]
    return count


def mark_as_read(notification_id, user_id):
    """标记单个通知为已读"""
    db = get_db()
    db.execute(
        'UPDATE notifications SET is_read = 1 WHERE id = ? AND user_id = ?',
        (notification_id, user_id)
    )
    db.commit()


def mark_all_as_read(user_id):
    """标记所有通知为已读"""
    db = get_db()
    db.execute(
        'UPDATE notifications SET is_read = 1 WHERE user_id = ?',
        (user_id,)
    )
    db.commit()
