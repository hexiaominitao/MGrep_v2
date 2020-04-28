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
    utc_t = local_t - datetime.timedelta(hours=8)
    utc_st = datetime.datetime.strftime(utc_t, "%Y-%m-%dT%H:%M:%S.%fZ")
    return utc_st