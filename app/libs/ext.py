import os, datetime, time

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import (Permission, Principal, RoleNeed)
from flask_uploads import UploadSet, DOCUMENTS, DATA, ARCHIVES

bcrypt = Bcrypt()
login_magager = LoginManager()
principal = Principal()

file_sam = UploadSet('filesam', DOCUMENTS)
file_okr = UploadSet('fileokr', ('tsv','json','xls','xlsx','zip'))


def str2time(string):
    try:
        if string and string != ' ':
            if len(string) == 6:
                out_time = datetime.datetime.strptime(string, '%Y%m')
            elif len(string) == 8:
                out_time = datetime.datetime.strptime(string, '%Y%m%d')
            else:
                out_time = None
        else:
            out_time = None
    except:
        out_time = None
    return out_time


def set_float(row):
    try:
        row = float(row)
    except:
        row = None
    return row

def get_local_time(str):
    if str:
        utc_time = datetime.datetime.strptime(str, "%Y-%m-%dT%H:%M:%S.%fZ")
        local_time = utc_time + datetime.timedelta(hours=8)
    else:
        local_time = None
    return local_time


def get_utc_time(local_t):
    """本地时间转UTC时间（-8: 00）"""
    if local_t:
        utc_t = local_t - datetime.timedelta(hours=8)
        utc_st = datetime.datetime.strftime(utc_t, "%Y-%m-%dT%H:%M:%S.%fZ")
    else:
        utc_st = ''
    return utc_st


def get_sample(applys):
    list_apply = []
    for apply in applys:
        sams = apply.sample_infos

        def get_list_dic(sams):
            list_sam = []
            if sams:
                for sam in sams:
                    dic_sam = sam.to_dict()
                    list_sam.append(dic_sam)
            return list_sam

        dic_apply = apply.to_dict()
        dic_apply['samplinfos'] = get_list_dic(sams)
        # print(get_list_dic(sams))
        pat = apply.patient_info_v
        if '岁' in pat.age:
            dic_apply['age_v'] = '岁'
            dic_apply['age'] = pat.age.strip('岁')
        elif '个月' in pat.age:
            dic_apply['age_v'] = '个月'
            dic_apply['age'] = pat.age.strip('个月')
        else:
            dic_apply['age_v'] = '岁'
            dic_apply['age'] = ''
        dic_apply['patient_info'] = pat.to_dict()
        # print([i.name for i in pat.treat_infos])

        dic_apply['family_info'] = get_list_dic(pat.family_infos) if get_list_dic(pat.family_infos) else [{
            'relationship': '',
            'age': '',
            'diseases': ''
        }]

        treat_info = get_list_dic(pat.treat_infos)
        dic_apply['treat_info'] = treat_info if treat_info else [{
            'item': '', 'name': '', 'treat_date': '', 'effect': ''
        }]

        rep_item_infos = apply.rep_item_infos
        dic_apply['rep_item'] = [i['name'] for i in get_list_dic(rep_item_infos)]
        dic_apply['send_methods'] = get_list_dic(apply.send_methods)[0] if get_list_dic(
            apply.send_methods) else {
            'the_way': '', 'to': '', 'phone_n': '', 'addr': ''
        }

        def is_snoke_i(str_s):
            if not str_s in ['', '无']:
                return {'is_smoke': '有', 'smoke': str_s}
            else:
                return {'is_smoke': str_s, 'smoke': ''}

        dic_apply['smoke_info'] = is_snoke_i(pat.smoke)
        list_apply.append(dic_apply)
    return list_apply