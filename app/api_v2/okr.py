import os

from flask import jsonify, current_app
from flask_restful import reqparse, request, Resource

from app.models.annotate import OKR
from app.libs.ext import file_okr
from app.libs.upload import file_2_dict
from app.libs.report import dict2df, get_grade, okr_create_n, get_drug


class OkrAnnotate(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()

    def get(self):
        okrs = OKR.query.all()
        list_okr = []
        for okr in okrs:
            list_okr.append(okr.to_dict())
        df = dict2df(list_okr)
        cancers = set(df['disease'].values)
        data = {'cancers': [{'value': v, 'label': v} for v in cancers]}
        return jsonify(data)

    def post(self):
        path_wk = current_app.config['COUNT_DEST']
        dir_res = current_app.config['RES_REPORT']

        for file in os.listdir(path_wk):
            os.remove(os.path.join(path_wk, file))
        filename = file_okr.save(request.files['file'])
        print(filename)
        file = file_okr.path(filename)
        dic = file_2_dict(file)
        okrs = OKR.query.all()
        list_okr = []
        for okr in okrs:
            list_okr.append(okr.to_dict())
        df = dict2df(list_okr)

        cancer = request.form['cancer']
        drug_effect = {'indicated', 'contraindicated', 'resistance', 'not_recommended'}
        list_out = []
        if dic:
            for row in dic:
                row_s = {'gene': row.get('基因'), 'mu_type': row.get('检测的突变类型'),
                         'mu_name': row.get('变异全称'), 'mu_af': row.get('丰度'),
                         'mu_name_usual': row.get('临床突变常用名称'), 'reads': row.get('支持序列数'),
                         'maf': row.get('maf'), 'exon': row.get('外显子'),
                         'fu_type': row.get('检测基因型'), 'status': '等待审核',
                         'locus': row.get('位置'), 'type': row.get('type')}
                grade = get_grade(row_s, df, cancer, drug_effect)
                dic_out = okr_create_n(row_s, df, cancer, drug_effect)
                if dic_out:
                    drug = get_drug(dic_out)
                    out_drug = []
                    for d in drug:
                        out_drug.append('{}({}:{})'.format(d.get('drug'),
                                                           d.get('drug_effect'), d.get('level')))
                    row_s['drug'] = ','.join(out_drug)
                else:
                    row_s['drug'] = ''
                row_s['grade'] = grade
                list_out.append(row_s)
        path_res = os.path.join(dir_res, 'okr')
        out_file = os.path.join(path_res, '{}.xlsx'.format(filename.split('.')[0]))
        if not os.path.exists(path_res):
            os.mkdir(path_res)
        if list_out:
            df_out = dict2df(list_out)
            df_out.to_excel(out_file, index=False)

        return {'msg': '完成'}


class OkrResult(Resource):
    def get(self):
        dir_res = current_app.config['RES_REPORT']
        path_res = os.path.join(dir_res, 'okr')
        file_list = [{'file': v.split('.')[0]} for v in os.listdir(path_res)]
        return jsonify({'files': file_list})

    def delete(self):
        dir_res = current_app.config['RES_REPORT']
        path_res = os.path.join(dir_res, 'okr')
        for file in os.listdir(path_res):
            os.remove(os.path.join(path_res,file))
        return {'msg': '清空了！！！！'}