import json, os

from flask import (jsonify, current_app)
from flask_restful import (reqparse, Resource, fields, request)

from app.models import db
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
        sams = read_json(dir_sample)['样本信息登记表'][0]['样本信息登记表']
        pagenation_sam = [sam for sam in splitN(sams, page_per)]
        dict_sam = {}
        for k in (pagenation_sam[page][0].keys()):
            print('''{
          title: '%s',
          key: '%s',
          width: '120'
        },''' % (k, k))
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
