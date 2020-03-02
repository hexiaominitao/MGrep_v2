import os
import json

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
        sams = read_json(dir_sample, 'sample_info')
        all_sample['all_sample'] = sams
        print(type(sams))
        return jsonify(all_sample)


class GetRunInfo(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('per_page', type=int, help='每页数量')
        self.parser.add_argument('id', help='样本id')

    def get(self):
        run_info = {}
        args = self.parser.parse_args()
        page = args.get('page')
        per_page = args.get('per_page')
        all_run = RunInfo.query.all()
        run_info['total'] = len(all_run)
        runs = RunInfo.query.order_by(RunInfo.start_T.desc()). \
            paginate(page=page, per_page=per_page, error_out=False)
        list_run = []
        for run in runs.items:
            list_run.append(run.to_dict())
        run_info['run'] = list_run
        return jsonify(run_info)

    def delete(self):
        args = self.parser.parse_args()
        id = args.get('id')
        run = RunInfo.query.filter(RunInfo.id == id).first()
        run_id = run.name
        db.session.delete(run)
        db.session.commit()
        return {'msg': '{}.删除完成'.format(run_id)}


class GetSeqInfo(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, help='run name')
        self.parser.add_argument('sams', help='报告编号', action='append')

    def get(self):
        args = self.parser.parse_args()
        run_info = {}
        run_name = args.get('name')
        run = RunInfo.query.filter(RunInfo.name == run_name).first()
        run_info['run'] = run.to_dict()
        list_seq = []
        for seq in run.seq_info:
            list_seq.append(seq.to_dict())
        run_info['seq'] = list_seq
        return jsonify(run_info)

    def delete(self):
        data = request.get_data()
        sams = json.loads(data)['sams']
        err = ''
        return None
