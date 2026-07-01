"""启动入口 — 一键启动"""

import os
import sys
import socket

# 修复 Windows 控制台 emoji 编码问题
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 确保项目根目录在sys.path中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.database import init_db
from seed_data import seed_all


def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            hostname = socket.gethostname()
            return socket.gethostbyname(hostname)
        except Exception:
            return '未知'


def main():
    local_ip = get_local_ip()

    print("\n" + "=" * 60)
    print("  智慧校园失物招领与物品交换平台")
    print("  Smart Campus Lost & Found Exchange Platform")
    print("=" * 60)

    # 初始化数据库
    print("\n[1/3] 初始化数据库...")
    init_db()

    # 检查是否需要种子数据
    import sqlite3
    from config import config
    conn = sqlite3.connect(config.DATABASE)
    user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    conn.close()

    if user_count == 0:
        print("[2/3] 导入演示数据...")
        seed_all()
        print("       演示数据导入完成!")
    else:
        print("[2/3] 数据库已有数据，跳过种子数据导入")

    # 启动应用
    print("[3/3] 启动Web服务...")
    print()
    print("  " + "=" * 56)
    print("  📍 访问地址")
    print("  " + "=" * 56)
    print(f"  👤 本机访问:     http://127.0.0.1:5000")
    print(f"  👥 局域网访问:   http://{local_ip}:5000")
    print()
    print(f"  🔑 演示账号")
    print(f"     admin    / admin123  (管理员)")
    print(f"     zhangsan / 123456    (学生)")
    print()
    print("  💡 提示：")
    print("     - 其他设备请连接同一WiFi/局域网后访问上面的局域网地址")
    print("     - 如无法访问，请以管理员身份运行 open_firewall.bat")
    print("     - 按 Ctrl+C 停止服务")
    print("  " + "=" * 56)
    print()

    from app import create_app
    app = create_app()

    # 启动定时匹配任务（可选）
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from services.match_service import run_batch_matching

        scheduler = BackgroundScheduler()
        scheduler.add_job(
            func=lambda: run_batch_matching_with_app(app),
            trigger='interval',
            minutes=30,
            id='batch_matching',
            name='智能匹配定期扫描',
            replace_existing=True,
        )
        scheduler.start()
        print("  [定时任务] 智能匹配引擎已启动（每30分钟扫描一次）")
    except ImportError:
        print("  [提示] APScheduler未安装，跳过定时匹配任务")

    app.run(debug=True, host='0.0.0.0', port=5000)


def run_batch_matching_with_app(app):
    """在应用上下文中运行批量匹配"""
    with app.app_context():
        try:
            count = run_batch_matching()
            if count > 0:
                print(f"  [智能匹配] 发现 {count} 条新匹配")
        except Exception as e:
            print(f"  [智能匹配] 匹配失败: {e}")


if __name__ == '__main__':
    main()
