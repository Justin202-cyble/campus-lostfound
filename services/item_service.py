"""物品CRUD业务逻辑"""

from models.database import get_db


TABLE_MAP = {
    'found': 'found_items',
    'lost': 'lost_items',
    'exchange': 'exchange_items',
}


def _get_table(item_type):
    """获取物品类型对应的表名"""
    table = TABLE_MAP.get(item_type)
    if not table:
        raise ValueError(f'无效的物品类型: {item_type}')
    return table


def get_items(item_type, page=1, per_page=12, category_id=None, status=None,
              condition=None, user_id=None, q=None):
    """获取物品列表（分页、筛选、搜索）"""
    db = get_db()
    table = _get_table(item_type)

    conditions = ['is_published = 1']
    params = []

    if category_id:
        conditions.append('category_id = ?')
        params.append(int(category_id))

    if status and item_type != 'exchange':
        conditions.append('status = ?')
        params.append(status)

    if condition and item_type == 'exchange':
        conditions.append('item_condition = ?')
        params.append(condition)

    if user_id:
        conditions.append('user_id = ?')
        params.append(int(user_id))

    if q:
        conditions.append('(title LIKE ? OR description LIKE ?)')
        params.extend([f'%{q}%', f'%{q}%'])

    where = ' AND '.join(conditions)

    # 总数
    count_sql = f'SELECT COUNT(*) FROM {table} WHERE {where}'
    total = db.execute(count_sql, params).fetchone()[0]

    # 分页数据
    offset = (page - 1) * per_page
    data_sql = f'''
        SELECT i.*, u.username, u.avatar as user_avatar,
               c.name as category_name, c.icon as category_icon
        FROM {table} i
        JOIN users u ON i.user_id = u.id
        JOIN categories c ON i.category_id = c.id
        WHERE {where}
        ORDER BY i.created_at DESC
        LIMIT ? OFFSET ?
    '''
    items = db.execute(data_sql, params + [per_page, offset]).fetchall()

    pages = max(1, (total + per_page - 1) // per_page)

    return {
        'items': [dict(row) for row in items],
        'total': total,
        'page': page,
        'pages': pages,
        'per_page': per_page,
    }


def get_item_by_id(item_type, item_id):
    """获取单个物品详情"""
    db = get_db()
    table = _get_table(item_type)

    item = db.execute(f'''
        SELECT i.*, u.username, u.avatar as user_avatar, u.student_id,
               c.name as category_name, c.icon as category_icon
        FROM {table} i
        JOIN users u ON i.user_id = u.id
        JOIN categories c ON i.category_id = c.id
        WHERE i.id = ?
    ''', (item_id,)).fetchone()

    return dict(item) if item else None


def create_item(item_type, user_id, data):
    """创建物品"""
    db = get_db()
    table = _get_table(item_type)

    if item_type == 'found':
        sql = f'''INSERT INTO {table}
            (user_id, title, category_id, description, location_found, found_time, photo, contact_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        params = (
            user_id,
            data['title'].strip(),
            int(data['category_id']),
            data.get('description', '').strip(),
            data['location_found'].strip(),
            data['found_time'].strip(),
            data.get('photo', ''),
            data.get('contact_info', '').strip(),
        )
    elif item_type == 'lost':
        sql = f'''INSERT INTO {table}
            (user_id, title, category_id, description, location_lost, lost_time, photo, contact_info)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        params = (
            user_id,
            data['title'].strip(),
            int(data['category_id']),
            data.get('description', '').strip(),
            data['location_lost'].strip(),
            data['lost_time'].strip(),
            data.get('photo', ''),
            data.get('contact_info', '').strip(),
        )
    elif item_type == 'exchange':
        sql = f'''INSERT INTO {table}
            (user_id, title, category_id, description, photo, item_condition, desired_exchange)
            VALUES (?, ?, ?, ?, ?, ?, ?)'''
        params = (
            user_id,
            data['title'].strip(),
            int(data['category_id']),
            data.get('description', '').strip(),
            data.get('photo', ''),
            data.get('item_condition', 'good').strip(),
            data.get('desired_exchange', '').strip(),
        )

    cursor = db.execute(sql, params)
    db.commit()

    return get_item_by_id(item_type, cursor.lastrowid)


def update_item(item_type, item_id, user_id, data, is_admin=False):
    """更新物品（仅所有者或管理员可操作）"""
    db = get_db()
    table = _get_table(item_type)

    # 检查所有权
    item = db.execute(f'SELECT * FROM {table} WHERE id = ?', (item_id,)).fetchone()
    if not item:
        return None, '物品不存在'
    if not is_admin and item['user_id'] != user_id:
        return None, '无权限修改此物品'

    allowed_fields_map = {
        'found': ['title', 'category_id', 'description', 'location_found',
                  'found_time', 'photo', 'contact_info', 'status'],
        'lost': ['title', 'category_id', 'description', 'location_lost',
                 'lost_time', 'photo', 'contact_info', 'status'],
        'exchange': ['title', 'category_id', 'description', 'photo',
                     'item_condition', 'desired_exchange', 'status'],
    }

    allowed_fields = allowed_fields_map.get(item_type, [])
    updates = []
    values = []

    for field in allowed_fields:
        if field in data:
            updates.append(f"{field} = ?")
            val = data[field]
            if isinstance(val, str):
                val = val.strip()
            values.append(val)

    if not updates:
        return get_item_by_id(item_type, item_id), None

    updates.append("updated_at = datetime('now', 'localtime')")
    values.append(item_id)

    sql = f"UPDATE {table} SET {', '.join(updates)} WHERE id = ?"
    db.execute(sql, values)
    db.commit()

    return get_item_by_id(item_type, item_id), None


def delete_item(item_type, item_id, user_id, is_admin=False):
    """删除物品（仅所有者或管理员可操作）"""
    db = get_db()
    table = _get_table(item_type)

    item = db.execute(f'SELECT * FROM {table} WHERE id = ?', (item_id,)).fetchone()
    if not item:
        return False, '物品不存在'
    if not is_admin and item['user_id'] != user_id:
        return False, '无权限删除此物品'

    db.execute(f'DELETE FROM {table} WHERE id = ?', (item_id,))
    db.commit()
    return True, None


def get_recent_items(limit=6):
    """获取首页最近物品"""
    db = get_db()

    found = db.execute('''
        SELECT i.*, 'found' as item_type, u.username, c.name as category_name, c.icon as category_icon
        FROM found_items i
        JOIN users u ON i.user_id = u.id
        JOIN categories c ON i.category_id = c.id
        WHERE i.is_published = 1
        ORDER BY i.created_at DESC LIMIT ?
    ''', (limit,)).fetchall()

    lost = db.execute('''
        SELECT i.*, 'lost' as item_type, u.username, c.name as category_name, c.icon as category_icon
        FROM lost_items i
        JOIN users u ON i.user_id = u.id
        JOIN categories c ON i.category_id = c.id
        WHERE i.is_published = 1
        ORDER BY i.created_at DESC LIMIT ?
    ''', (limit,)).fetchall()

    exchange = db.execute('''
        SELECT i.*, 'exchange' as item_type, u.username, c.name as category_name, c.icon as category_icon
        FROM exchange_items i
        JOIN users u ON i.user_id = u.id
        JOIN categories c ON i.category_id = c.id
        WHERE i.is_published = 1
        ORDER BY i.created_at DESC LIMIT ?
    ''', (limit,)).fetchall()

    return {
        'found': [dict(r) for r in found],
        'lost': [dict(r) for r in lost],
        'exchange': [dict(r) for r in exchange],
    }


def get_home_stats():
    """获取首页统计数据"""
    db = get_db()

    total_found = db.execute(
        'SELECT COUNT(*) FROM found_items WHERE is_published = 1'
    ).fetchone()[0]

    total_lost = db.execute(
        'SELECT COUNT(*) FROM lost_items WHERE is_published = 1'
    ).fetchone()[0]

    total_exchange = db.execute(
        'SELECT COUNT(*) FROM exchange_items WHERE is_published = 1'
    ).fetchone()[0]

    resolved_found = db.execute(
        "SELECT COUNT(*) FROM found_items WHERE status = 'resolved'"
    ).fetchone()[0]

    resolved_lost = db.execute(
        "SELECT COUNT(*) FROM lost_items WHERE status = 'resolved'"
    ).fetchone()[0]

    return {
        'total_found': total_found,
        'total_lost': total_lost,
        'total_exchange': total_exchange,
        'total_resolved': resolved_found + resolved_lost,
    }
