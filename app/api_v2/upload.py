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
from app.models.mutation import Mutation, SNV_INDEL, Fusion, CNV, Chemotherapy
from app.libs.ext import file_sam, file_okr
from app.libs.upload import save_json_file, excel_to_dict, get_excel_title, get_seq_info, excel2dict, df2dict, time_set, \
    tsv_to_list, file_2_dict
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
                                              note=dict_val.get('备注'))
                                db.session.add(seq)
                                run.seq_info.append(seq)
                            db.session.commit()
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
            for snv in mu.snv:
                db.session.delete(snv)
            for fusion in mu.fusion:
                db.session.delete(fusion)
            for cnv in mu.cnv:
                db.session.delete(cnv)
            db.session.commit()
        mutation = Mutation()
        dic = file_2_dict(file)
        print(dic)
        if dic:
            for row in dic:
                if row['type'] == 'snv_indel':
                    snv = SNV_INDEL(gene=row.get('基因'),
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
                    mutation.snv.append(snv)
                if row['type'] == 'fusion':
                    fusion = Fusion(gene=row.get('基因'),
                                    mu_type=row.get('检测的突变类型'),
                                    mu_name=row.get('变异全称'),
                                    mu_af=row.get('丰度'), status='等待审核',
                                    mu_name_usual=row.get('临床突变常用名称'), type=row.get('type'))
                    db.session.add(fusion)
                    mutation.fusion.append(fusion)
                if row['type'] == "cnv":
                    cnv = CNV(gene=row.get('基因'),
                              mu_type=row.get('检测的突变类型'),
                              mu_name=row.get('变异全称'),
                              mu_af=row.get('丰度'), status='等待审核',
                              mu_name_usual=row.get('临床突变常用名称'), type=row.get('type'))
                    db.session.add(cnv)
                    mutation.cnv.append(cnv)
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
