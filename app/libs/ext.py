import os, datetime, time
import zipfile, shutil
from io import BytesIO

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_principal import (Permission, Principal, RoleNeed)
from flask_uploads import UploadSet, DOCUMENTS, DATA, ARCHIVES

bcrypt = Bcrypt()
login_magager = LoginManager()
principal = Principal()

file_sam = UploadSet('filesam', DOCUMENTS)
file_okr = UploadSet('fileokr', ('tsv', 'json', 'xls', 'xlsx', 'zip', 'csv'))
file_pdf = UploadSet('filepdf', ('tsv',))


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


def str2time(str):
    time = datetime.datetime.strptime(str, "%Y.%m.%d")
    return time


def calculate_time(str_t1,str_t2):
    start = str2time(str_t1)
    end = str2time(str_t2)
    time = end -start
    return time.days + 1


def set_time_now():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%Y.%m.%d")


def archive_path(path_report):
    '''
    :param path_report: 报告输出文件夹
    :return:
    '''

    memory_zip = BytesIO()
    with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for arc_root, arc_dir, arc_file in os.walk(path_report):
            for file in arc_file:
                with open(os.path.join(arc_root, file), 'rb')as fp:
                    zf.writestr(file, fp.read())
    memory_zip.seek(0)
    return memory_zip


