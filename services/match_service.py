"""智能匹配引擎 - jieba分词 + TF-IDF余弦相似度"""

import json
import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models.database import get_db
from services.notification_service import create_notification

# 中文停用词表
STOP_WORDS = set([
    '的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一',
    '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有',
    '看', '好', '自己', '这', '他', '她', '它', '们', '那', '些', '什么', '怎么',
    '如果', '因为', '所以', '但是', '而且', '或者', '虽然', '可以', '这个', '那个',
    '已经', '还是', '只是', '的话', '把', '被', '让', '给', '从', '向', '对', '与',
    '及', '为', '以', '等', '之', '啊', '吗', '呢', '吧', '哦', '嗯',
])


def _jieba_tokenize(text):
    """jieba分词并去停用词"""
    tokens = jieba.cut(text)
    result = []
    for t in tokens:
        t = t.strip()
        if t and t not in STOP_WORDS and len(t) > 1:
            result.append(t)
    return result


def _compute_location_similarity(loc1, loc2):
    """计算地点Jaccard相似度"""
    if not loc1 or not loc2:
        return 0.0
    set1 = set(_jieba_tokenize(loc1))
    set2 = set(_jieba_tokenize(loc2))
    if not set1 or not set2:
        return 0.0
    intersection = set1 & set2
    union = set1 | set2
    return len(intersection) / len(union)


def _compute_time_score(time1_str, time2_str):
    """计算时间接近度分数"""
    from datetime import datetime, timedelta
    try:
        # 尝试多种时间格式
        for fmt in ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S',
                     '%Y-%m-%d %H:%M', '%Y-%m-%d']:
            try:
                t1 = datetime.strptime(time1_str[:19], fmt)
                t2 = datetime.strptime(time2_str[:19], fmt)
                break
            except ValueError:
                continue
        else:
            return 0.5  # 格式不匹配时给中等分数

        diff_days = abs((t1 - t2).days)
        if diff_days <= 1:
            return 1.0
        elif diff_days <= 3:
            return 0.8
        elif diff_days <= 7:
            return 0.5
        elif diff_days <= 14:
            return 0.3
        else:
            return 0.1
    except Exception:
        return 0.5


def _extract_matched_keywords(lost_text, found_text, common_tokens):
    """提取匹配的关键词"""
    lost_tokens = _jieba_tokenize(lost_text)
    found_tokens = _jieba_tokenize(found_text)
    keywords = list(set(lost_tokens) & set(found_tokens))[:10]
    return keywords


def find_matches_for_item(item_type, item):
    """
    为单个物品查找匹配
    item_type: 'found' 或 'lost'
    item: 物品字典
    返回匹配结果列表
    """
    db = get_db()

    if item_type == 'found':
        # 为拾物寻找匹配的寻物
        candidates = db.execute(
            "SELECT * FROM lost_items WHERE status = 'open' AND is_published = 1"
        ).fetchall()

        item_text = f"{item['title']} {item.get('description', '')} {item.get('location_found', '')}"
        item_location = item.get('location_found', '')
        item_time = item.get('found_time', '')

        matches = []
        for candidate in candidates:
            cand = dict(candidate)
            cand_text = f"{cand['title']} {cand.get('description', '')} {cand.get('location_lost', '')}"
            cand_location = cand.get('location_lost', '')
            cand_time = cand.get('lost_time', '')

            score = _compute_match_score(
                item_text, item_location, item_time,
                cand_text, cand_location, cand_time,
                item.get('category_id'), cand.get('category_id'),
            )

            if score['total'] >= 0.40:
                matches.append({
                    'lost_item': cand,
                    **score,
                })

        matches.sort(key=lambda m: m['total'], reverse=True)
        return matches

    elif item_type == 'lost':
        # 为寻物寻找匹配的拾物
        candidates = db.execute(
            "SELECT * FROM found_items WHERE status = 'pending' AND is_published = 1"
        ).fetchall()

        item_text = f"{item['title']} {item.get('description', '')} {item.get('location_lost', '')}"
        item_location = item.get('location_lost', '')
        item_time = item.get('lost_time', '')

        matches = []
        for candidate in candidates:
            cand = dict(candidate)
            cand_text = f"{cand['title']} {cand.get('description', '')} {cand.get('location_found', '')}"
            cand_location = cand.get('location_found', '')
            cand_time = cand.get('found_time', '')

            score = _compute_match_score(
                item_text, item_location, item_time,
                cand_text, cand_location, cand_time,
                item.get('category_id'), cand.get('category_id'),
            )

            if score['total'] >= 0.40:
                matches.append({
                    'found_item': cand,
                    **score,
                })

        matches.sort(key=lambda m: m['total'], reverse=True)
        return matches

    return []


def _compute_match_score(text1, loc1, time1, text2, loc2, time2, cat_id1, cat_id2):
    """计算综合匹配分数"""
    # 1. 分类匹配 (30%)
    cat_score = 1.0 if cat_id1 == cat_id2 else 0.0

    # 2. 地点相似度 (25%)
    loc_score = _compute_location_similarity(loc1, loc2)

    # 3. 时间接近度 (15%)
    time_score = _compute_time_score(time1, time2)

    # 4. TF-IDF余弦相似度 (30%)
    try:
        all_texts = [text1, text2]
        # 使用jieba分词作为tokenizer
        vectorizer = TfidfVectorizer(
            tokenizer=_jieba_tokenize,
            token_pattern=None,
        )
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        tfidf_score = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
    except Exception:
        tfidf_score = 0.0

    # 综合评分
    total = 0.30 * cat_score + 0.25 * loc_score + 0.15 * time_score + 0.30 * tfidf_score

    return {
        'total': round(total, 4),
        'cat_score': round(cat_score, 4),
        'loc_score': round(loc_score, 4),
        'time_score': round(time_score, 4),
        'tfidf_score': round(tfidf_score, 4),
    }


