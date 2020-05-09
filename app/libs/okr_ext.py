import csv, os
import json
import requests

from flata import Flata
from flata.storages import JSONStorage
from bs4 import BeautifulSoup
from docxtpl import DocxTemplate, InlineImage


def therapy_dict(therapy):
    list_therapy = {'目前来自FDA 靶向药物信息': ['目前来自FDA 靶向药物信息'],
                    '目前来自NCCN 靶向药物信息': ['目前来自NCCN 靶向药物信息'],
                    '目前来自EMA 靶向药物信息': ['目前来自EMA 靶向药物信息'],
                    '目前来自ESMO 靶向药物信息': ['目前来自ESMO 靶向药物信息'],
                    '目前来自Clinical Trials 靶向药物信息': ['目前来自Clinical Trials 靶向药物信息']}
    dic_index = {}
    dic_the = {}
    for key, index in list_therapy.items():
        if index in therapy:
            dic_index[therapy.index(index)] = key
    # print(dic_index)
    if dic_index:
        sort_index = list(dic_index.keys())
        sort_index.sort()
        for i in range(len(sort_index)):
            if i < len(sort_index) - 1:
                dic_the[dic_index[sort_index[i]]] = therapy[sort_index[i] + 1: sort_index[i + 1]]
            else:
                dic_the[dic_index[sort_index[i]]] = therapy[sort_index[i] + 1:]

    dic_out = {}
    for k, v in dic_the.items():
        dic_the1 = {}
        time = v.pop(0)
        dic_the1['time'] = time[1]
        list_the = []
        title = v.pop(0)
        dic_the1['title'] = title
        # print(title)
        for row in v:
            # print(row)
            dic_row = {}
            for i in title:
                # print(i)
                soup = BeautifulSoup(row[title.index(i)], 'html.parser')
                dic_row[i] = soup.get_text()
            list_the.append(dic_row)
        dic_the1['therapy'] = list_the
        dic_out[k] = dic_the1

    return dic_out


def okr_list2dic(therapy, item):
    list = therapy.get(item)
    title = list.pop(0)
    dic_out = {}
    dic_out['title'] = title
    list_out = []
    for row in list:
        dic_row = {}
        if '美国食品药品监督管理局' in row[0]:
            dic_out['note'] = row[0]
        else:
            for i in title:
                dic_row[i] = row[title.index(i)]
            list_out.append(dic_row)
    dic_out[item] = list_out
    return dic_out


def strip_div(row):
    list_div = ['<ul><li>', '</li></ul>', '</', '</ul>']
    for div in list_div:
        print(div)
        row.strip('<ul><li>')
    return row


def okr(all):
    dic_index = {}
    list_index = {'临床上显著生物标志物': ['临床上显著生物标志物'],
                  '基于包含的数据源，无临床意义的流行癌症生物标志物': ['基于包含的数据源，无临床意义的流行癌症生物标志物'],
                  '基因变异相应靶向治疗方案': ['基因变异相应靶向治疗方案'],
                  '相关疗法详情': ['相关疗法详情'], '预后细节': ['预后细节'], '诊断细节': ['诊断细节']}
    # print(all)
    dic_re = {}
    for key, index in list_index.items():
        if index in all:
            dic_index[all.index(index)] = key
    if dic_index:
        sort_index = list(dic_index.keys())
        sort_index.sort()
        for i in range(len(sort_index)):
            if i < len(sort_index) - 1:
                dic_re[dic_index[sort_index[i]]] = all[sort_index[i] + 1: sort_index[i + 1] - 1]
            else:
                dic_re[dic_index[sort_index[i]]] = all[sort_index[i] + 1: -1]
    if dic_re:
        dic_re['相关疗法详情'] = therapy_dict(dic_re.get('相关疗法详情'))
        dic_re['临床上显著生物标志物'] = okr_list2dic(dic_re, '临床上显著生物标志物')
        dic_re['基因变异相应靶向治疗方案'] = okr_list2dic(dic_re, '基因变异相应靶向治疗方案')
        dic_re['版本'] = all[-1][0]
        dic_re['样本癌症类型'] = all[1][1]

    return dic_re


def fileokr_to_dict(okr_file):
    file_content = []
    with open(okr_file, 'r') as f:
        tsv_f = csv.reader(f, delimiter='\t')
        for row in tsv_f:
            if row:
                file_content.append(row)

    dict_okr = okr(file_content)
    return dict_okr


import os

BASE_URL = '192.168.1.103:8088/api/okr'
USER = 'cjhconfig'
PASSWORD = '123456'



def make_service_request(func, endpoint, data=None, files=None, headers=None):
    url = 'http://{0}:{1}@{2}/{3}'.format(USER, PASSWORD, BASE_URL, endpoint)
    return func(url, data=data, files=files, headers=headers)


def post(endpoint, data=None, files=None, headers=None):
    return make_service_request(requests.post, endpoint, data, files, headers)


def create_reports_using_report_file(vcf_file,cancer, out_file):
    REPORT_OPTIONS = {'filterPresetID': 100,
                      'reportTemplateID': 106,
                      'reportFormat': 'TXT',
                      'useGrayscale': False,
                      'cancerType': cancer,
                      'fields': [{'name': 'Sample ID', 'value': '12345'}]}
    request_data = {'options': json.dumps(REPORT_OPTIONS)}
    files = {'file': (vcf_file, open(vcf_file))}
    response = post('report/file', data=request_data, files=files)
    out = open(out_file, 'wb')
    out.write(response.content)


def is_okr(okr_f,k):
    with open(okr_f,'r')as f:
        fc = csv.reader(f,delimiter='\t')
        list_f = []
        for row in fc:
            if row:
                list_f.append(row[0])
    if k in list_f:
        return 0
    else:
        return 1


if __name__ == '__main__':
    VCF_file = './test.vcf'
    out_file = './test.txt'
    create_reports_using_report_file(VCF_file, out_file)
