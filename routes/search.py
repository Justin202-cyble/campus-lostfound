"""搜索 & 分类路由"""

from flask import Blueprint, request, jsonify
from models.database import get_db

search_bp = Blueprint('search', __name__, url_prefix='/api')


@search_bp.route('/categories', methods=['GET'])
def list_categories():
    """获取所有分类"""
    db = get_db()
    categories = db.execute(
        'SELECT * FROM categories ORDER BY sort_order'
    ).fetchall()
    return jsonify({'categories': [dict(c) for c in categories]}), 200


@search_bp.route('/search', methods=['GET'])
def unified_search():
    """统一搜索：跨拾物、寻物、交换物品搜索"""
    q = request.args.get('q', '').strip()
    category_id = request.args.get('category_id', type=int)
    item_type = request.args.get('type', '')  # found / lost / exchange / 空=全部
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    try:
        per_page = min(50, max(1, int(request.args.get('per_page', 12))))
    except ValueError:
        per_page = 12

    if not q and not category_id:
        return jsonify({'error': '请输入搜索关键词或选择分类'}), 400

    db = get_db()
    results = []
    tables = []

    if item_type:
        table_map = {
            'found': 'found_items',
            'lost': 'lost_items',
            'exchange': 'exchange_items',
        }
        if item_type in table_map:
            tables.append((item_type, table_map[item_type]))
        else:
            return jsonify({'error': '无效的物品类型'}), 400
    else:
        tables = [
            ('found', 'found_items'),
            ('lost', 'lost_items'),
            ('exchange', 'exchange_items'),
        ]

    for itype, table in tables:
        conditions = ['is_published = 1']
        params = []

        if q:
            conditions.append('(title LIKE ? OR description LIKE ?)')
            params.extend([f'%{q}%', f'%{q}%'])
        if category_id:
            conditions.append('category_id = ?')
            params.append(category_id)

        where = ' AND '.join(conditions)
        sql = f'''
            SELECT i.*, '{itype}' as item_type,
                   u.username, u.avatar as user_avatar,
                   c.name as category_name, c.icon as category_icon
            FROM {table} i
            JOIN users u ON i.user_id = u.id
            JOIN categories c ON i.category_id = c.id
            WHERE {where}
            ORDER BY i.created_at DESC
        '''
        rows = db.execute(sql, params).fetchall()
        results.extend([dict(r) for r in rows])

    # 按创建时间排序（已在SQL中排序，但合并后需要再排序）
    results.sort(key=lambda x: x.get('created_at', ''), reverse=True)

    # 分页
    total = len(results)
    pages = max(1, (total + per_page - 1) // per_page)
    offset = (page - 1) * per_page
    paged_results = results[offset:offset + per_page]

    return jsonify({
        'items': paged_results,
        'total': total,
        'page': page,
        'pages': pages,
    }), 200
