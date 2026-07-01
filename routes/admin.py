"""管理后台路由"""

from flask import Blueprint, request, jsonify
from models.database import get_db
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/stats/overview', methods=['GET'])
@admin_required
def stats_overview():
    """管理后台概览统计"""
    db = get_db()

    total_users = db.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_found = db.execute('SELECT COUNT(*) FROM found_items WHERE is_published = 1').fetchone()[0]
    total_lost = db.execute('SELECT COUNT(*) FROM lost_items WHERE is_published = 1').fetchone()[0]
    total_exchange = db.execute('SELECT COUNT(*) FROM exchange_items WHERE is_published = 1').fetchone()[0]
    resolved_found = db.execute("SELECT COUNT(*) FROM found_items WHERE status = 'resolved'").fetchone()[0]
    resolved_lost = db.execute("SELECT COUNT(*) FROM lost_items WHERE status = 'resolved'").fetchone()[0]
    resolved_exchange = db.execute("SELECT COUNT(*) FROM exchange_items WHERE status = 'exchanged'").fetchone()[0]
    active_matches = db.execute("SELECT COUNT(*) FROM match_logs WHERE status = 'pending'").fetchone()[0]

    total_items = total_found + total_lost + total_exchange
    total_resolved = resolved_found + resolved_lost + resolved_exchange
    resolve_rate = round(total_resolved / total_items * 100, 1) if total_items > 0 else 0

    return jsonify({
        'total_users': total_users,
        'total_found': total_found,
        'total_lost': total_lost,
        'total_exchange': total_exchange,
        'total_items': total_items,
        'total_resolved': total_resolved,
        'resolve_rate': resolve_rate,
        'active_matches': active_matches,
    }), 200


@admin_bp.route('/stats/heatmap', methods=['GET'])
@admin_required
def stats_heatmap():
    """失物高发区域分布（热力图数据）"""
    db = get_db()

    # 统计拾物地点分布
    found_locations = db.execute('''
        SELECT location_found as location, COUNT(*) as count
        FROM found_items WHERE is_published = 1
        GROUP BY location_found
        ORDER BY count DESC
    ''').fetchall()

    # 统计丢失地点分布
    lost_locations = db.execute('''
        SELECT location_lost as location, COUNT(*) as count
        FROM lost_items WHERE is_published = 1
        GROUP BY location_lost
        ORDER BY count DESC
    ''').fetchall()

    return jsonify({
        'found_locations': [dict(r) for r in found_locations],
        'lost_locations': [dict(r) for r in lost_locations],
    }), 200


@admin_bp.route('/stats/time-distribution', methods=['GET'])
@admin_required
def stats_time_distribution():
    """时段分布统计"""
    db = get_db()

    # 按小时统计
    hourly_found = db.execute('''
        SELECT CAST(strftime('%H', found_time) AS INTEGER) as hour, COUNT(*) as count
        FROM found_items WHERE is_published = 1
        GROUP BY hour ORDER BY hour
    ''').fetchall()

    hourly_lost = db.execute('''
        SELECT CAST(strftime('%H', lost_time) AS INTEGER) as hour, COUNT(*) as count
        FROM lost_items WHERE is_published = 1
        GROUP BY hour ORDER BY hour
    ''').fetchall()

    # 按星期统计（SQLite: 0=Sunday, 1=Monday, ...）
    weekly_found = db.execute('''
        SELECT CAST(strftime('%w', found_time) AS INTEGER) as day, COUNT(*) as count
        FROM found_items WHERE is_published = 1
        GROUP BY day ORDER BY day
    ''').fetchall()

    weekly_lost = db.execute('''
        SELECT CAST(strftime('%w', lost_time) AS INTEGER) as day, COUNT(*) as count
        FROM lost_items WHERE is_published = 1
        GROUP BY day ORDER BY day
    ''').fetchall()

    day_names = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']

    return jsonify({
        'hourly': {
            'found': [dict(r) for r in hourly_found],
            'lost': [dict(r) for r in hourly_lost],
        },
        'weekly': {
            'found': [{'day': day_names[r['day']], 'count': r['count']} for r in weekly_found],
            'lost': [{'day': day_names[r['day']], 'count': r['count']} for r in weekly_lost],
        },
    }), 200


