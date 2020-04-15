from flask import (jsonify, current_app)
from flask_restful import (reqparse, Resource, fields, request)
from sqlalchemy import and_

from app.models.user import User
from app.models.record_config import PatientRecord, SampleRecord, \
    SeqItemRecord, FamilyRecord, TreatRecord, SendMethod


class SampleInfoRecord(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('per_page', type=int, help='每页数量')

    def get(self):
        args = self.parser.parse_args()
        page = args.get('page')
        per_page = args.get('per_page')

        token = request.headers.get('token')
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        samples = SampleRecord.query.order_by(SampleRecord.id.desc()). \
            paginate(page=page, per_page=per_page, error_out=False)
        list_sam = []
        total = len(SampleRecord.query.all())
        for sam in samples.items:
            dic_sam = sam.to_dict()
            dic_sam['edit_able'] = False
            list_sam.append(dic_sam)

        # print(list_sam[0])
        return jsonify({'sample': list_sam, 'total': total, 'test': {'name': 'hah'}})
