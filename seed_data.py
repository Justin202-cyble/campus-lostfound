"""演示数据初始化脚本"""

import sqlite3
import os
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash
from config import config


def seed_all():
    """导入所有演示数据"""
    db_path = config.DATABASE
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # 使用北京时间 (UTC+8) 确保时间显示正确
    now = datetime.now(timezone(timedelta(hours=8)))

    # ===== 1. 用户数据 =====
    print("  创建用户...")
    users = [
        ('admin', generate_password_hash('admin123'), 'admin@campus.edu.cn',
         '13800000000', 'admin', '', 'A00001'),
        ('zhangsan', generate_password_hash('123456'), 'zhangsan@campus.edu.cn',
         '13800000001', 'student', '', 'S2024001'),
        ('lisi', generate_password_hash('123456'), 'lisi@campus.edu.cn',
         '13800000002', 'student', '', 'S2024002'),
        ('wangwu', generate_password_hash('123456'), 'wangwu@campus.edu.cn',
         '13800000003', 'student', '', 'S2024003'),
        ('zhaoliu', generate_password_hash('123456'), 'zhaoliu@campus.edu.cn',
         '13800000004', 'student', '', 'S2024004'),
        ('sunqi', generate_password_hash('123456'), 'sunqi@campus.edu.cn',
         '13800000005', 'student', '', 'S2024005'),
        ('zhouba', generate_password_hash('123456'), 'zhouba@campus.edu.cn',
         '13800000006', 'student', '', 'S2024006'),
        ('wujiu', generate_password_hash('123456'), 'wujiu@campus.edu.cn',
         '13800000007', 'student', '', 'S2024007'),
    ]

    for u in users:
        cursor.execute(
            '''INSERT OR IGNORE INTO users
               (username, password, email, phone, role, avatar, student_id)
               VALUES (?, ?, ?, ?, ?, ?, ?)''', u
        )
    conn.commit()

    # ===== 2. 拾物数据 =====
    print("  创建拾物数据...")
    found_items = [
        ('华为MateBook笔记本', 1, '银灰色华为MateBook 14，在图书馆二楼自习室捡到，带保护壳',
         '图书馆二楼自习室', (now - timedelta(days=2, hours=3)).strftime('%Y-%m-%dT%H:%M'),
         '', '请联系微信: zhangsan123', 'pending'),
        ('黑色钱包', 4, '黑色皮质钱包，内有少量现金和一张校园卡',
         '第一食堂二楼', (now - timedelta(days=1, hours=5)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'pending'),
        ('英语四级词汇书', 2, '新东方四级词汇书，书内有一些笔记',
         '教学楼A-301', (now - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'pending'),
        ('校园卡', 3, '校园卡一张，学号S2024005',
         '操场跑道旁', (now - timedelta(hours=12)).strftime('%Y-%m-%dT%H:%M'),
         '', '请到宿管处认领', 'pending'),
        ('蓝牙耳机充电仓', 1, '白色AirPods充电仓，无耳机',
         '教学楼B-205', (now - timedelta(days=1, hours=8)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'claimed'),
        ('蓝色保温杯', 4, '膳魔师蓝色保温杯500ml',
         '体育馆更衣室', (now - timedelta(days=4)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'pending'),
        ('学生证', 3, '计算机学院李四的学生证',
         '图书馆入口处', (now - timedelta(days=2, hours=6)).strftime('%Y-%m-%dT%H:%M'),
         '', '已交至学生事务中心', 'resolved'),
        ('雨伞', 4, '黑色折叠雨伞',
         '教学楼C-102', (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'pending'),
        ('U盘', 1, '金士顿32GB黑色U盘，挂在钥匙扣上',
         '计算机实验室410', (now - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'pending'),
        ('毛呢外套', 5, '驼色女士毛呢外套，L码',
         '图书馆三楼', (now - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'pending'),
    ]

    user_ids = [2, 3, 4, 5, 6, 7, 8]  # 学生用户ID
    for i, item in enumerate(found_items):
        cursor.execute(
            '''INSERT INTO found_items
               (user_id, title, category_id, description, location_found,
                found_time, photo, contact_info, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_ids[i % len(user_ids)], *item,
             (now - timedelta(days=i % 5, hours=i * 2 % 12)).strftime('%Y-%m-%dT%H:%M:%S'))
        )
    conn.commit()

    # ===== 3. 寻物数据 =====
    print("  创建寻物数据...")
    lost_items = [
        ('华为MateBook笔记本', 1, '银灰色华为MateBook 14 Pro，带黑色保护壳，里面有重要学习资料',
         '图书馆二楼', (now - timedelta(days=2, hours=4)).strftime('%Y-%m-%dT%H:%M'),
         '', '急寻！电话: 13900001234', 'open'),
        ('黑色钱包', 4, '黑色Coach钱包，内有身份证和银行卡',
         '第一食堂或教学楼A区', (now - timedelta(days=1, hours=6)).strftime('%Y-%m-%dT%H:%M'),
         '', '重谢！微信: wallet_finder', 'open'),
        ('iPad平板', 1, 'iPad Air 5 蓝色，带白色保护壳和Apple Pencil',
         '图书馆三楼自习区', (now - timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
         '', '电话: 18800005555', 'open'),
        ('钥匙串', 4, '一串钥匙，有宿舍钥匙和U盘，钥匙扣是皮卡丘',
         '操场或体育馆', (now - timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'open'),
        ('校园卡', 3, '校园卡，姓名孙七',
         '食堂或教学楼', (now - timedelta(hours=18)).strftime('%Y-%m-%dT%H:%M'),
         '', '请联系邮箱: sunqi@campus.edu.cn', 'open'),
        ('运动手表', 1, '黑色佳明运动手表',
         '操场跑道', (now - timedelta(days=4)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'found'),
        ('眼镜', 4, '黑色半框近视眼镜，度数约400度',
         '图书馆或教学楼', (now - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'open'),
        ('充电宝', 1, '白色罗马仕20000mAh充电宝',
         '教学楼B栋', (now - timedelta(days=1, hours=10)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'open'),
        ('围巾', 5, '蓝灰格子羊毛围巾',
         '图书馆二楼', (now - timedelta(days=6)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'open'),
        ('数据线', 1, '苹果原装USB-C充电线',
         '计算机实验室', (now - timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
         '', '', 'resolved'),
    ]

    for i, item in enumerate(lost_items):
        cursor.execute(
            '''INSERT INTO lost_items
               (user_id, title, category_id, description, location_lost,
                lost_time, photo, contact_info, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_ids[(i + 1) % len(user_ids)], *item,
             (now - timedelta(days=i % 5, hours=i * 3 % 12)).strftime('%Y-%m-%dT%H:%M:%S'))
        )
    conn.commit()

    # ===== 4. 交换物品数据 =====
    print("  创建交换物品数据...")
    exchange_items = [
        ('机械键盘', 1, '樱桃MX青轴机械键盘，使用半年，功能完好',
         'good', '想换一个静音红轴键盘或蓝牙耳机',
         'available'),
        ('Python编程书籍', 2, '《流畅的Python》第二版，九成新',
         'good', '换《算法导论》或其他计算机经典书籍',
         'available'),
        ('台灯', 4, 'LED护眼台灯，三档调光，使用一年',
         'used', '换一个小风扇或桌面收纳盒',
         'available'),
        ('篮球', 4, '斯伯丁篮球，七成新',
         'used', '换羽毛球拍一副',
         'available'),
        ('耳机', 1, '索尼WH-1000XM4降噪耳机，带原装盒',
         'brand_new', '换iPad或加钱换MacBook',
         'available'),
        ('吉他', 6, '雅马哈F310民谣吉他，送琴包和调音器',
         'good', '换电子琴或尤克里里+差价',
         'available'),
        ('显示器', 1, '戴尔27寸4K显示器U2723QE，使用3个月',
         'brand_new', '换Mac mini或轻薄笔记本',
         'available'),
        ('自行车', 6, '捷安特ATX860山地车，26寸21速',
         'used', '换电动车或平衡车',
         'exchanged'),
    ]

    for i, item in enumerate(exchange_items):
        cursor.execute(
            '''INSERT INTO exchange_items
               (user_id, title, category_id, description, item_condition,
                desired_exchange, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_ids[(i + 2) % len(user_ids)], *item,
             (now - timedelta(days=i % 5, hours=i * 4)).strftime('%Y-%m-%dT%H:%M:%S'))
        )
    conn.commit()

    # ===== 5. 留言数据 =====
    print("  创建留言数据...")
    messages_data = [
        (2, 3, 1, 'found', '你好！我丢了一个华为笔记本，和你捡到的描述很像，请问能看看照片吗？'),
        (3, 2, 1, 'found', '可以的，要不我发给你照片确认一下？'),
        (2, 3, 1, 'found', '太好了！我的笔记本是银灰色的，保护壳也是黑色的。'),
        (3, 2, 1, 'found', '那应该就是你的了，我们约个时间在图书馆见面吧'),
        (4, 5, 1, 'lost', '我看到你在食堂捡到一个钱包，我丢了一个黑色的'),
        (5, 4, 1, 'lost', '请问你的钱包是什么品牌的？里面有什么？'),
        (4, 5, 1, 'lost', '是Coach的，里面有我的身份证，姓赵'),
        (6, 7, 1, 'exchange', '你好，我对你的机械键盘感兴趣，我有一个罗技蓝牙耳机可以交换吗？'),
        (7, 6, 1, 'exchange', '可以的，你的耳机是什么型号？成色如何？'),
    ]

    for msg in messages_data:
        cursor.execute(
            '''INSERT INTO messages
               (sender_id, receiver_id, item_id, item_type, content, created_at)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (*msg, (now - timedelta(hours=len(messages_data) - messages_data.index(msg))).strftime('%Y-%m-%dT%H:%M:%S'))
        )
    conn.commit()

    # ===== 6. 通知数据 =====
    print("  创建通知数据...")
    notifications_data = [
        (2, '🔔 智能匹配提醒', '系统匹配到一件与您丢失的「华为MateBook笔记本」相似度82%的拾物信息',
         'match', 1, 'found'),
        (3, '🔔 智能匹配提醒', '系统匹配到一件与您丢失的「黑色钱包」相似度76%的拾物信息',
         'match', 2, 'found'),
        (2, '💬 收到新留言', 'lisi 在您的拾物「华为MateBook笔记本」下留言了',
         'message', 1, 'found'),
        (4, '📢 系统通知', '欢迎加入智慧校园失物招领平台！请完善您的个人信息',
         'system', None, None),
    ]

    for notif in notifications_data:
        cursor.execute(
            '''INSERT INTO notifications
               (user_id, title, content, notification_type,
                related_item_id, related_item_type, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (*notif, now.strftime('%Y-%m-%dT%H:%M:%S'))
        )
    conn.commit()

    # ===== 7. 匹配日志 =====
    print("  创建匹配记录...")
    match_logs_data = [
        (1, 1, 0.8245, '["华为", "笔记本", "MateBook", "银灰色", "图书馆"]', 'notified'),
        (2, 2, 0.7632, '["钱包", "黑色", "食堂"]', 'notified'),
        (3, 3, 0.6120, '["校园卡", "食堂"]', 'pending'),
    ]

    for mlog in match_logs_data:
        cursor.execute(
            '''INSERT INTO match_logs
               (lost_item_id, found_item_id, similarity_score, matched_keywords, status)
               VALUES (?, ?, ?, ?, ?)''',
            mlog
        )
    conn.commit()

    conn.close()
    print("  演示数据导入完成！")


if __name__ == '__main__':
    from models.database import init_db
    print("初始化数据库...")
    init_db()
    print("导入演示数据...")
    seed_all()
    print("\n完成！现在可以运行 python run.py 启动应用")
