import os, json

from docxtpl import DocxTemplate,InlineImage

from flask import (jsonify, current_app, send_from_directory, Response, make_response, send_file)
from flask_restful import (reqparse, Resource, request)

from sqlalchemy import and_
from app.models import db
from app.models.user import User
from app.models.report import Report
from app.models.mutation import Mutation, CNV, SNV_INDEL, Fusion
from app.models.annotate import Annotate, OKR, AnnotateAuto

from app.libs.report import first_check, get_rep_item, set_gene_list
from app.libs.get_data import read_json, splitN


class ReportStart(Resource):
    '''
    报告开始制作:承包
    '''

    # todo 添加真实用户

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('page_per', type=int, help='每页数量')
        self.parser.add_argument('sams', help='报告', action='append')

    def get(self):

        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        args = self.parser.parse_args()
        page = args.get('page')
        page_per = args.get('page_per')
        reps = Report.query.order_by(Report.id.desc()).paginate(page=page, per_page=page_per, error_out=False)
        list_rep = []
        for rep in reps.items:
            report_user = rep.report_user
            if report_user == user.username:
                rep_dict = rep.to_dict()
                rep_dict['mg_id'] = rep.samples[0].mg_id
                list_rep.append(rep_dict)
        dict_rep = {'sample': list_rep, 'total': len(Report.query.all())}
        return jsonify(dict_rep)

    def post(self):
        data = request.get_data()
        sams = (json.loads(data)['sams'])
        err = ''
        report = ''
        mmsg = ''
        user = '伞兵一号'
        for sam in sams:
            sample = sam.get('sample_name')
            print(sample)

        return {'msg': mmsg, 'err': '{}'.format(err)}


