import os
import json
import shutil

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
    SeqItems, CancerTypes, Barcode, FlowItem, CancerTypes
from app.models.sample_v import PatientInfoV, FamilyInfoV, TreatInfoV, ApplyInfo, \
    SendMethodV, SampleInfoV, ReportItem, PathologyInfo, Operation

from app.libs.ext import file_sam, file_okr, file_pdf
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


class SampleInfoVUpload(Resource):
    def post(self):
        filename = file_sam.save(request.files['file'])
        file = file_sam.path(filename)
        list_sam = excel_to_dict(file)
        for row in list_sam:
            apply = ApplyInfo.query.filter(ApplyInfo.req_mg == row.get('申请单号')).first()
            if apply:
                pass
            else:
                pat = PatientInfoV(name=row.get('患者姓名'), age=row.get('病人年龄'), gender=row.get('病人性别'),
                                   nation=row.get('民族')
                                   , origo=row.get('籍贯'), contact=row.get('病人联系方式'), ID_number=row.get('病人身份证号码'),
                                   address=row.get('病人地址'))
                db.session.add(pat)
                apply = ApplyInfo(mg_id=row.get('迈景编号'), req_mg=row.get('申请单号'), sales=row.get('销售代表'),
                                  outpatient_id=row.get('门诊/住院号'), doctor=row.get('医生姓名'), hosptial=row.get('医院名称'),
                                  room=row.get('科室'), cancer_d=row.get('病理诊断'), seq_type=row.get('项目类型'),
                                  pathological=row.get('病理诊断'), note=row.get('备注'))
                db.session.add(apply)
                pat.applys.append(apply)
                sam = SampleInfoV(sample_id=row.get('迈景编号'), pnumber=row.get('病理号')
                                  , sample_type=row.get('样本类型（报告用）'), mth=row.get('采样方式')
                                  , sample_count=row.get('数量'))
                db.session.add(sam)
                apply.sample_infos.append(sam)

        db.session.commit()
        os.remove(file)
        return {'msg': '文件上传成功'}


