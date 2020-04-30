import os
import json
import datetime

from flask import (jsonify, current_app)
from flask_login import current_user, login_required
from flask_restful import (reqparse, Resource, fields, request)
from sqlalchemy import and_

from app.models import db
from app.models.user import User
from app.models.run_info import RunInfo, SeqInfo
from app.models.sample_v import PatientInfoV, FamilyInfoV
from app.models.sample_v import (SampleInfoV, ApplyInfo, TreatInfoV, PathologyInfo, Operation)
from app.models.report import Report

from app.libs.get_data import read_json
from app.libs.ext import str2time, set_float


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
    # decorators = [login_required] # 添加装饰器

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('per_page', type=int, help='每页数量')
        self.parser.add_argument('id', help='样本id')
        # self.parser.add_argument('token', type=str, required=True, help='用户认证')

    def get(self):
        run_info = {}
        args = self.parser.parse_args()
        token = request.headers.get('token')
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401
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

    def post(self):
        args = self.parser.parse_args()
        id = args.get('id')
        run = RunInfo.query.filter(RunInfo.id == id).first()
        for seq in run.seq_info:
            apply = ApplyInfo.query.filter(ApplyInfo.req_mg==seq.sample_mg).first()
            for sam in apply.sample_infos:
                if seq.sample_name in sam.sample_id:
                    sam.seq.append(seq)
        return {'msg': '成功'}

    def delete(self):
        args = self.parser.parse_args()
        id = args.get('id')
        run = RunInfo.query.filter(RunInfo.id == id).first()
        run_id = run.name
        db.session.delete(run)
        for seq in run.seq_info:
            sam = seq.sample_info_v
            sam.remove(sam)
            db.session.delete(seq)

        # db.session.commit()
        return {'msg': '{}.删除完成'.format(run_id)}


class GetSeqInfo(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('name', type=str, help='run name')
        self.parser.add_argument('sams', help='报告编号', action='append')

    def get(self):

        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

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

    #  样本信未保存至数据库 todo：将所有样本信息保存到数据库

    def post(self):

        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        data = request.get_data()
        sams = (json.loads(data)['sams'])
        dir_app = current_app.config['PRE_REPORT']
        dir_sample = os.path.join(dir_app, 'sample', 'sample.json')
        samples = read_json(dir_sample, 'sample_info')[0]['sams']
        err = []
        msgs = []
        name = user.username
        for sam in sams:
            sample = sam.get('sample_name')
            for row in samples:
                if sample in row.values():  # 使用迈景编号 todo：新的方案？
                    pat = PatientInfoV.query.filter(PatientInfoV.name == row.get('患者姓名')).first()
                    if pat:
                        pass
                    else:
                        pat = PatientInfoV(name=row.get('患者姓名'), age=row.get('病人年龄'), gender=row.get('病人性别'),
                                           nation=row.get('民族'), origo=row.get('籍贯'), contact=row.get('病人联系方式'),
                                           ID_number=row.get('病人身份证号码'), other_diseases=row.get('有无其他基因疾病'),
                                           smoke=row.get('有无吸烟史'))
                        db.session.add(pat)
                        # db.session.commit()
                    samp = SampleInfoV.query.filter(and_(SampleInfoV.req_mg == row.get('申请单号'),
                                                         SampleInfoV.mg_id == row.get('迈景编号'))).first()
                    if samp:
                        pass
                    else:
                        samp = SampleInfoV(mg_id=row.get('迈景编号'), req_mg=row.get('申请单号'),
                                           seq_item=row.get('检测项目'), seq_type=row.get('项目类型'),
                                           doctor=row.get('医生姓名'), hosptial=row.get('医院名称'),
                                           room=row.get('科室'), diagnosis=row.get('临床诊断'),
                                           diagnosis_date=str2time(row.get('诊断日期')),
                                           pathological=row.get('病理诊断'), pnumber=row.get('病理号'),
                                           pathological_date=str2time(row.get('诊断日期.1')),
                                           recive_date=str2time(row.get('病理样本收到日期')), Sour=row.get('样本来源'),
                                           mode_of_trans=row.get('运输方式'), Tytime=str2time(row.get('采样时间')),
                                           send_sample_date=str2time(row.get('送检日期')), mth=row.get('采样方式'),
                                           reciver=row.get('收样人'), recive_room_date=str2time(row.get('收样日期')),
                                           sample_status=row.get('状态是否正常'), sample_type=row.get('样本类型（报告用）'),
                                           sample_size=row.get('样本大小'), sample_count=row.get('数量'),
                                           seq_date=str2time(row.get('检测日期')), note=row.get('备注'),
                                           recorder=row.get('录入'), reviewer=row.get('审核'))
                        tre_h = TreatInfoV(name='化疗', is_treat=row.get('是否接受化疗'),
                                           star_time=str2time(row.get('开始时间')),
                                           end_time=str2time(row.get('结束时间')), effect=row.get('治疗效果'))
                        tre_f = TreatInfoV(name='放疗', is_treat=row.get('是否放疗'),
                                           star_time=str2time(row.get('起始时间')),
                                           end_time=str2time(row.get('结束时间.2')), effect=row.get('治疗效果.2'))
                        tre_b = TreatInfoV(name='靶向治疗', is_treat=row.get('是否靶向药治疗'),
                                           star_time=str2time(row.get('开始时间.1')),
                                           end_time=str2time(row.get('结束时间.1')), effect=row.get('治疗效果.1'))
                        fam = FamilyInfoV(diseases=row.get('有无家族遗传疾病'))
                        patho = PathologyInfo(pathology=row.get('病理审核'), cell_count=row.get('标本内细胞总量'),
                                              cell_content=set_float(row.get('肿瘤细胞含量')),
                                              spical_note=row.get('特殊说明'))
                        db.session.add(samp)
                        db.session.add(patho)
                        samp.treat_info.append(tre_b)
                        samp.treat_info.append(tre_f)
                        samp.treat_info.append(tre_h)
                        samp.pathology_info = patho
                        db.session.add(tre_b)
                        db.session.add(tre_f)
                        db.session.add(tre_h)
                        db.session.add(fam)
                        pat.sample_info.append(samp)
                        pat.family_info.append(fam)
                    rep_name = '{}_{}'.format(sam.get('sample_mg'), sam.get('item').split('/')[0])
                    rep = Report.query.filter(Report.rep_code == rep_name).first()
                    if rep:
                        err.append('报告{}已经被{}承包了,麻烦换一份'.format(sample, rep.report_user))
                    else:
                        seq = SeqInfo.query.filter(SeqInfo.id == sam.get('id')).update({'status': '{}承包中'.format(name)})
                        msgs.append(sample)
                        rep = Report(rep_code=rep_name, stage='突变审核', report_user=name)  # todo 简化
                        db.session.add(rep)
                        rep.samples.append(samp)

                        operation = Operation(user=name, name='突变审核', time=datetime.datetime.now())
                        samp.operation_log.append(operation)
                        db.session.add(operation)
                    db.session.commit()

        msg = '{}承包完成'.format('、'.join(msgs))
        errs = ';'.join(err)

        return {'msg': msg, 'errs': errs}
