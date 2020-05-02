import os
from os import path
from docxtpl import DocxTemplate, InlineImage

from app.models.report import Report

from app.libs.report import first_check, get_rep_item, set_gene_list
from app.libs.get_data import read_json, splitN

from flask import (render_template, Blueprint, make_response, send_from_directory, current_app)

home = Blueprint('home', __name__)


@home.route('/')
def index():
    return 'hello'


@home.route('/api/download1/<id>_<item>_<note>/')
def download(id, item, note):
    print(id)
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

    rep_id = id

    dic_m = {}
    list_m = []
    list_card = []

    report = Report.query.filter(Report.id == rep_id).first()
    if note == '1':
        sam = report.samples[0]
        patient = sam.patient_info
        list_m = []
        dic_m['s'] = sam.to_dict()  # 样本信息
        dic_m['sp'] = sam.patient_info.to_dict()  # 病理信息
        dic_m['p'] = patient.to_dict()  # 病人信息

    else:
        if report.stage == '注释复核':
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
                    all_mu.append('{} {}'.format(mu['mu_name_usual'], mu['mu_type']))
                dic_m['mu_info'] = {'total': total_mutation, 'all': '、'.join(all_mu)}
            else:
                a = [1 for ge in cc['结果详情'] if '融合' in ge['检测的变异类型']]
                note_res = '和RNA融合' if a else ''
                dic_m['note_res'] = '未检测到该样本的DNA变异' + note_res

    temp_docx = os.path.join(path_docx, '12.docx')
    file = os.path.join(dir_report, '{}.docx'.format(item))
    if os.path.exists(file):
        pass
    else:
        docx = DocxTemplate(temp_docx)
        if list_card:
            myimage = InlineImage(docx, os.path.join(path_docx, 'appendix_3.png'))
            dic_m['img'] = myimage
        else:
            dic_m['img'] = ''
        docx.render(dic_m)
        docx.save(file)

    path_rep = os.path.join(os.getcwd(),dir_report)
    return send_from_directory(path_rep, '{}.docx'.format(item), as_attachment=True)
    # return file


@home.route('/api/download/<id>_<item>_<note>/')
def download1(id,item,note):
    dir_res = current_app.config['RES_REPORT']
    dir_report = os.path.join(dir_res, 'report')
    report = Report.query.filter(Report.id == id).first()
    sam = report.sample_info_v
    mg_id = sam.sample_id
    file = os.path.join(dir_report, '{}_{}.docx'.format(mg_id,item))
    if os.path.exists(file):
        path_rep = os.path.join(os.getcwd(), dir_report)
        # return send_from_directory(path_rep, '{}_{}.docx'.format(mg_id,item), as_attachment=True)
        response = make_response(
        send_from_directory(path_rep,  '{}_{}.docx'.format(mg_id,item), as_attachment=True))
        return response


@home.route('/api/download_okr/<filename>/')
def download_ork(filename):
    dir_res = current_app.config['RES_REPORT']
    path_res = os.path.join(dir_res, 'okr')
    file = os.path.join(path_res,'{}.xlsx'.format(filename))
    if file:
        path_rep = os.path.join(os.getcwd(), path_res)
        response = make_response(
            send_from_directory(path_rep, '{}.xlsx'.format(filename), as_attachment=True))
        return response