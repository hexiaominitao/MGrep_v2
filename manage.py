import os

from flask import current_app
from flask_script import (Manager, Server)
from flask_migrate import (Migrate, MigrateCommand)

from app import create_app
from app.config import DevConfig
from app.models import (db, annotate, mutation, report, run_info)
from app.models.user import User, Role

app = create_app(DevConfig)
manager = Manager(app)
migrate = Migrate(app)

manager.add_command('server', Server())
manager.add_command('db', MigrateCommand)


@manager.shell
def make_shell_content():
    return dict(app=app, db=db)


@manager.shell
def set_up():
    db.create_all()

    admin_role = Role(name='admin')
    admin_role.description = 'admin'
    db.session.add(admin_role)

    super_admin = Role(name='super_admin')
    super_admin.description = 'super_admin'
    db.session.add(super_admin)

    default_role = Role(name='default')
    default_role.description = 'default'
    db.session.add(default_role)

    # default_role = Role(name='default') #添加权限 联系 ext
    # default_role.description = 'default'
    # db.session.add(default_role)

    admin = User(username='admin')
    admin.set_password("hm714012636")
    admin.roles.append(super_admin)
    admin.roles.append(admin_role)
    admin.roles.append(default_role)
    db.session.add(admin)
    db.session.commit()
    # if Role.query.filter(Role.name == 'admin').first():
    #     pass
    # else:
    #     db.session.commit()
    # 文件目录
    dir_static = current_app.config['STATIC_DIR']
    dir_pre_report = current_app.config['PRE_REPORT']
    dir_report = current_app.config['RES_REPORT']
    dir_upload = current_app.config['UPLOADED_FILESAM_DEST']
    for dir in [dir_static, dir_pre_report, dir_report, dir_upload]:
        if not os.path.exists(dir):
            os.mkdir(dir)


if __name__ == '__main__':
    manager.run()
