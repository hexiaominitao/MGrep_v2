from flata import Flata
from flata.storages import JSONStorage
import pandas as pd
import xlrd, os
import datetime
import zipfile
from collections import OrderedDict

from app.libs.ext import set_time_now, calculate_time, str2time


def save_json_file(db_path, dic_file, table_name):
    '''
    :param db_path: json文件保存路径
    :param dic_file: 要保存的字典
    :param table_name: 表的名字
    :return: None
    '''
    db = Flata(db_path, storage=JSONStorage)
    tb = db.table(table_name)
    tb.purge()
    tb.insert({'sams': dic_file})


def excel_to_dict(file):
    '''
    :param file: excel文件
    :param dict_key: 保存的键名
    :return: 字典
    '''
    df = pd.read_excel(file, keep_default_na=False)
    result = []
    for i in df.index:
        dic_row = {}
        df_row = df.loc[i].copy()
        for k in df.columns:
            dic_row[k] = str(df_row[k])
        result.append(dic_row)
    return result


def time_set(item):
    '''
    :param item: 字符串
    :return: 时间
    '''
    if item != ' ':
        if '.' in item:
            date = datetime.datetime.strptime(item, "%Y.%m.%d %H:%M")
        else:
            date = datetime.datetime.strptime(item, "%Y%m%d %H:%M")
        time = date.strftime('%Y-%m-%d %H:%M:%S')
    else:
        time = ''
    return time


def df2dict(df):
    '''
    :param df: pandas.Datafram
    :return:
    '''
    result_dict = {}
    for i in df.index:
        row_dict = {}
        df_row = df.loc[i].copy()
        for sam in df.columns:
            row_dict[sam] = str(df_row[sam])
        result_dict[i] = row_dict
    return result_dict


def get_seq_info(file):
    '''
    :param file: 上机信息表
    :return: 上机信息
    '''
    df = pd.read_excel(file, header=1, keep_default_na=False)
    df1 = df.copy()
    return df1.groupby(pd.Grouper(key='文件名(Run)'))


def excel2dict(file):
    '''
    :param file: 上机信息表
    :return: 字典
    '''
    df = pd.read_excel(file, header=1, keep_default_na=False)

    for i in df['Run name'].unique():
        if i:
            run_name = i
    df['Run name'] = run_name
    for i in df['上机时间'].unique():
        if i:
            start_T = i
    df['上机时间'] = start_T
    for i in df['下机时间'].unique():
        if i:
            end_T = i
    df['下机时间'] = end_T
    dict_f = df2dict(df)
    return dict_f


def get_excel_title(file):
    '''
    :param file: 上机信息表
    :return: 上机信息表标题
    '''
    data = xlrd.open_workbook(file)
    table = data.sheets()[0]
    title = table.row_values(0)[0].strip('上机信息表')
    return title


def tsv_to_list(file):
    '''
    :param file: tsv文件
    :return: 列表
    '''
    df = pd.read_csv(file, delimiter='\t')
    result = []
    for i in df.index:
        dic_row = {}
        df_row = df.loc[i].copy()
        for k in df.columns:
            dic_row[k] = str(df_row[k])
        result.append(dic_row)
    return result


def type_mu(row):
    dict_type = {'融合': 'fusion', '拷贝数变异': 'cnv'}
    v = dict_type.get(row)
    if v:
        pass
    else:
        v = 'snv_indel'
    return v


def file_2_dict(file):
    df = pd.read_excel(file, keep_default_na=False)
    df['type'] = [type_mu(v) for v in df['检测的突变类型'].values]
    result = []
    for i in df.index:
        dic_row = {}
        df_row = df.loc[i].copy()
        for k in df.columns:
            dic_row[k] = str(df_row[k])
        result.append(dic_row)
    return result


def df2list(df):
    '''
    :param df: pandas.Datafram
    :return:
    '''
    result_dict = []
    for i in df.index:
        row_dict = {}
        df_row = df.loc[i].copy()
        for sam in df.columns:
            row_dict[sam] = str(df_row[sam])
        result_dict.append(row_dict)
    return result_dict


def m_excel2list(file):
    df_a = pd.read_excel(file, sheet_name=None, keep_default_na=False)
    res_dict = {}
    for name, df in df_a.items():
        res_dict[name] = df2list(df)
    return res_dict


def unzip_file(file, path_unzip):
    zipfile.ZipFile(file).extractall(path_unzip)


def find_apply(rec_date, rep_mg, dir_apply):
    list_f = [p for p in os.listdir(os.path.join(os.getcwd(), dir_apply))]
    list_f.sort()
    list_f.reverse()
    if rec_date:
        dic_f = OrderedDict()
        dic_f.update({calculate_time(rec_date, f'{f[:4]}.{f[4:6]}.{f[6:]}'): f for f in list_f})
        list_k = ([f for f in dic_f.keys() if f > 0])
        list_k.sort()
        list_f = ([dic_f[k] for k in list_k])
    apply_f = []
    for f in list_f:
        root = os.path.join(os.getcwd(), dir_apply, f)
        for file in os.listdir(root):
            # print(file)
            if rep_mg in file and file.endswith('.pdf'):
                # print(file)
                apply_f.append(os.path.join(root, file))
                break

    return apply_f
