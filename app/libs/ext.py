import os, datetime

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