def notify_high_matches(item_type, item):
    """
    为高分匹配创建通知并记录匹配日志
    """
    matches = find_matches_for_item(item_type, item)
    db = get_db()

    for match in matches:
        if match['total'] < 0.40:
            continue

        if item_type == 'found':
            lost_item = match['lost_item']
            lost_item_id = lost_item['id']
            found_item_id = item['id']
        else:
            found_item = match['found_item']
            lost_item_id = item['id']
            found_item_id = found_item['id']

        # 检查是否已存在匹配记录
        existing = db.execute(
            '''SELECT id FROM match_logs
               WHERE lost_item_id = ? AND found_item_id = ?''',
            (lost_item_id, found_item_id)
        ).fetchone()

        if existing:
            continue

        # 提取匹配关键词
        keywords = _extract_matched_keywords(
            f"{item.get('title','')} {item.get('description','')}",
            f"{match.get('lost_item', match.get('found_item', {})).get('title','')} "
            f"{match.get('lost_item', match.get('found_item', {})).get('description','')}",
            [],
        )

        # 记录匹配日志
        db.execute(
            '''INSERT INTO match_logs (lost_item_id, found_item_id, similarity_score,
                matched_keywords, status)
               VALUES (?, ?, ?, ?, ?)''',
            (lost_item_id, found_item_id, match['total'],
             json.dumps(keywords, ensure_ascii=False),
             'notified' if match['total'] >= 0.55 else 'pending')
        )
        db.commit()

        # 高匹配推送通知
        if match['total'] >= 0.55:
            percentage = int(match['total'] * 100)

            # 通知寻物者
            lost_owner = db.execute(
                'SELECT user_id FROM lost_items WHERE id = ?', (lost_item_id,)
            ).fetchone()
            if lost_owner:
                create_notification(
                    user_id=lost_owner['user_id'],
                    title='🔔 智能匹配提醒',
                    content=f'系统匹配到一件与您丢失物品相似度{percentage}%的拾物信息，点击查看详情',
                    notification_type='match',
                    related_item_id=found_item_id,
                    related_item_type='found',
                )

            # 通知拾物者
            found_owner = db.execute(
                'SELECT user_id FROM found_items WHERE id = ?', (found_item_id,)
            ).fetchone()
            if found_owner:
                create_notification(
                    user_id=found_owner['user_id'],
                    title='🔔 智能匹配提醒',
                    content=f'系统匹配到一件与您拾取物品相似度{percentage}%的寻物信息，可能帮助失主找回',
                    notification_type='match',
                    related_item_id=lost_item_id,
                    related_item_type='lost',
                )


def run_batch_matching():
    """批量运行匹配（周期调用，扫描所有未匹配的物品）"""
    db = get_db()

    open_lost = db.execute(
        "SELECT * FROM lost_items WHERE status = 'open' AND is_published = 1"
    ).fetchall()

    pending_found = db.execute(
        "SELECT * FROM found_items WHERE status = 'pending' AND is_published = 1"
    ).fetchall()

    matched_count = 0
    for lost in open_lost:
        lost_dict = dict(lost)
        for found in pending_found:
            found_dict = dict(found)

            # 检查是否已有匹配
            existing = db.execute(
                'SELECT id FROM match_logs WHERE lost_item_id = ? AND found_item_id = ?',
                (lost_dict['id'], found_dict['id'])
            ).fetchone()
            if existing:
                continue

            lost_text = f"{lost_dict['title']} {lost_dict.get('description','')} {lost_dict.get('location_lost','')}"
            found_text = f"{found_dict['title']} {found_dict.get('description','')} {found_dict.get('location_found','')}"

            score = _compute_match_score(
                lost_text, lost_dict.get('location_lost', ''),
                lost_dict.get('lost_time', ''),
                found_text, found_dict.get('location_found', ''),
                found_dict.get('found_time', ''),
                lost_dict.get('category_id'), found_dict.get('category_id'),
            )

            if score['total'] >= 0.40:
                db.execute(
                    '''INSERT INTO match_logs (lost_item_id, found_item_id, similarity_score, status)
                       VALUES (?, ?, ?, ?)''',
                    (lost_dict['id'], found_dict['id'], score['total'],
                     'notified' if score['total'] >= 0.55 else 'pending')
                )
                matched_count += 1

                if score['total'] >= 0.55:
                    pct = int(score['total'] * 100)
                    create_notification(
                        user_id=lost_dict['user_id'],
                        title='🔔 智能匹配提醒',
                        content=f'系统匹配到一件与您丢失物品相似度{pct}%的拾物信息',
                        notification_type='match',
                        related_item_id=found_dict['id'],
                        related_item_type='found',
                    )
                    create_notification(
                        user_id=found_dict['user_id'],
                        title='🔔 智能匹配提醒',
                        content=f'系统匹配到一件与您拾取物品相似度{pct}%的寻物信息',
                        notification_type='match',
                        related_item_id=lost_dict['id'],
                        related_item_type='lost',
                    )

    db.commit()
    return matched_count
