import os

from flask import (jsonify, current_app)
from flask_login import current_user
from flask_restful import (reqparse, Resource, fields, request)

from app.models import db
from app.models.run_info import RunInfo, SeqInfo
from app.libs.get_data import read_json


class GetAllSample(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('val', required=True, type=str,
                                 help='迈景编号/申请单号/患者姓名')

    def get(self):
        all_sample = {}
        dir_app = current_app.config['PRE_REPORT']
        dir_sample = os.path.join(dir_app, 'sample', 'sample.json')
        sams = read_json(dir_sample,'sample_info')
        all_sample['all_sample'] = sams
        return jsonify(all_sample)