class GetMutationList(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int, help='报告id')

    def get(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        args = self.parser.parse_args()
        rep_id = args.get('id')
        dic_m = {}
        print(rep_id)
        report = Report.query.filter(Report.id == rep_id).first()
        if report.stage == '突变初审':
            sam = report.samples[0]
            list_m = []
            mutation = report.mutation
            if mutation:
                snvs = mutation.snv
                cnvs = mutation.cnv
                fusions = mutation.fusion

                first_check(snvs, list_m)
                first_check(cnvs, list_m)
                first_check(fusions, list_m)
            dic_m['mutation'] = list_m
            dic_m['mg_id'] = sam.mg_id

        print(dic_m)
        return jsonify(dic_m)

    def post(self):
        data = request.get_data()
        sams = (json.loads(data)['sams'])
        for sam in sams:
            type = sam.get('type')
            id = sam.get('id')
            if type == 'snv_indel':
                snv = SNV_INDEL.query.filter(SNV_INDEL.id == id).update({
                    'status': '初审通过'
                })
            if type == 'cnv':
                cnv = CNV.query.filter(CNV.id == id).update({
                    'status': '初审通过'
                })
            if type == 'fusion':
                fusion = Fusion.query.filter(Fusion.id == id).update({
                    'status': '初审通过'
                })
            db.session.commit()
        return {'msg': '初审通过！'}

    def delete(self):
        data = request.get_data()
        sams = json.loads(data)['sams']
        for sam in sams:
            type = sam.get('type')
            id = sam.get('id')
            if type == 'snv_indel':
                snv = SNV_INDEL.query.filter(SNV_INDEL.id == id).update({
                    'status': '初审未通过'
                })
            if type == 'cnv':
                cnv = CNV.query.filter(CNV.id == id).update({
                    'status': '初审未通过'
                })
            if type == 'fusion':
                fusion = Fusion.query.filter(Fusion.id == id).update({
                    'status': '初审未通过'
                })
            db.session.commit()
        return {'msg': '初审未通过！'}


class ReportStage(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int, help='报告id')
        self.parser.add_argument('stage', type=str, help='当前步骤')

    def post(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        args = self.parser.parse_args()
        stage = args.get('stage')
        rep_id = args.get('id')
        stages = ['突变初审', '突变二审', '突变注释', '注释复核', '制作完成', '开始审核',
                  '初次审核', '再次审核', '审核完成', '开始发报', '发送完成', '报告完成']  # 报告步骤
        if stage in stages:
            report = Report.query.filter(Report.id == rep_id).update({
                'stage': stage
            })
            db.session.commit()
        return {'msg': '提交成功!!!'}


class EditMutation(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int, help='报告id')

    def get(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        args = self.parser.parse_args()
        rep_id = args.get('id')
        dic_m = {}
        print(rep_id)
        report = Report.query.filter(Report.id == rep_id).first()
        if report.stage in ['突变注释', '突变二审','报告完成']: # todo 简化
            sam = report.samples[0]
            list_m = []
            mutation = report.mutation
            if mutation:
                snvs = mutation.snv
                cnvs = mutation.cnv
                fusions = mutation.fusion
                list_c = None   # todo 简化
                first_check(snvs, list_m, list_c)
                first_check(cnvs, list_m, list_c)
                first_check(fusions, list_m, list_c)
            dic_m['mutation'] = list_m
            dic_m['mg_id'] = sam.mg_id

            # print(dic_m)
        return jsonify(dic_m)

    def post(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        data = request.get_data()
        sams = (json.loads(data)['sams'])
        if isinstance(sams, dict):
            sams = [sams]
        for sam in sams:
            id = sam.get('id')
            type = sam.get('type')
            grade = sam.get('grade')
            if type == 'snv_indel':
                SNV_INDEL.query.filter(SNV_INDEL.id == id).update({
                    'status': '二审通过',
                    'grade': grade
                })
            if type == 'cnv':
                CNV.query.filter(CNV.id == id).update({
                    'status': '二审通过',
                    'grade': grade
                })
            if type == 'fusion':
                Fusion.query.filter(Fusion.id == id).update({
                    'status': '二审通过',
                    'grade': grade
                })
            db.session.commit()
        return {'msg': '二审通过！'}

    def delete(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        data = request.get_data()
        sams = (json.loads(data)['sams'])
        id = sams.get('id')
        type = sams.get('type')
        if type == 'snv_indel':
            snv = SNV_INDEL.query.filter(SNV_INDEL.id == id).update({
                'status': '二审未通过'
            })
        if type == 'cnv':
            cnv = CNV.query.filter(CNV.id == id).update({
                'status': '二审未通过'
            })
        if type == 'fusion':
            fusion = Fusion.query.filter(Fusion.id == id).update({
                'status': '二审未通过'
            })
        db.session.commit()
        return {'msg': '二审未通过！'}


class AnnotateMutation(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int, help='报告id')
        self.parser.add_argument('cancer', type=str, help='癌症类型')

    def get(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        args = self.parser.parse_args()
        rep_id = args.get('id')
        dic_m = {}
        print(rep_id)
        report = Report.query.filter(Report.id == rep_id).first()
        if report.stage in ['突变注释', '注释复核']:
            sam = report.samples[0]
            patient = sam.patient_info
            list_m = []
            mutation = report.mutation
            if mutation:
                snvs = mutation.snv
                cnvs = mutation.cnv
                fusions = mutation.fusion
                list_c = ['二审通过']

                first_check(snvs, list_m, list_c)
                first_check(cnvs, list_m, list_c)
                first_check(fusions, list_m, list_c)
            dic_m['mutation'] = list_m
            dic_m['sample_info'] = sam.to_dict()
            dic_m['patient_info'] = patient.to_dict()
        # print(dic_m)

        return jsonify(dic_m)

    def post(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        data = request.get_data()
        sams = (json.loads(data)['sams'])
        args = self.parser.parse_args()
        cancer = args.get('cancer')
        for sam in sams:
            id = sam.get('id')
            type = sam.get('type')
            annotate = AnnotateAuto.query.filter(and_(AnnotateAuto.mu_name_usual == sam.get('mu_name_usual'),
                                                      AnnotateAuto.cancer == cancer,
                                                      AnnotateAuto.status == '审核通过')).first()
            if annotate:
                annotate = Annotate(mu_name_usual=annotate.mu_name_usual, cancer=annotate.cancer,
                                    annotate_c=annotate.annotate_c)
            else:
                annotate = Annotate(mu_name_usual=sam.get('mu_name_usual'), cancer=cancer,
                                    annotate_c=sam.get('annotate_c'))
            if type == 'snv_indel':
                snv = SNV_INDEL.query.filter(SNV_INDEL.id == id).first()
                if snv.annotate:
                    Annotate.query.filter(Annotate.id == snv.annotate.id).update({
                        'annotate_c': sam.get('annotate_c')
                    })
                else:
                    snv.annotate = annotate
            if type == 'cnv':
                cnv = CNV.query.filter(CNV.id == id).first()
                if cnv.annotate:
                    Annotate.query.filter(Annotate.id == cnv.annotate.id).update({
                        'annotate_c': sam.get('annotate_c')
                    })
                else:
                    cnv.annotate = annotate
            if type == 'fusion':
                fusion = Fusion.query.filter(Fusion.id == id).first()
                if fusion.annotate:
                    Annotate.query.filter(Annotate.id == fusion.annotate.id).update({
                        'annotate_c': sam.get('annotate_c')
                    })
                else:
                    fusion.annotate = annotate
            db.session.commit()
        return {'msg': '注释保存成功'}

    def put(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        # data = request.get_data()
        # sams = (json.loads(data)['sams'])
        args = self.parser.parse_args()
        cancer = args.get('cancer')
        rep_id = args.get('id')
        report = Report.query.filter(Report.id == rep_id).first()
        sam = report.samples[0]
        sam.cancer = cancer
        # disease_cancer = {'非小细胞肺癌': 'Non-Small Cell Lung Cancer'}
        db.session.commit()
        # report = Report.query.filter(Report.id == rep_id).first()
        # if report.stage == '突变注释':
        #     mutation = report.mutation
        #     if mutation:
        #         snvs = mutation.snv
        #         cnvs = mutation.cnv
        #         fusions = mutation.fusion
        #
        #         for snv in snvs:
        #             print(snv.mu_name_usual)
        #             okrs = OKR.query.filter(and_(OKR.disease == disease_cancer[cancer],OKR.gene_name==snv.gene,
        #                                         OKR.protein_alteration.like('EGFR L858R'))).all()
        #             for okr in okrs:
        #                 print(okr.id)

        return {'msg': '添加完成'}


class AnnotateCheck(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int, help='报告id')

    def get(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        args = self.parser.parse_args()
        rep_id = args.get('id')
        dic_m = {}
        print(rep_id)
        report = Report.query.filter(Report.id == rep_id).first()
        if report.stage == '注释复核':
            sam = report.samples[0]
            patient = sam.patient_info
            list_m = []
            mutation = report.mutation
            if mutation:
                snvs = mutation.snv
                cnvs = mutation.cnv
                fusions = mutation.fusion
                list_c = ['二审通过']

                first_check(snvs, list_m, list_c)
                first_check(cnvs, list_m, list_c)
                first_check(fusions, list_m, list_c)
            dic_m['mutation'] = list_m
            dic_m['sample_info'] = sam.to_dict()
            dic_m['patient_info'] = patient.to_dict()
        # print(dic_m)

        return jsonify(dic_m)


class ExportReport(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int, help='报告id')
        self.parser.add_argument('item', type=str, help='报告模板')
        self.parser.add_argument('note', type=str, help='未检测到')

    def post(self):
        token = request.headers.get('token')  # 权限
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        dir_pre = current_app.config['PRE_REPORT']
        path_docx = os.path.join(dir_pre, 'template_docx')
        dir_res = current_app.config['RES_REPORT']
        dir_report = os.path.join(dir_res, 'report')

        dir_pgm_remplate = os.path.join(dir_pre, 'template_config', 'template_pgm.json')
        config = read_json(dir_pgm_remplate, 'config')
        gene_card = read_json(dir_pgm_remplate, 'gene_card')
        transcript = read_json(dir_pgm_remplate, 'transcript')
        dict_items = {'card': ['10', '12', '25'], 'no_card': ['52']}

        # 转录本字典
        dic_transcript = {}
        for row in transcript:
            dic_transcript[row['gene']] = row['transcript']

        if not os.path.exists(dir_report):
            os.mkdir(dir_report)

        args = self.parser.parse_args()
        rep_id = args.get('id')
        item = args.get('item')
        note = args.get('note')
        dic_m = {}
        report = Report.query.filter(Report.id == rep_id).first()
        list_m = []
        list_card = []

        if note == '1':
            sam = report.samples[0]
            patient = sam.patient_info
            list_m = []
            dic_m['s'] = sam.to_dict()  # 样本信息
            dic_m['sp'] = sam.patient_info.to_dict()  # 病理信息
            dic_m['p'] = patient.to_dict()  # 病人信息

        else:
            if report.stage in ['突变注释', '突变二审','注释复核']: # todo 简化
                sam = report.samples[0]
                patient = sam.patient_info
                mutation = report.mutation
                if mutation:
                    snvs = mutation.snv
                    cnvs = mutation.cnv
                    fusions = mutation.fusion
                    list_c = ['二审通过']

                    first_check(snvs, list_m, list_c)
                    first_check(cnvs, list_m, list_c)
                    first_check(fusions, list_m, list_c)
                dic_m['s'] = sam.to_dict()  # 样本信息
                dic_m['sp'] = sam.patient_info.to_dict()  # 病理信息
                dic_m['p'] = patient.to_dict()  # 病人信息


        for cc in config:
            if item == cc['item']:
                rep_item = get_rep_item(cc['item'])
                dic_m['c'] = {'item': rep_item, '检测内容': cc['检测内容'],
                              '检测方法': cc['检测方法']}  # 报告配置文件
                list_mutation = []

                for row in cc['结果详情']:
                    gene = row['基因']
                    m_type = row['检测的变异类型']
                    r_mutation = []

                    if rep_item in dict_items['card']:
                        if list_m:
                            for mu in list_m:
                                if mu['gene'] == gene:
                                    row_ir = {'result': mu['mu_name'], 'mu_af': mu['mu_af'],
                                              'mu_name_usual': mu['mu_name_usual'], 'grade': mu['grade']}
                                    r_mutation.append(row_ir)
                            if r_mutation:
                                pass
                            else:
                                r_mutation = [{'result': '未检出', 'mu_af': '',
                                               'mu_name_usual': '', 'grade': ''}]
                            rep_mutation = {'gene': gene, 'm_type': m_type, 'result': r_mutation}
                            list_mutation.append(rep_mutation)
                        else:
                            r_mutation = [{'result': '未检出', 'mu_af': '',
                                           'mu_name_usual': '', 'grade': ''}]
                            rep_mutation = {'gene': gene, 'm_type': m_type, 'result': r_mutation}
                            list_mutation.append(rep_mutation)

                        for card in gene_card:
                            if gene == card['基因']:
                                list_card.append(card)

                        dic_m['gene_card'] = list_card  # gene card

                    elif rep_item in dict_items['no_card']:
                        if list_m:
                            for mu in list_m:
                                if mu['gene'] == gene:
                                    list_mutation.append(mu)
                        else:
                            list_mutation = []

                script_snv = [gene for gene in
                              splitN([{'gene': ge['基因'], 'transcript': dic_transcript.get(ge['基因'])} for ge in cc['结果详情']],
                                     3)]
                script_fusion = [gene for gene in splitN(
                    [{'gene': ge['基因'], 'transcript': dic_transcript.get(ge['基因'])} for ge in cc['结果详情'] if
                     '融合' in ge['检测的变异类型']], 3)]
                script_cnv = [gene for gene in
                              splitN([{'gene': ge['基因'], 'transcript': dic_transcript.get(ge['基因'])} for ge in cc['结果详情'] if
                                      '拷贝数变异' in ge['检测的变异类型']], 3)]
                script_other = [gene for gene in
                                splitN(
                                    [{'gene': ge['基因'], 'transcript': dic_transcript.get(ge['基因'])} for ge in cc['结果详情'] if
                                     ('VII' in ge['检测的变异类型'] or
                                      '14号外显子跳跃' in ge['检测的变异类型'])], 3)]
                dic_gene = {'突变': script_snv, '融合': script_fusion, '拷贝数变异': script_cnv, '跳跃': script_other}
                gene_list = []
                for k in ['突变', '拷贝数变异', '融合', '跳跃']:
                    if dic_gene[k]:
                        gene_list.append({'item': k, 'list_gene': set_gene_list(dic_gene[k], 3)})

                dic_m['mutation'] = list_mutation  # 突变信息
                dic_m['gene_list'] = gene_list  # 基因列表
                dic_m['list_m'] = list_m

                if list_m:
                    total_mutation = len(list_m)
                    all_mu = []
                    for mu in list_m:
                        all_mu.append('{} {}'.format(mu['mu_name_usual'],mu['mu_type']))
                    dic_m['mu_info'] = {'total': total_mutation, 'all': '、'.join(all_mu)}
                else:
                   a = [1 for ge in cc['结果详情']  if '融合' in ge['检测的变异类型']]
                   note_res = '和RNA融合' if a else ''
                   dic_m['note_res'] = '未检测到该样本的DNA变异'+ note_res

        temp_docx = os.path.join(path_docx,'12.docx')
        file = os.path.join(dir_report, '{}.docx'.format(item))

        docx = DocxTemplate(temp_docx)
        if list_card:
            myimage = InlineImage(docx, os.path.join(path_docx, 'appendix_3.png'))
            dic_m['img'] = myimage
        else:
            dic_m['img'] = ''
        docx.render(dic_m)
        docx.save(file)

        return {'msg': '报告成功生成！！'}

        # return send_from_directory(os.path.join(os.getcwd(), path_rep), '迈景基因检测报告_{}.pdf'.format(req_mg),
        #                            as_attachment=True)
