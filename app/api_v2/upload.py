import os
import json

from flask_restful import (reqparse, Resource, request)
from flask import (current_app)
from werkzeug.datastructures import FileStorage
from sqlalchemy import and_

from app.models import db
from app.models.run_info import RunInfo, SeqInfo
from app.models.annotate import ClinicInterpretation, OKR
from app.models.report import Report
from app.models.mutation import Mutation, Mutations, Chemotherapy
from app.models.record_config import SalesInfo, HospitalInfo, SampleType, \
    SeqItems, CancerTypes

from app.libs.ext import file_sam, file_okr
from app.libs.upload import save_json_file, excel_to_dict, get_excel_title, get_seq_info, excel2dict, df2dict, time_set, \
    tsv_to_list, file_2_dict, m_excel2list
from app.libs.report import del_db
from app.libs.ir import save_mutation
from app.libs.get_data import read_json


class SampleInfoUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True, help='样本信息登记表')
        super(SampleInfoUpload, self).__init__()

    def post(self):
        filename = file_sam.save(request.files['file'])
        file = file_sam.path(filename)
        dict_sample = excel_to_dict(file)
        dir_app = current_app.config['PRE_REPORT']
        try:
            os.mkdir(os.path.join(dir_app, 'sample'))
        except IOError:
            pass

        dir_sample = os.path.join(dir_app, 'sample', 'sample.json')
        save_json_file(dir_sample, dict_sample, 'sample_info')
        os.remove(file)
        return {'msg': '样本信息保存成功！！'}


class RunInfoUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True,
                                 help='file')
        super(RunInfoUpload, self).__init__()

    def post(self):
        filename = file_sam.save(request.files['file'])
        file = file_sam.path(filename)
        try:
            title = get_excel_title(file)
            print(title)
            if title in ['S5', 'PGM', 's5', 'pgm']:
                df_seq = get_seq_info(file)
                for name, df in df_seq:
                    if name:
                        print(df)
                        dict_run = df2dict(df)
                        for dict_val in dict_run.values():
                            run = RunInfo.query.filter(RunInfo.name == name).first()
                            if run:
                                pass
                            else:
                                run = RunInfo(name=name, platform=title,
                                              start_T=time_set(dict_val.get('上机时间')),
                                              end_T=time_set(dict_val.get('结束时间')))

                                db.session.add(run)
                                db.session.commit()
                            seq = SeqInfo.query.filter(SeqInfo.sample_name == dict_val.get('迈景编号')).first()
                            if seq:
                                pass
                            else:
                                seq = SeqInfo(sample_name=dict_val.get('迈景编号'), sample_mg=dict_val.get('申请单号'),
                                              item=dict_val.get('检测内容'), barcode=dict_val.get('Barcode编号'),
                                              note=dict_val.get('备注'), cancer=dict_val.get('肿瘤类型(报告用)'),
                                              report_item=dict_val.get('报告模板'))
                                db.session.add(seq)
                                run.seq_info.append(seq)
                            # db.session.commit()
            else:
                dict_run = excel2dict(file)
                for dict_val in dict_run.values():
                    run = RunInfo.query.filter(RunInfo.name == dict_val.get('Run name')).first()
                    if run:
                        pass
                    else:
                        run = RunInfo(name=dict_val.get('Run name'), platform=title,
                                      start_T=time_set(dict_val.get('上机时间')),
                                      end_T=time_set(dict_val.get('下机时间')))
                        db.session.add(run)
                        db.session.commit()
                    seq = SeqInfo.query.filter(SeqInfo.sample_name == dict_val.get('样本编号')).first()
                    if seq:
                        pass
                    else:
                        seq = SeqInfo(sample_name=dict_val.get('样本编号'),
                                      item=dict_val.get('检测项目'), barcode=dict_val.get('index(P7+P5)'),
                                      note=dict_val.get('备注'))
                        db.session.add(seq)
                        run.seq_info.append(seq)
                    db.session.commit()
            msg = '文件上传成功!'
        except IOError:
            msg = '文件有问题,请检查后再上传!!!!!'
        os.remove(file)
        return {'msg': msg}, 200


class MutationUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        # self.parser.add_argument('file', type=FileStorage, required=True, help='样本信息登记表')
        # self.parser.add_argument('name')
        super(MutationUpload, self).__init__()

    def post(self):
        filename = file_okr.save(request.files['file'])
        file = file_okr.path(filename)
        id = request.form['name']
        report = Report.query.filter(Report.id == id).first()
        mu = report.mutation
        if mu:
            del_db(db, mu.snv)
            del_db(db, mu.cnv)
            del_db(db, mu.fusion)
            db.session.commit()
        mutation = Mutations()
        dic = file_2_dict(file)
        print(dic)
        if dic:
            for row in dic:
                snv = Mutation(gene=row.get('基因'),
                               mu_type=row.get('检测的突变类型'),
                               mu_name=row.get('变异全称'),
                               mu_af=row.get('丰度'),
                               mu_name_usual=row.get('临床突变常用名称'),
                               reads=row.get('支持序列数'),
                               maf=row.get('maf'),
                               exon=row.get('外显子'),
                               fu_type=row.get('检测基因型'), status='等待审核',
                               locus=row.get('位置'), type=row.get('type'))
                db.session.add(snv)
                mutation.mutation.append(snv)
        db.session.add(mutation)
        report.mutation = mutation
        db.session.commit()
        print(report.mutation.id)

        os.remove(file)
        return {'msg': '突变信息上传成功！！！'}


class OKRUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        # self.parser.add_argument('file', type=FileStorage, required=True, help='样本信息登记表')
        # self.parser.add_argument('name')
        super(OKRUpload, self).__init__()

    def post(self):
        filename = file_okr.save(request.files['file'])
        file = file_okr.path(filename)
        list_okr = tsv_to_list(file)
        okr_version = filename.split('_')[0]
        clinic = ClinicInterpretation.query.filter(ClinicInterpretation.okr_version == okr_version).first()
        if clinic:
            pass
        else:
            clinic = ClinicInterpretation(okr_version=okr_version)
            for okr_dic in list_okr:
                okr = OKR.query.filter(
                    and_(OKR.disease == okr_dic.get('disease'), OKR.gene_name == okr_dic.get('gene_name'),
                         OKR.protein_alteration == okr_dic.get('protein_alteration'), OKR.drug == okr_dic.get('drug'),
                         OKR.drug_effect == okr_dic.get('drug_effect'), OKR.evidence == okr_dic.get('evidence'),
                         OKR.evidence_level == okr_dic.get('evidence_level'))).first()
                if okr:
                    pass
                else:
                    okr = OKR(disease=okr_dic.get('disease'), gene_name=okr_dic.get('gene_name'),
                              protein_alteration=okr_dic.get('protein_alteration'), drug=okr_dic.get('drug'),
                              drug_effect=okr_dic.get('drug_effect'), evidence=okr_dic.get('evidence'),
                              evidence_level=okr_dic.get('evidence_level'))
                    db.session.add(okr)
                clinic.okr.append(okr)
            db.session.commit()

        os.remove(file)
        return {'msg': 'okr更新成功!!!'}


class IrUpload(Resource):
    def __init__(self):
        pass

    def post(self):
        path_wk = current_app.config['COUNT_DEST']
        dir_res = current_app.config['RES_REPORT']

        for file in request.files.getlist('file'):
            file_okr.save(file)

        rep_id = request.form['name']
        report = Report.query.filter(Report.id == rep_id).first()
        sample = report.samples[0]
        rep_mg = sample.req_mg
        mg_id = sample.mg_id

        dir_rep = os.path.join(dir_res, rep_mg)

        save_mutation(path_wk, dir_rep, mg_id, rep_mg)
        return {'msg': '保存完成'}


# class SampleRecordUpload(Resource):
#     def post(self):
#         filename = file_okr.save(request.files['file'])
#         file = file_okr.path(filename)
#         list_sample = excel_to_dict(file)
#         for row in list_sample:
#             mg_id = row['迈景编号']
#             req_mg = row['申请单号']
#             code = req_mg[4:8]
#             sale = SalesInfo.query.filter(SalesInfo.code == code).first()
#             sample = SampleRecord.query.filter(and_(
#                 SampleRecord.mg_id == mg_id, SampleRecord.req_mg == req_mg)).first()
#             if sample:
#                 pass
#             else:
#                 sample = SampleRecord(mg_id=mg_id, req_mg=req_mg, sales=sale.name)
#                 db.session.add(sample)
#         db.session.commit()
#         os.remove(file)
#         return {'msg': '上传成功!!!'}


class GeneralUpload(Resource):
    def post(self):
        filename = file_okr.save(request.files['file'])
        file = file_okr.path(filename)

        item = request.form['name']
        if item == 'sales':
            list_sample = m_excel2list(file)
            for name, dict_r in list_sample.items():
                print(name)
                if name == 'sales':
                    for row in dict_r:
                        code = row['销售代码']
                        sale = SalesInfo.query.filter(SalesInfo.code == code).first()
                        if sale:
                            pass
                        else:
                            sale = SalesInfo(code=code, name=row.get('销售姓名'),
                                             status=row.get('状态'), mail=row.get('电子邮箱'),
                                             region=row.get('所属区域'), phone=row.get('电话'),
                                             address=row.get('地址'))
                            db.session.add(sale)
                if name == 'hospital':
                    for row in dict_r:
                        h_name = row['医院']
                        hospital = HospitalInfo.query.filter(HospitalInfo.name == h_name).first()
                        if hospital:
                            pass
                        else:
                            hospital = HospitalInfo(name=h_name)
                            db.session.add(hospital)
                if name == 'type':
                    for row in dict_r:
                        name = row['样本类型']
                        ty = SampleType.query.filter(SampleType.name == name).first()
                        if ty:
                            pass
                        else:
                            ty = SampleType(name=name)
                            db.session.add(ty)
                if name == 'cancer':
                    for row in dict_r:
                        name = row['okr']
                        cn_name = row['癌症类型']
                        cancer = CancerTypes.query.filter(CancerTypes.cn_name == cn_name).first()
                        if cancer:
                            pass
                        else:
                            cancer = CancerTypes(name=name, cn_name=cn_name)
                            db.session.add(cancer)
                if name == 'items':
                    for row in dict_r:
                        name = row['检测项目']
                        items = SeqItems.query.filter(SeqItems.name == name).first()
                        if items:
                            pass
                        else:
                            items = SeqItems(name=name)
                            db.session.add(items)
            # 利用item 添加新的项目

        db.session.commit()
        os.remove(file)
