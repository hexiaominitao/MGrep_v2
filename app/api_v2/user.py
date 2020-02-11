from flask_restful import (reqparse, Resource)
from flask import (jsonify, current_app)
from flask_login import (login_user, logout_user, current_user)
from flask_principal import Identity, identity_changed

from app.models.user import User


class LoginView(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('userName', required=True,
                                 help='请输入用户名')
        self.parser.add_argument('password', required=True,
                                 help='请输入密码')
        # self.parser.add_argument('token',type=str, required=True,
        #                          help='token')
        super(LoginView, self).__init__()

    def get(self):
        return jsonify({'data': '你好啊Vue,来自FLASK的问候!'})

    def post(self):
        args = self.parser.parse_args()
        username = args.get('userName')
        password = args.get('password')
        user = User.query.filter_by(
            username=username
        ).first()
        # return 'hello'
        if user and user.check_password(password):
            login_user(user)
            identity_changed.send(
                current_app._get_current_object(),
                identity=Identity(user.id)
            )
            return {'token': user.generate_auth_token().decode('ascii'), 'msg': '登录成功!'}
        else:
            return {'msg': '密码或用户名不正确!!!!'}, 401


class LoginOut(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('token', type=str, required=True,
                                 help='token')
        super(LoginOut, self).__init__()

    def get(self):
        return jsonify({'data': '你好啊Vue,来自FLASK的问候!'})

    def post(self):
        # args = self.parser.parse_args()
        # token = args.get('token')
        # print(token)
        return {'msg': 'hello'}, 200


class GetInfo(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('token', type=str, required=True,
                                 help='token')
        super(GetInfo, self).__init__()

    def get(self):
        args = self.parser.parse_args()
        token = args.get('token')
        user = User.verify_auth_token(token)

        if user:
            user_info = {'name': user.username,
                         'user_id': user.id,
                         'access': ['super_admin', 'admin'],
                         'token': token,
                         'avator': 'https://avatars0.githubusercontent.com/u/20942571?s=460&v=4'}
            return user_info