@admin_bp.route('/stats/category-distribution', methods=['GET'])
@admin_required
def stats_category_distribution():
    """分类分布统计"""
    db = get_db()

    categories = db.execute('SELECT * FROM categories ORDER BY sort_order').fetchall()

    result = []
    for cat in categories:
        found_count = db.execute(
            'SELECT COUNT(*) FROM found_items WHERE category_id = ? AND is_published = 1',
            (cat['id'],)
        ).fetchone()[0]
        lost_count = db.execute(
            'SELECT COUNT(*) FROM lost_items WHERE category_id = ? AND is_published = 1',
            (cat['id'],)
        ).fetchone()[0]
        exchange_count = db.execute(
            'SELECT COUNT(*) FROM exchange_items WHERE category_id = ? AND is_published = 1',
            (cat['id'],)
        ).fetchone()[0]

        result.append({
            'category': cat['name'],
            'icon': cat['icon'],
            'found': found_count,
            'lost': lost_count,
            'exchange': exchange_count,
            'total': found_count + lost_count + exchange_count,
        })

    return jsonify({'categories': result}), 200


@admin_bp.route('/stats/match-statistics', methods=['GET'])
@admin_required
def stats_match_statistics():
    """匹配统计"""
    db = get_db()

    total_matches = db.execute('SELECT COUNT(*) FROM match_logs').fetchone()[0]
    high_matches = db.execute(
        'SELECT COUNT(*) FROM match_logs WHERE similarity_score >= 0.55'
    ).fetchone()[0]
    medium_matches = db.execute(
        'SELECT COUNT(*) FROM match_logs WHERE similarity_score >= 0.40 AND similarity_score < 0.55'
    ).fetchone()[0]
    notified = db.execute(
        "SELECT COUNT(*) FROM match_logs WHERE status = 'notified'"
    ).fetchone()[0]
    resolved = db.execute(
        "SELECT COUNT(*) FROM match_logs WHERE status = 'resolved'"
    ).fetchone()[0]

    # 最近匹配记录
    recent_matches = db.execute('''
        SELECT ml.*,
               li.title as lost_title,
               fi.title as found_title,
               lu.username as lost_user,
               fu.username as found_user
        FROM match_logs ml
        LEFT JOIN lost_items li ON ml.lost_item_id = li.id
        LEFT JOIN found_items fi ON ml.found_item_id = fi.id
        LEFT JOIN users lu ON li.user_id = lu.id
        LEFT JOIN users fu ON fi.user_id = fu.id
        ORDER BY ml.created_at DESC
        LIMIT 20
    ''').fetchall()

    return jsonify({
        'total_matches': total_matches,
        'high_matches': high_matches,
        'medium_matches': medium_matches,
        'notified': notified,
        'resolved': resolved,
        'recent_matches': [dict(r) for r in recent_matches],
    }), 200


@admin_bp.route('/users', methods=['GET'])
@admin_required
def list_users():
    """用户管理列表"""
    db = get_db()
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    try:
        per_page = min(50, max(1, int(request.args.get('per_page', 20))))
    except ValueError:
        per_page = 20

    role = request.args.get('role', '')

    conditions = []
    params = []
    if role:
        conditions.append('role = ?')
        params.append(role)

    where = ' AND '.join(conditions) if conditions else '1 = 1'

    total = db.execute(f'SELECT COUNT(*) FROM users WHERE {where}', params).fetchone()[0]

    offset = (page - 1) * per_page
    users = db.execute(
        f'''SELECT id, username, email, phone, role, student_id, avatar,
                   created_at, updated_at
            FROM users WHERE {where}
            ORDER BY created_at DESC LIMIT ? OFFSET ?''',
        params + [per_page, offset]
    ).fetchall()

    pages = max(1, (total + per_page - 1) // per_page)

    return jsonify({
        'users': [dict(u) for u in users],
        'total': total,
        'page': page,
        'pages': pages,
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """管理员修改用户信息（角色等）"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': '请提供更新信息'}), 400

    db = get_db()

    user = db.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    if not user:
        return jsonify({'error': '用户不存在'}), 404

    updates = []
    values = []

    if 'role' in data and data['role'] in ('student', 'admin'):
        updates.append('role = ?')
        values.append(data['role'])

    if not updates:
        return jsonify({'error': '没有需要更新的字段'}), 400

    updates.append("updated_at = datetime('now', 'localtime')")
    values.append(user_id)

    sql = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
    db.execute(sql, values)
    db.commit()

    return jsonify({'message': '更新成功'}), 200
