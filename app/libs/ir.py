import zipfile, shutil, os, csv, re
import pandas as pd
from flata import Flata
from flata.storages import JSONStorage


def df2dict(df):
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
    tb.insert({'tsv': dic_file})


def read_json(path_db, table_name):
    '''
    :param path_db: json文件路径
    :return:
    '''
    db = Flata(path_db, storage=JSONStorage)
    tb = db.table(table_name)
    dic = tb.all()
    return dic


def merge_tsv(vcf):
    frams = []
    for f in reversed(vcf):
        df = pd.read_csv(f, delimiter='\t', header=2, keep_default_na=False)
        frams.append(df)
    df_merge = pd.concat(frams, sort=False)
    return df_merge


def unzip_file(path_wk, mg_id, rep_id, dir_rep):
    '''
    :param path_wk: 工作目录
    :param mg_id: 迈景编号
    :param rep_id: 报告编号
    :return: vcf文件
    '''
    dir_zip = dir_unzip = path_wk
    path_rep = os.path.join(dir_rep, rep_id)
    if not os.path.exists(path_rep):
        os.mkdir(path_rep)
    zip_files = []
    for name_zip in os.listdir(dir_zip):
        if not name_zip.endswith('.zip'):
            continue
        if mg_id in name_zip:
            path_unzip = os.path.join(dir_unzip, name_zip.strip('.zip'))
            zipfile.ZipFile(os.path.join(dir_zip, name_zip)).extractall(path_unzip)
            zip_files.append(path_unzip)
    vcf_files = []
    other_files = []
    for unzip_f in zip_files:
        for zip_root, zip_dir, zip_name in os.walk(unzip_f):
            for file_zip in zip_name:
                vcf = os.path.join(zip_root, file_zip)
                if file_zip.endswith('vcf') and 'Non-Filtered' in file_zip:
                    other_files.append(vcf)
                elif file_zip.endswith('full.tsv'):
                    vcf_files.append(vcf)
                elif file_zip.endswith('QC.pdf'):
                    other_files.append(vcf)
    for file in other_files:
        shutil.copy2(file, path_rep)
    for file in vcf_files:
        shutil.copy2(file, path_rep)
    df = merge_tsv(vcf_files)
    vcf = os.path.join(path_rep, '{}.full.tsv'.format(mg_id))
    df.to_csv(vcf, sep='\t', index=False)
    for p in zip_files:
        os.system('rm -r {}'.format(p))
    return vcf


def get_cnv(cnv):
    cnv = cnv.split(',')
    if cnv and len(cnv) > 1:
        if float(cnv[0].split(':')[1]) >= 4:
            return True
        if float(cnv[1].split(':')[1]) <= 1:
            return True
        return False
    else:
        return False


def convert_str(row, rep):
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pat = re.compile('|'.join(rep.keys()))
    out = pat.sub(lambda n: rep[re.escape(n.group(0))], row)
    return out


