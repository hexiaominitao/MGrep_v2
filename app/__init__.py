from flask import (Flask, redirect, url_for, current_app)
from flask_principal import (identity_loaded, UserNeed, RoleNeed)
from flask_login import current_user
from flask_uploads import configure_uploads, patch_request_class

from app.models import db
from app.libs.ext import (bcrypt, login_magager, principal, file_sam, file_okr, file_pdf)


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_name)
    db.init_app(app)
    bcrypt.init_app(app)
    login_magager.init_app(app)
    principal.init_app(app)

    # configure_uploads(app, file_ork) # 配置上传文件
    configure_uploads(app, file_sam)
    configure_uploads(app, file_okr)
    configure_uploads(app, file_pdf)

    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        # 设置当前用户身份为login登录对象
        identity.user = current_user

        # 添加UserNeed到identity user对象
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        # 每个Role添加到identity user对象，roles是User的多对多关联
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    @app.route('/')
    def index():
        return 'Hello'

    from app.api_v2 import api_v2
    from app.download_report.download import home

    app.register_blueprint(api_v2)
    app.register_blueprint(home)

    return app
