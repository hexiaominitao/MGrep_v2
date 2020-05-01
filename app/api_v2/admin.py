import json, os

from flask import (jsonify, current_app)
from flask_restful import (reqparse, Resource, fields, request)

from app.models import db
from app.models.user import User, Role
from app.libs.get_data import read_json, splitN


class AdminSample(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('page_per', type=int, help='每页数量')
        self.parser.add_argument('id', type=int, help='样本id')

    def get(self):
        args = self.parser.parse_args()
        page = args.get('page')
        page_per = args.get('page_per')
        dir_app = current_app.config['PRE_REPORT']
        dir_sample = os.path.join(dir_app, 'sample', 'sample.json')
        sams = read_json(dir_sample, 'sample_info')[0]['sams']
        pagenation_sam = [sam for sam in splitN(sams, page_per)]
        dict_sam = {}
        dict_sam['sample'] = pagenation_sam[page]
        dict_sam['total'] = len(sams)
        return jsonify(dict_sam)

    # def post(self):
    #     args = self.parser.parse_args()
    #     id = args.get('id')
    #     dir_app = current_app.config['PRE_REPORT']
    #     dir_sample = os.path.join(dir_app, 'sample', 'sample.json')
    #     sams = read_json(dir_sample)['样本信息登记表'][0]['样本信息登记表']
    #     mg = sam.mg_id
    #     db.session.delete(sam)
    #     db.session.commit()
    #     return {'msg': '{}删除成功'.format(mg)}, 200


class AdminTemplate(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()

    def get(self):
        dir_app = current_app.config['PRE_REPORT']
        dir_pgm_remplate = os.path.join(dir_app, 'template_config', 'template_pgm.json')
        config = read_json(dir_pgm_remplate, 'config')
        gene_card = read_json(dir_pgm_remplate, 'gene_card')
        transcript = read_json(dir_pgm_remplate, 'transcript')
        dic_template = {'all_template': config}
        for c in config:
            print(c.keys())
        return jsonify(dic_template)


class AdminUser(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', required=True)
        self.parser.add_argument('passwd', required=True)
        self.parser.add_argument('mail', required=True)
        self.parser.add_argument('role',help='权限')

    def get(self):
        users = User.query.all()
        all_user = []
        for user in users:
            all_user.append(user.to_dict())
        dic_user = {'users': all_user}
        return jsonify(dic_user)

    def post(self):
        args = self.parser.parse_args()
        name = args.get('name')
        passwd = args.get('passwd')
        mail = args.get('mail')
        roles = args.get('role')
        if User.query.filter_by(username=name).first() is not None:
            msg = '用户已存在!!'
        else:
            user = User(username=name)
            user.mail = mail
            user.set_password(passwd)
            for role in roles:
                rol = Role.query.filter(Role.name==role).first()
                user.roles.append(rol)
            db.session.add(user)
            db.session.commit()
            msg = '注册成功'
        return {'msg': msg}


class AdminRole(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument()

    def get(self):
        roles = Role.query.all()
        list_role = []
        for role in roles:
            list_role.append(role.to_dict())
        return jsonify({'roles': list_role})
