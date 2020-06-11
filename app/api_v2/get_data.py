import os, shutil
import json
import datetime

from flask import (jsonify, current_app)
from flask_login import current_user, login_required
from flask_restful import (reqparse, Resource, fields, request)
from sqlalchemy import and_

from app.models import db
from app.models.user import User
from app.models.run_info import RunInfo, SeqInfo
from app.models.sample_v import (SampleInfoV, ApplyInfo, TreatInfoV, PathologyInfo, Operation, PatientInfoV,
                                 FamilyInfoV)
from app.models.report import Report

from app.libs.get_data import read_json
from app.libs.ext import str2time, set_float, time_set, set_time_now, calculate_time
from app.libs.report import save_reesult, get_qc_raw, dict2df
from app.libs.upload import find_apply


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
        self.parser.add_argument('page_per', type=int, help='每页数量')
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
        per_page = args.get('page_per')
        # print(per_page)
        all_run = RunInfo.query.all()
        run_info['total'] = len(all_run)
        runs = RunInfo.query.order_by(RunInfo.start_T.desc()). \
            paginate(page=page, per_page=per_page, error_out=False)
        list_run = []
        for run in runs.items:
            list_run.append(run.to_dict())
        run_info['run'] = list_run
        return jsonify(run_info)

    def post(self):  # 生成报告
        args = self.parser.parse_args()
        id = args.get('id')
        token = request.headers.get('token')
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401
        name = user.username
        run = RunInfo.query.filter(RunInfo.id == id).first()
        msgs = []
        for seq in run.seq_info:
            if seq.status == '分析完成':
                apply = ApplyInfo.query.filter(ApplyInfo.req_mg == seq.sample_mg).first()
                for sam in apply.sample_infos:
                    if seq.sample_name in sam.sample_id:
                        sam.seq.append(seq)
                        msg = save_reesult(seq, name, sam)

                        msgs.append(msg)
            elif seq.status == '结果已保存':
                msgs.append('样本{}结果已经保存'.format(seq.sample_name))
            else:
                msgs.append('样本{}未分析完成'.format(seq.sample_name))

        return {'msg': ','.join(msgs)}

    def delete(self):
        args = self.parser.parse_args()
        id = args.get('id')
        run = RunInfo.query.filter(RunInfo.id == id).first()
        run_id = run.name

        for seq in run.seq_info:
            sam = seq.sample_info_v
            if sam:
                report = sam.report
                sam.seq.remove(seq)
            run.seq_info.remove(seq)
            db.session.delete(seq)

        db.session.delete(run)
        db.session.commit()
        return {'msg': '{}.删除完成'.format(run_id)}

    def put(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        data = request.get_data()
        sams = (json.loads(data)['sams'])
        for sam in sams:
            seq_id = sam.get('id')
            print(sam)
            SeqInfo.query.filter(SeqInfo.id == seq_id).update(sam)
        db.session.commit()
        return {'msg': '保存成功'}


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
        run_info['seq_title'] = [
            {'type': 'selection', 'width': '50', 'align': 'center'},
            {'title': '操作', 'slot': 'action', 'width': '200'},
            {'title': '状态', 'key': 'status', 'width': '150'},
            {'title': '迈景编号', 'key': 'sample_name', 'width': '150'},
            {'title': '申请单号', 'key': 'sample_mg', 'width': '150'},
            {'title': '检测内容', 'key': 'item', 'width': '150'},
            {'title': '性别', 'key': 'gender', 'width': '150'},
            {'title': '样本类型', 'key': 'sam_type', 'width': '150'},
            {'title': '肿瘤细胞占比', 'key': 'cell_percent', 'width': '150'},
            {'title': 'Barcode编号', 'key': 'barcode', 'width': '150'},
            {'title': '肿瘤类型(报告用)', 'key': 'cancer', 'width': '150'},
            {'title': '报告模板', 'key': 'report_item', 'width': '150'},
            {'title': '备注', 'key': 'note', 'width': '150'}
        ]
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
        dir_res = current_app.config['RES_REPORT']
        dir_report = os.path.join(dir_res, 'report')
        if not os.path.exists(dir_report):
            os.mkdir(dir_report)
        err = []
        msgs = []
        name = user.username
        for sam in sams:
            seq_id = sam.get('id')
            seq = SeqInfo.query.filter(SeqInfo.id == seq_id).first()
            if seq.status == '分析完成':
                applys = ApplyInfo.query.filter(ApplyInfo.req_mg == seq.sample_mg).all()
                if applys:
                    for apply in applys:
                        print(f'申请单信息id:{apply.id}')
                        for sam in apply.sample_infos:
                            if seq.cancer:
                                if seq.sample_name in sam.sample_id:
                                    sam.seq.append(seq)
                                    print(seq.cell_percent)
                                    pathology = PathologyInfo(cell_content=seq.cell_percent)
                                    db.session.add(pathology)
                                    sam.pathology_info = pathology
                                    msg = save_reesult(seq, name, sam)
                                    msgs.append(msg)

                                    dic_out = (get_qc_raw(seq))
                                    qc = dic_out.get('qc')

                                    dic_qc = {}
                                    for row in qc:
                                        if 'D' in row['Sample']:
                                            dic_qc['on_target'] = row['On_Target']
                                            dic_qc['coverage'] = row['Coverage']
                                            dic_qc['dna_reads'] = row['Clean_reads']
                                            dic_qc['depth'] = row['Depth(X)']
                                            dic_qc['uniformity'] = row['Uniformity']
                                        if 'R' in row['Sample']:
                                            dic_qc['rna_reads'] = row['RNA_mapped_reads']
                                    pat = apply.patient_info_v.to_dict()
                                    dic_detail = {'迈景编号': apply.mg_id, '申请单号': apply.req_mg, '检测内容': seq.item,
                                                  '申请单检测项目': seq.report_item,
                                                  '治疗史，家族史': f"{pat['treat_info']},{pat['family_info']}",
                                                  '癌症类型': apply.cancer_d, '样本类型': seq.sam_type,
                                                  '肿瘤细胞纯度': seq.cell_percent,
                                                  'DNA mapped reads数': dic_qc.get('dna_reads'),
                                                  'on target': dic_qc.get('on_target'), '测序深度': dic_qc.get('depth'),
                                                  '均一性': dic_qc.get('uniformity'),
                                                  '覆盖完整性': dic_qc.get('coverage'),
                                                  'RNA mapped reads数': dic_qc.get('rna_reads') if dic_qc.get(
                                                      'rna_reads') else '',
                                                  '检测的突变': '', '靶向药物': '', '销售': apply.sales,
                                                  '报告状态': '', '报告制作人': '', '收样日期': time_set(sam.receive_t),
                                                  '报告日期': set_time_now(),
                                                  '质控时间': f"{calculate_time(time_set(sam.receive_t), set_time_now())}天"}
                                    df = dict2df([dic_detail])
                                    mg_id = apply.mg_id
                                    req_mg = apply.req_mg
                                    dir_report_mg = os.path.join(dir_report, mg_id)
                                    if not os.path.exists(dir_report_mg):
                                        os.mkdir(dir_report_mg)
                                    excel_f = os.path.join(dir_report_mg, f"{mg_id}_{req_mg}.xlsx")
                                    df.to_excel(excel_f, sheet_name='详情', index=False)
                                    dir_apply = current_app.config['UPLOADED_FILEREQ_DEST']
                                    apply_f = find_apply(time_set(sam.receive_t), apply.req_mg, dir_apply)
                                    for file in apply_f:
                                        if file:
                                            shutil.copy2(file, os.path.join(dir_report_mg, os.path.split(file)[-1]))

                                else:
                                    msgs.append(f'样本{seq.sample_name} 迈景编号与样本信息不符')
                            else:
                                msgs.append(f'样本{seq.sample_name} 肿瘤类型（报告用未填写）')

                else:
                    msgs.append('样本{} 的样本信息未录入，请到样本信息登记处录入'.format(seq.sample_name))
            elif seq.status == '结果已保存':
                msgs.append('样本{}结果已经保存'.format(seq.sample_name))
            else:
                msgs.append('样本{}未分析完成'.format(seq.sample_name))
            print(seq_id)
        #     sample = sam.get('sample_name')
        #     for row in samples:
        #         if sample in row.values():  # 使用迈景编号 todo：新的方案？
        #             pat = PatientInfoV.query.filter(PatientInfoV.name == row.get('患者姓名')).first()
        #             if pat:
        #                 pass
        #             else:
        #                 pat = PatientInfoV(name=row.get('患者姓名'), age=row.get('病人年龄'), gender=row.get('病人性别'),
        #                                    nation=row.get('民族'), origo=row.get('籍贯'), contact=row.get('病人联系方式'),
        #                                    ID_number=row.get('病人身份证号码'), other_diseases=row.get('有无其他基因疾病'),
        #                                    smoke=row.get('有无吸烟史'))
        #                 db.session.add(pat)
        #                 # db.session.commit()
        #             samp = SampleInfoV.query.filter(and_(SampleInfoV.req_mg == row.get('申请单号'),
        #                                                  SampleInfoV.mg_id == row.get('迈景编号'))).first()
        #             if samp:
        #                 pass
        #             else:
        #                 samp = SampleInfoV(mg_id=row.get('迈景编号'), req_mg=row.get('申请单号'),
        #                                    seq_item=row.get('检测项目'), seq_type=row.get('项目类型'),
        #                                    doctor=row.get('医生姓名'), hosptial=row.get('医院名称'),
        #                                    room=row.get('科室'), diagnosis=row.get('临床诊断'),
        #                                    diagnosis_date=str2time(row.get('诊断日期')),
        #                                    pathological=row.get('病理诊断'), pnumber=row.get('病理号'),
        #                                    pathological_date=str2time(row.get('诊断日期.1')),
        #                                    recive_date=str2time(row.get('病理样本收到日期')), Sour=row.get('样本来源'),
        #                                    mode_of_trans=row.get('运输方式'), Tytime=str2time(row.get('采样时间')),
        #                                    send_sample_date=str2time(row.get('送检日期')), mth=row.get('采样方式'),
        #                                    reciver=row.get('收样人'), recive_room_date=str2time(row.get('收样日期')),
        #                                    sample_status=row.get('状态是否正常'), sample_type=row.get('样本类型（报告用）'),
        #                                    sample_size=row.get('样本大小'), sample_count=row.get('数量'),
        #                                    seq_date=str2time(row.get('检测日期')), note=row.get('备注'),
        #                                    recorder=row.get('录入'), reviewer=row.get('审核'))
        #                 tre_h = TreatInfoV(name='化疗', is_treat=row.get('是否接受化疗'),
        #                                    star_time=str2time(row.get('开始时间')),
        #                                    end_time=str2time(row.get('结束时间')), effect=row.get('治疗效果'))
        #                 tre_f = TreatInfoV(name='放疗', is_treat=row.get('是否放疗'),
        #                                    star_time=str2time(row.get('起始时间')),
        #                                    end_time=str2time(row.get('结束时间.2')), effect=row.get('治疗效果.2'))
        #                 tre_b = TreatInfoV(name='靶向治疗', is_treat=row.get('是否靶向药治疗'),
        #                                    star_time=str2time(row.get('开始时间.1')),
        #                                    end_time=str2time(row.get('结束时间.1')), effect=row.get('治疗效果.1'))
        #                 fam = FamilyInfoV(diseases=row.get('有无家族遗传疾病'))
        #                 patho = PathologyInfo(pathology=row.get('病理审核'), cell_count=row.get('标本内细胞总量'),
        #                                       cell_content=set_float(row.get('肿瘤细胞含量')),
        #                                       spical_note=row.get('特殊说明'))
        #                 db.session.add(samp)
        #                 db.session.add(patho)
        #                 samp.treat_info.append(tre_b)
        #                 samp.treat_info.append(tre_f)
        #                 samp.treat_info.append(tre_h)
        #                 samp.pathology_info = patho
        #                 db.session.add(tre_b)
        #                 db.session.add(tre_f)
        #                 db.session.add(tre_h)
        #                 db.session.add(fam)
        #                 pat.sample_info.append(samp)
        #                 pat.family_info.append(fam)
        #             rep_name = '{}_{}'.format(sam.get('sample_mg'), sam.get('item').split('/')[0])
        #             rep = Report.query.filter(Report.rep_code == rep_name).first()
        #             if rep:
        #                 err.append('报告{}已经被{}承包了,麻烦换一份'.format(sample, rep.report_user))
        #             else:
        #                 seq = SeqInfo.query.filter(SeqInfo.id == sam.get('id')).update({'status': '{}承包中'.format(name)})
        #                 msgs.append(sample)
        #                 rep = Report(rep_code=rep_name, stage='突变审核', report_user=name)  # todo 简化
        #                 db.session.add(rep)
        #                 rep.samples.append(samp)
        #
        #                 operation = Operation(user=name, name='突变审核', time=datetime.datetime.now())
        #                 samp.operation_log.append(operation)
        #                 db.session.add(operation)
        #             db.session.commit()
        #
        # msg = '{}承包完成'.format('、'.join(msgs))
        # errs = ';'.join(err)

        return {'msg': ','.join(msgs)}

    def put(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        data = request.get_data()
        sams = (json.loads(data)['sams'])
        for sam in sams:
            seq_id = sam.get('id')
            seq = SeqInfo.query.filter(SeqInfo.id == seq_id).first()
            seq.status = '分析完成'
        db.session.commit()
        return {'msg': '开始重新分析'}


class SeqQc(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', help='报告id')

    def get(self):
        argv = self.parser.parse_args()
        rep_id = argv.get('id')
        sam = Report.query.filter(Report.id == rep_id).first().sample_info_v
        seq = SeqInfo.query.filter(SeqInfo.sample_name == sam.sample_id).first()
        dic_out = (get_qc_raw(seq))
        qc = dic_out.get('qc')
        if qc:
            qc_title = [{'title': k, 'key': k, 'width': '100'} for k in qc[0].keys()]
            dic_out['qc_title'] = qc_title
        raw = dic_out.get('raw')
        if raw:
            dic_out['raw_title'] = [{'title': k, 'key': k, 'width': '100'} for k in raw[0].keys()]
        w_list = dic_out.get('w_list')
        if w_list:
            dic_out['w_list_title'] = [{'title': k, 'key': k, 'width': '100'} for k in w_list[0].keys()]
        # print(dic_out['w_list_title'])
        return jsonify(dic_out)
