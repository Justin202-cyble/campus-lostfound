"""应用配置"""

import os


class Config:
    """基础配置"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-campus-secret-key-2024')

    # 数据库（生产环境使用环境变量指定路径）
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATABASE = os.environ.get('DATABASE_PATH', os.path.join(BASE_DIR, 'campus_lostfound.db'))

    # 文件上传
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # 分页
    ITEMS_PER_PAGE = 12

    # 智能匹配
    MATCH_HIGH_THRESHOLD = 0.55  # 高分匹配，推送通知
    MATCH_MEDIUM_THRESHOLD = 0.40  # 中等匹配，记录日志
    MATCH_SCAN_INTERVAL_MINUTES = 30  # 定时扫描间隔


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = DevelopmentConfig()