def archive_file(dir, files):
    memory_zip = BytesIO()
    with zipfile.ZipFile(memory_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            with open(os.path.join(dir, file), 'rb')as fp:
                zf.writestr(file, fp.read())
    memory_zip.seek(0)
    return memory_zip


def time_set(str):
    out = ''
    if str:
        if len(str) == 8:
            out = '{}.{}.{}'.format(str[:4], str[4:6], str[6:])
            try:
                datetime.datetime.strptime(out, "%Y.%m.%d")
            except:
                out = '日期错误'
        else:
            out = '日期错误'
    else:
        out = ''
    return out


def get_treat(row):
    out = []
    if row['靶向治疗'] and row['靶向治疗'] not in ['未知', '无']:
        out.append(row['靶向治疗'])
    for v in ['化疗', '放疗']:
        if row[v] and row[v] not in ['未知', '无']:
            out.append(v)
    if not out:
        out.append('无')
    return '、'.join(out)


def get_family_info(row):
    if row and row not in ['未知', '无']:
        family_info = row
    else:
        family_info = '无'
    return family_info


dic_mu_type = {'3_prime_UTR_variant': "3'UTR变异",
               '5_prime_UTR_variant': "5'UTR变异",
               'NMD_transcript_variant': 'NMD变异',
               'TFBS_ablation': '转录因子结合位点缺失',
               'TFBS_amplification': '转录因子结合位点扩增',
               'TF_binding_site_variant': '转录因子结合位点变异',
               'coding_sequence_variant': '编码变异',
               'downstream_gene_variant': '基因下游变异',
               'feature_elongation': '区域延长',
               'feature_truncation': '截短变异',
               'frameshift_variant': '移码突变',
               'incomplete_terminal_codon_variant': '末位密码子变异',
               'inframe_deletion': '非移码缺失变异',
               'inframe_insertion': '非移码插入变异',
               'intergenic_variant': '基因间区变异',
               'intron_variant': '内含子变异',
               'mature_miRNA_variant': 'miRNA变异',
               'missense_variant': '错义突变',
               'non_coding_transcript_exon_variant': '非编码变异',
               'non_coding_transcript_variant': '非编码基因变异',
               'protein_altering_variant': '氨基酸变异',
               'regulatory_region_ablation': '调控区缺失',
               'regulatory_region_amplification': '调控区扩增',
               'regulatory_region_variant': '调控区变异',
               'splice_acceptor_variant': '剪接位点突变',
               'splice_donor_variant': '剪接位点突变',
               'splice_region_variant': '剪接位点变异',
               'start_lost': '起始密码子变异',
               'start_retained_variant': '起始密码子变异（功能保留）',
               'stop_gained': '无义突变',
               'stop_lost': '终止密码子变异',
               'stop_retained_variant': '终止密码子变异（功能保留）',
               'synonymous_variant': '同义变异',
               'transcript_ablation': '大片段缺失',
               'transcript_amplification': '基因扩增',
               'upstream_gene_variant': '基因上游变异'}

dic_zsy_introduce = {
    '10': {'item': '10个肿瘤驱动基因（EGFR, KRAS, BRAF, PIK3CA, NRAS, ERBB2, KIT, PDGFRA, AKT1和MET）点突变检测。',
           'methods': '本方法采用多重PCR技术进行靶向捕获，运用Ion PGM进行高通量测序，'
                      '检测10个肿瘤驱动基因突变热点区域的单碱基替换突变和小片段的插入缺失突变。'
                      '目标区域的平均覆盖度不低于2000倍，检测灵敏度的下限为1%。'},
    '12': {
        'item': '12个肿瘤靶向治疗密切相关的基因，利用多重PCR捕获技术和半导体测序技术，'
                '检测包含12个基因（AKT1、ALK、BRAF、EGFR、ERBB2、KRAS、MAP2K1、MET、NRAS、PIK3CA、RET、ROS1）'
                '突变热点区域的点突变和小片段插入缺失检测，7个基因（ALK、BRAF、EGFR、ERBB2、KRAS、MET、PIK3CA）的扩增检测，'
                '3个基因（ALK、ROS1、RET）的融合检测，以及MET基因的第14外显子跳跃。',
        'methods': '本方法采用多重PCR 技术进行靶向捕获，运用Ion PGM进行高通量测序，'
                   '包含12个基因（AKT1、ALK、BRAF、EGFR、ERBB2、KRAS、MAP2K1、MET、NRAS、PIK3CA、RET、ROS1）'
                   '突变热点区域的点突变和小片段插入缺失检测，7个基因（ALK、BRAF、EGFR、ERBB2、KRAS、MET、PIK3CA）'
                   '的扩增检测，3个基因（ALK、ROS1、RET）的融合检测，以及MET基因的第14外显子跳跃。'
                   '检测方法采用多重PCR技术建库和新一代测序技术（NGS）测序，测序深度不低于1000x，'
                   '点突变和小片段插入缺失的检测下限不低于1.0%。'},
    '52': {
        'item': '35个肿瘤驱动基因（AKT1, ALK, AR, BRAF, CDK4, CTNNB1, DDR2, EGFR, ERBB2, ERBB3, ERBB4, ESR1,'
                ' FGFR2, FGFR3, GNA11, GNAQ, HRAS, IDH1, IDH2, JAK1, JAK2, JAK3, KIT, KRAS,'
                ' MAP2K1, MAP2K2, MET, MTOR, NRAS, PDGFRA, PIK3CA, RAF1, RET, ROS1, SMO）点突变检测,'
                '19个基因(ALK, AR, BRAF, CCND1, CDK4, CDK6, EGFR, ERBB2, FGFR1, FGFR2, FGFR3, FGFR4,'
                ' KIT, KRAS, MET, MYC, MYCN, PDGFRA, PIK3CA)拷贝数变异检测和23个基因(ABL1, AKT3, '
                'ALK, AXL, BRAF, ERG, ETV1, ETV4, ETV5, EGFR, ERBB2, FGFR1, FGFR2, FGFR3, MET, '
                'NTRK1, NTRK2, NTRK3, PDGFRA, PPARG, RAF1, RET, ROS1) 的融合转录本检测。',
        'methods': '本方法采用多重PCR技术进行靶向捕获，运用Ion PGM进行高通量测序，'
                   '检测35个肿瘤驱动基因突变热点区域的单碱基替换突变和小片段的插入缺失突变, '
                   '19个基因的拷贝数变异检测和23个基因的RNA融合转录本。'
                   '目标区域的平均覆盖度不低于1000倍，检测灵敏度的下限为1%。'}
}
