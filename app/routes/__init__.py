from app.routes import user
from app.routes import admin
from app.routes import api


def init_app(app):
    app.register_blueprint(user.user_bp)
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(api.api_bp)
    user.login_manager.init_app(app)
    user.login_manager.login_view = 'user_bp.index'
    api.set_app(app)
