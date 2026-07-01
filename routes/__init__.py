"""蓝图注册"""

from routes.auth import auth_bp
from routes.items import items_bp
from routes.search import search_bp
from routes.messages import messages_bp
from routes.notifications import notifications_bp
from routes.admin import admin_bp


def register_routes(app):
    """向Flask应用注册所有蓝图"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(admin_bp)