def ir_10086(tsv, excel_file, df_d=pd.DataFrame()):
    df = pd.read_csv(tsv, delimiter='\t', keep_default_na=False)

    # 生成af fao
    allele = [v.split(',') for v in df['allele_coverage'].values]
    coverage = [v for v in df['coverage'].values]
    af_l = []
    fao_l = []
    af1_l = []
    for a, c in zip(allele, coverage):
        if a[0] and int(c) > int(a[0]):
            fao = int(c) - int(a[0])
            af = ','.join([str(round((float(i) / float(c) * 100), 2)) + '%' for i in a if i != '0'][1:])
            af1 = (float(a[1]) / float(c) * 100)  # 辅助筛选
        else:
            fao = af = af1 = ''
        af_l.append(af)
        fao_l.append(fao)
        af1_l.append(af1)

    columns = [v for v in df.columns]
    columns.insert(columns.index('coverage'), 'AF')
    columns.insert(columns.index('coverage'), 'FAO')
    df['AF'] = af_l
    df['FAO'] = fao_l

    df_ir = df.copy()
    df_ir.columns = columns

    df['AF1'] = af1_l

    pat_fu = '^(missense|nonsense|nonframeshiftDeletion|nonframeshiftInsertion|' \
             'frameshiftDeletion|frameshiftInsertion|frameshiftBlockSubstitution' \
             '|nonframeshiftBlockSubstitution)'

    # 过滤 利用df.query() 生成mutation
    df['mu'] = [bool(re.match(pat_fu, function)) for function in df['function'].values]
    df['af1'] = [float(af) > 0 if af else False for af in df['AF1'].values]
    df_m = df.query('mu and af1')[columns].copy()

    # 生成fusion
    df_f = df[df['fusion_presence'].isin(["Present", 'Present-Non-Targeted'])].copy() \
        if 'fusion_presence' in columns else pd.DataFrame()

    # 生成cnv
    if 'CNV' in columns:
        df['cnv'] = [get_cnv(cnv) for cnv in df['confidence'].values]
        df_c = df.query('cnv and Subtype not in "REF"')[columns].copy()
    else:
        df_c = pd.DataFrame(columns=columns)

    rep_P = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C",
             "Gln": "Q", "Glu": "E", "Gly": "G", "His": "H",
             "Ile": "I", "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F",
             "Pro": "P", "Ser": "S", "Thr": "T", "Trp": "W",
             "Tyr": "Y", "Val": "V", "p.": "", }
    rep_F = {'missense': '错义突变', 'nonsense': '无义突变', 'nonframeshiftDeletion': '非移码缺失突变',
             'frameshiftDeletion': '移码缺失突变', 'nonframeshiftInsertion': '非移码插入突变',
             'frameshiftInsertion': '移码插入突变',
             'nonframeshiftBlockSubstitution': '非移码插入突变'}

    coding = [v.split('|')[0] for v in df_m['coding'].values]
    protein = [convert_str(v.split('|')[0], rep_P) for v in df_m['protein'].values]
    function_m = [convert_str(v.split('|')[0], rep_F) for v in df_m['function'].values]

    re_gene, de_gene = [], []
    for row in coding:
        if 'del' in row:
            gene = row.split('del')[-1]
            re_gene.append(gene)
            de_gene.append(gene + '/-')
        elif 'ins' in row:
            gene = row.split('ins')[-1]
            re_gene.append('-')
            de_gene.append('-/' + gene)
        else:
            gene = row[-3:].split('>')
            re_gene.append(gene[0])
            de_gene.append(gene[0] + '/' + gene[-1])

    title_Report = ['手工审核', '位置', '基因', '检测的突变类型', '变异全称', '丰度', '临床突变常用名称',
                    '支持序列数', 'maf', '外显子', '功能影响', '参考基因型', '检测基因型']

    df_rep = pd.DataFrame(columns=title_Report)
    # df['手工审核'] = []
    df_rep['位置'] = df_m['# locus']
    df_rep['基因'] = [v.split('|')[0] for v in df_m['gene'].values]
    df_rep['检测的突变类型'] = function_m
    df_rep['变异全称'] = ['{}({}):{} ({})'.format(t.split('|')[0],
                                              g.split('|')[0], c.split('|')[0], p.split('|')[0])
                      for t, g, c, p in zip(df_m['transcript'].values,
                                            df_m['gene'].values, df_m['coding'].values, df_m['protein'].values)]
    df_rep['丰度'] = [v.split('|')[0] for v in df_m['AF'].values]
    df_rep['临床突变常用名称'] = ['{} {}'.format(g.split('|')[0], p)
                          for g, p in zip(df_m['gene'].values, protein)]
    df_rep['支持序列数'] = df_m['FAO']
    df_rep['maf'] = df_m['maf']
    df_rep['外显子'] = [v.split('|')[0] for v in df_m['exon'].values]
    df_rep['功能影响'] = [v.split('|')[0] for v in df_m['type'].values]
    df_rep['参考基因型'] = re_gene
    df_rep['检测基因型'] = de_gene

    dic_df = {'IR': df_ir, 'IR过滤': df_m, 'CNV': df_c, 'Fusion': df_f, 'Report': df_rep}  # 表格文件名
    for k, df in dic_df.items():
        save_json_file(excel_file, df2dict(df), k)

    # 保存为excel
    # with pd.ExcelWriter(excel_file, mode='a') as writer:
    #     df_ir.to_excel(writer, sheet_name='IR', index=False)
    #     df_m.to_excel(writer, sheet_name='IR过滤', index=False)
    #     df_c.to_excel(writer, sheet_name='CNV', index=False)
    #     df_f.to_excel(writer, sheet_name='Fusion', index=False)
    #     df_rep.to_excel(writer, sheet_name='Report', index=False)
    #     pd.DataFrame().to_excel(writer, sheet_name='覆盖度', index=False)
    #     df_d.to_excel(writer, sheet_name='详情', index=False)


def save_mutation(path_wk, dir_rep, mg_id, rep_id):
    '''
    :param path_wk:  压缩文件所在目录
    :param dir_rep:  输出文件夹目录
    :param mg_id: 压缩文件编号
    :param rep_id: mg_id对应申请单号
    :param excel_file: 输出文件
    :return: None
    '''
    tsv = unzip_file(path_wk, mg_id, rep_id, dir_rep)
    excel_file = os.path.join(dir_rep,rep_id,'{}.json'.format(mg_id))
    ir_10086(tsv, excel_file)