class RunInfoUpload(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file', type=FileStorage, required=True,
                                 help='file')
        super(RunInfoUpload, self).__init__()

    def post(self):
        filename = file_sam.save(request.files['file'])
        file = file_sam.path(filename)
        erro = []
        barcodes = set()
        for bar in Barcode.query.all():
            barcodes.add(bar.name)
        flowitems = set()
        for items in FlowItem.query.all():
            flowitems.add(items.name)
        l_cancer = set()
        for can in CancerTypes.query.all():
            l_cancer.add(can.name)
        dir_app = current_app.config['PRE_REPORT']
        dir_pgm_remplate = os.path.join(dir_app, 'template_config', 'template_pgm.json')
        config = read_json(dir_pgm_remplate, 'config')
        l_item = set()
        for row in config:
            l_item.add(row.get('item'))


        try:
            title = get_excel_title(file)
            print(title)
            if title in ['S5', 'PGM', 's5', 'pgm']:
                df_seq = get_seq_info(file)
                for name, df in df_seq:
                    if name:
                        # print(df)
                        title_df = [v for v in df.columns]
                        if '肿瘤类型(报告用)' not in title_df and '报告模板' not in title_df:
                            erro.append('上机信息未包含“肿瘤类型(报告用)”或“报告模板”')
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
                                if erro:
                                    pass
                                else:
                                    db.session.commit()
                            barcode = dict_val.get('Barcode编号').split('/')
                            sam_type = dict_val.get('样本类型').split('/')
                            cancer = dict_val.get('肿瘤类型(报告用)')
                            rep_item = dict_val.get('报告模板')

                            if cancer and (cancer not in l_cancer):
                                erro.append(f'样本{dict_val.get("迈景编号")}癌症类型_{cancer}_不包含在数据库中，请修改后重试！！，所有类型：{"、".join(l_cancer)}。')

                            if rep_item and (rep_item not in l_item):
                                erro.append(f'样本{dict_val.get("迈景编号")}报告模板_{rep_item}_不包含在数据库中，请修改后重试！！，所有模板：{"、".join(l_item)}。')

                            for bar in barcode:
                                if bar in barcodes:
                                    continue
                                erro.append('样本{}Barcode编号存在问题，请检查后重试！！'.format(dict_val.get('迈景编号')))
                            for i in sam_type:
                                if i in flowitems:
                                    continue
                                erro.append('样本{}样本类型存在问题，请检查后重试！！'.format(dict_val.get('迈景编号')))

                            seq = SeqInfo.query.filter(SeqInfo.sample_name == dict_val.get('迈景编号')).first()

                            if seq:
                                print(f"样本id为{seq.id}")
                                erro.append('样本{}信息已存在'.format(dict_val.get('迈景编号')))
                                pass
                            else:
                                seq = SeqInfo(sample_name=dict_val.get('迈景编号'), sample_mg=dict_val.get('申请单号'),
                                              item=dict_val.get('检测内容'), barcode=dict_val.get('Barcode编号'),
                                              note=dict_val.get('备注'), cancer=dict_val.get('肿瘤类型(报告用)'),
                                              report_item=dict_val.get('报告模板'), sam_type=dict_val.get('样本类型'),
                                              cell_percent=dict_val.get('肿瘤细胞占比'), status='准备分析',
                                              gender=dict_val.get('性别'))
                                db.session.add(seq)
                                run.seq_info.append(seq)
                            if erro:
                                pass
                            else:
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

            msg = '上机信息上传成功!'
        except IOError:
            msg = '文件有问题,请检查后再上传!!!!!'
        os.remove(file)
        if erro:
            msg = ','.join(erro)
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
            del_db(db, clinic.okr)
            db.session.commit()
        else:
            clinic = ClinicInterpretation(okr_version=okr_version)
        for okr_dic in list_okr:
            okr = OKR(disease=okr_dic.get('disease'), gene_name=okr_dic.get('gene_name'),
                      protein_alteration=okr_dic.get('protein_alteration'), drug=okr_dic.get('drug'),
                      drug_effect=okr_dic.get('drug_effect'), evidence=okr_dic.get('evidence'),
                      evidence_level=okr_dic.get('evidence_level'), grade=okr_dic.get('grade'))
            db.session.add(okr)
            clinic.okr.append(okr)

        db.session.commit()

        os.remove(file)
        return {'msg': 'okr更新成功!!!'}


class IrUpload(Resource):
    def __init__(self):
        pass

    def post(self):
        dir_res = current_app.config['RES_REPORT']
        dir_report = os.path.join(dir_res, 'report')

        rep_id = request.form['name']
        report = Report.query.filter(Report.id == rep_id).first()
        sam = report.sample_info_v
        report.auto_okr = 'No'
        db.session.commit()
        mg_id = sam.sample_id
        filename = file_pdf.save(request.files['file'], name='{}.okr.tsv'.format(mg_id))
        file = file_pdf.path(filename)

        dir_report_mg = os.path.join(dir_report, mg_id)
        if not os.path.exists(dir_report_mg):
            os.mkdir(dir_report_mg)
        shutil.copy2(os.path.join(os.getcwd(),file),dir_report_mg)
        print(dir_report_mg)
        os.remove(file)
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
                        okr_name = row['okr']
                        name = row['癌症类型']
                        cancer = CancerTypes.query.filter(CancerTypes.name == name).first()
                        if cancer:
                            pass
                        else:
                            cancer = CancerTypes(name=name, okr_name=okr_name)
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
                if name == 'Barcode':
                    for row in dict_r:
                        name = row['barcode']
                        full_name = row['barcode_a']
                        barcode = Barcode.query.filter(Barcode.name == name).first()
                        if barcode:
                            Barcode.query.filter(Barcode.name == name).update({
                                'full_name': full_name
                            })
                        else:
                            barcode = Barcode(name=name, full_name=full_name)
                            db.session.add(barcode)
                if name == 'Sample':
                    for row in dict_r:
                        name = row['编号']
                        type = row['类型']
                        barcode = FlowItem.query.filter(FlowItem.name == name).first()
                        if barcode:
                            FlowItem.query.filter(FlowItem.name == name).update({
                                'type': type
                            })
                        else:
                            barcode = FlowItem(name=name, type=type)
                            db.session.add(barcode)
            # 利用item 添加新的项目

        db.session.commit()
        os.remove(file)
