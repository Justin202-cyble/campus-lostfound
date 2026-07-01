"""Flask 应用工厂 — 智慧校园失物招领与物品交换平台"""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import config
from models.database import init_db, close_db


def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config)

    # 生产环境使用环境变量中的 SECRET_KEY
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', config.SECRET_KEY)

    CORS(app, supports_credentials=True)

    # 确保上传目录存在
    os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

    # 数据库初始化
    init_db()

    # 自动导入演示数据（如果数据库为空）
    _auto_seed_if_empty()

    # 注册数据库清理
    app.teardown_appcontext(close_db)

    # 注册蓝图
    from routes import register_routes
    register_routes(app)

    # ===== SPA 外壳 =====
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')

    # ===== 静态文件 =====
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(app.static_folder, filename)

    # ===== 健康检查 =====
    @app.route('/health')
    def health():
        from flask import jsonify
        return jsonify({'status': 'ok', 'message': '校园失物招领平台运行中'})

    # ===== 错误处理 =====
    @app.errorhandler(404)
    def not_found(e):
        from flask import jsonify
        return jsonify({'error': '资源不存在'}), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import jsonify
        return jsonify({'error': '服务器内部错误'}), 500

    @app.errorhandler(413)
    def too_large(e):
        from flask import jsonify
        return jsonify({'error': '文件大小超出限制（最大16MB）'}), 413

    return app


def _auto_seed_if_empty():
    """如果数据库没有用户数据，自动导入演示数据"""
    import sqlite3
    try:
        conn = sqlite3.connect(config.DATABASE)
        user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        conn.close()

        if user_count == 0:
            print("[启动] 检测到空数据库，自动导入演示数据...")
            from seed_data import seed_all
            seed_all()
            print("[启动] 演示数据导入完成!")
    except Exception as e:
        print(f"[启动] 种子数据检查跳过: {e}")


# ===== 为 gunicorn 等 WSGI 服务器暴露 app 对象 =====
app = create_app()


# ===== 本地开发直接运行 =====
if __name__ == '__main__':
    # 获取本机IP
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.254.254.254', 1))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = '127.0.0.1'

    port = int(os.environ.get('PORT', 5000))

    print("\n" + "=" * 60)
    print("  智慧校园失物招领与物品交换平台")
    print("  Smart Campus Lost & Found Exchange Platform")
    print("=" * 60)
    print(f"\n  📍 本机访问:     http://127.0.0.1:{port}")
    print(f"  👥 局域网访问:   http://{local_ip}:{port}")
    print(f"\n  🔑 演示账号: admin / admin123")
    print(f"  💡 按 Ctrl+C 停止服务\n")

    app.run(debug=True, host='0.0.0.0', port=port)
