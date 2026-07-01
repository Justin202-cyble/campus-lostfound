"""数据库初始化与管理"""

import sqlite3
import os
from flask import g
from config import config


def get_db():
    """获取数据库连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(config.DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
        g.db.execute("PRAGMA journal_mode=WAL")
    return g.db


def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    """初始化数据库表结构"""
    db_path = config.DATABASE

    # 确保数据库目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    # ===== 用户表 =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT    NOT NULL UNIQUE,
            password    TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            phone       TEXT    DEFAULT '',
            role        TEXT    NOT NULL DEFAULT 'student'
                                CHECK(role IN ('student', 'admin')),
            avatar      TEXT    DEFAULT '',
            student_id  TEXT    DEFAULT '',
            created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    # ===== 分类表 =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            icon        TEXT    DEFAULT '',
            sort_order  INTEGER DEFAULT 0
        )
    ''')

    # ===== 拾物表 =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS found_items (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title           TEXT    NOT NULL,
            category_id     INTEGER NOT NULL REFERENCES categories(id),
            description     TEXT    DEFAULT '',
            location_found  TEXT    NOT NULL,
            found_time      TEXT    NOT NULL,
            photo           TEXT    DEFAULT '',
            contact_info    TEXT    DEFAULT '',
            status          TEXT    NOT NULL DEFAULT 'pending'
                                   CHECK(status IN ('pending', 'claimed', 'resolved')),
            is_published    INTEGER NOT NULL DEFAULT 1,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_found_category ON found_items(category_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_found_user ON found_items(user_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_found_status ON found_items(status)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_found_location ON found_items(location_found)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_found_created ON found_items(created_at DESC)
    ''')

    # ===== 寻物表 =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lost_items (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title           TEXT    NOT NULL,
            category_id     INTEGER NOT NULL REFERENCES categories(id),
            description     TEXT    DEFAULT '',
            location_lost   TEXT    NOT NULL,
            lost_time       TEXT    NOT NULL,
            photo           TEXT    DEFAULT '',
            contact_info    TEXT    DEFAULT '',
            status          TEXT    NOT NULL DEFAULT 'open'
                                   CHECK(status IN ('open', 'found', 'resolved')),
            is_published    INTEGER NOT NULL DEFAULT 1,
            created_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at      TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_lost_category ON lost_items(category_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_lost_user ON lost_items(user_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_lost_status ON lost_items(status)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_lost_location ON lost_items(location_lost)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_lost_created ON lost_items(created_at DESC)
    ''')

    # ===== 交换物品表 =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS exchange_items (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id           INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title             TEXT    NOT NULL,
            category_id       INTEGER NOT NULL REFERENCES categories(id),
            description       TEXT    DEFAULT '',
            photo             TEXT    DEFAULT '',
            item_condition    TEXT    NOT NULL DEFAULT 'good'
                                     CHECK(item_condition IN ('brand_new', 'good', 'used', 'worn')),
            desired_exchange  TEXT    DEFAULT '',
            status            TEXT    NOT NULL DEFAULT 'available'
                                     CHECK(status IN ('available', 'exchanged', 'resolved')),
            is_published      INTEGER NOT NULL DEFAULT 1,
            created_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime')),
            updated_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_exchange_category ON exchange_items(category_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_exchange_user ON exchange_items(user_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_exchange_condition ON exchange_items(item_condition)
    ''')

    # ===== 留言表 =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            receiver_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            item_id     INTEGER NOT NULL,
            item_type   TEXT    NOT NULL
                               CHECK(item_type IN ('found', 'lost', 'exchange')),
            content     TEXT    NOT NULL,
            is_read     INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_messages_item ON messages(item_id, item_type)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_messages_thread
            ON messages(sender_id, receiver_id, item_id)
    ''')

    # ===== 通知表 =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id            INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title              TEXT    NOT NULL,
            content            TEXT    NOT NULL,
            notification_type  TEXT    NOT NULL
                                   CHECK(notification_type IN ('match', 'message', 'system')),
            related_item_id    INTEGER,
            related_item_type  TEXT,
            is_read            INTEGER NOT NULL DEFAULT 0,
            created_at         TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_notif_user ON notifications(user_id, is_read)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_notif_created ON notifications(created_at DESC)
    ''')

    # ===== 匹配日志表 =====
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_logs (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            lost_item_id      INTEGER NOT NULL,
            found_item_id     INTEGER NOT NULL,
            similarity_score  REAL    NOT NULL,
            matched_keywords  TEXT    DEFAULT '[]',
            status            TEXT    NOT NULL DEFAULT 'pending'
                                   CHECK(status IN ('pending', 'notified', 'resolved')),
            created_at        TEXT    NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_match_logs_lost ON match_logs(lost_item_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_match_logs_found ON match_logs(found_item_id)
    ''')
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_match_logs_score ON match_logs(similarity_score DESC)
    ''')

    # ===== 初始化分类数据 =====
    categories = [
        (1, '电子产品', '📱', 1),
        (2, '书籍资料', '📚', 2),
        (3, '文件证件', '📄', 3),
        (4, '生活用品', '🎒', 4),
        (5, '服饰配饰', '👗', 5),
        (6, '其他', '📦', 6),
    ]
    for cat in categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (id, name, icon, sort_order)
            VALUES (?, ?, ?, ?)
        ''', cat)

    conn.commit()
    conn.close()
    print("[OK] 数据库表结构初始化完成")


def seed_categories():
    """确保分类数据存在（供外部调用）"""
    conn = sqlite3.connect(config.DATABASE)
    cursor = conn.cursor()
    categories = [
        (1, '电子产品', '📱', 1),
        (2, '书籍资料', '📚', 2),
        (3, '文件证件', '📄', 3),
        (4, '生活用品', '🎒', 4),
        (5, '服饰配饰', '👗', 5),
        (6, '其他', '📦', 6),
    ]
    for cat in categories:
        cursor.execute('''
            INSERT OR IGNORE INTO categories (id, name, icon, sort_order)
            VALUES (?, ?, ?, ?)
        ''', cat)
    conn.commit()
    conn.close()
