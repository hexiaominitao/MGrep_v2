import re, os

import pandas as pd

from app.libs.upload import df2dict


def df_to_dict(df):
    '''
    :param df: pd.Dataframe
    :return: list
    '''
    result = []
    for i in df.index:
        dic_row = {}
        df_row = df.loc[i].copy()
        for k in df.columns:
            dic_row[k] = str(df_row[k])
        result.append(dic_row)
    return result


def del_db(db, snvs):
    if snvs:
        try:
            for snv in snvs:
                db.session.delete(snv)
        except:
            db.session.delete(snvs)


def model_to_dict(snvs, list_m):
    if snvs:
        for snv in snvs:
            list_m.append(snv.to_dict())
    return None


def first_check(snvs, list_m, list_c=None):
    if snvs:
        for snv in snvs:
            if list_c:
                if snv.status in list_c:
                    drugs = snv.drug
                    dic_snv = snv.to_dict()
                    if 'fu_type' not in dic_snv.keys():
                        dic_snv['fu_type'] = dic_snv['mu_name_usual']
                    l_drug = []
                    if drugs:
                        for drug in drugs:
                            l_drug.append(drug.to_dict())
                    dic_snv['drugs'] = l_drug
                    list_m.append(dic_snv)
            else:
                list_m.append(snv.to_dict())
    return None


def get_rep_item(item):
    pat = '(.*)([0-9]{2,3})(.*)'
    m = re.match(pat, item)
    if m:
        item = m.group(2)
    return item


def set_gene_list(list_gene, N):
    list_row = []
    dic_h = {2: 'r', 1: 'm', 0: 'l'}
    for gene_l in list_gene:
        dic_row = {}
        for i in range(N):
            if gene_l:
                tem = gene_l.pop()
                dic_row[dic_h.get(i)] = tem
            else:
                dic_row[dic_h.get(i)] = {'gene': '', 'transcript': ''}
        list_row.append(dic_row)
    return list_row


def dict2df(list_dic):
    dic_out = {}
    for k in (k for k in list_dic[0].keys()):
        dic_out[k] = []
        for dic in list_dic:
            dic_out[k].append(dic[k])
    df = pd.DataFrame(dic_out)
    return df


def get_okr(df, disease, gene, mutation, drug_effect, grade=None):
    levels = ['NCCN', 'Clinical + III', 'Clinical + II/III', 'Clinical + II', 'Clinical + I/II', 'Clinical + I']
    if grade:
        for i in ['FDA', 'ESMO', 'EMA']:
            levels.insert(1, i)
    df['drug_effect'].replace('.', 'indicated', inplace=True)
    df_mutation = df[df['disease'].str.contains(disease) &
                     df['gene_name'].str.contains(gene) & (df['protein_alteration'] == mutation)]
    df_list = []

    tem = set()
    if not df_mutation.empty:
        for level in levels:
            if level in ['NCCN', 'FDA', 'ESMO', 'EMA']:
                df_le = df_mutation[df_mutation['evidence_level'].str.contains(level)].copy()
            else:
                df_le = df_mutation[df_mutation['evidence_level'] == level].copy()
            if not df_le.empty:
                if tem:
                    for k in drug_effect - tem:
                        df_drug = df_le[df_le['drug_effect'] == k].copy()
                        if not df_drug.empty:
                            df_list.append(df_drug)
                            tem.add(k)
                else:
                    for k in drug_effect:
                        df_drug = df_le[df_le['drug_effect'] == k].copy()
                        if not df_drug.empty:
                            tem.add(k)
                            df_list.append(df_drug)

    return df_list, drug_effect - tem


def get_mutation_parent():
    file_parent = os.path.join(os.getcwd(), 'app/static/pre_report/template_config/variant_class_parent.csv')
    df_p = pd.read_csv(file_parent, delimiter=',', keep_default_na=False)
    dic_p = {}
    for k, p in df_p[['kids', 'parents']].values:
        if k in dic_p.keys():
            dic_p[k].append(p)
        else:
            if p:
                dic_p[k] = [p]
            else:
                dic_p[k] = ''
    return dic_p


def get_parent_variant(mutation, dic_mu, par_l):
    '''
    :param mutation: 突变
    :param dic_mu: 父子突变对应表
    :param par_l: 所有有关系的突变
    :return: par_l
    '''
    par = dic_mu.get(mutation)
    for k in dic_mu.keys():
        if mutation in k:
            par = dic_mu.get(k)

    if par:
        # par_l.append(mutation)
        for mu in par:
            par_l.append(mu)
            get_parent_variant(mu, dic_mu, par_l)
    return par_l


def okr_create(df, disease, gene, mutation, drug_effect):
    '''
    :param df: okr表格生成的dataframe
    :param disease: 肿瘤类型
    :param gene: 基因名称（融合的选其中一个）
    :param mutation: 突变（融合直接写fusion 例如：EML4-ALK fusion；gene：ALK; mutation: fusion）
    :param drug_effect: {'indicated', 'contraindicated', 'resistance', 'not_recommended'}
    :return: dict_out: okr详细信息  type: dict
    '''
    dic_p = get_mutation_parent()
    df_list, le_key = get_okr(df, disease, gene, mutation, drug_effect)
    if 'fusion' in mutation and gene in mutation:
        par_l = get_parent_variant(mutation, dic_p, [])
    else:
        par_l = get_parent_variant('{} {}'.format(gene, mutation), dic_p, [])

    list_mu = set()
    for mu in par_l:
        for p in set(df['protein_alteration'].values):
            if p in mu:
                list_mu.add(p)
    if df_list:
        if le_key:
            le_list, _ = get_okr(df, 'Unspecified Solid Tumor', gene, mutation, le_key)
            df_list.extend(le_list)
            for p in list_mu:
                le_list, _ = get_okr(df, disease, gene, p, le_key)
                df_list.extend(le_list)
        df_out = pd.concat(df_list, sort=False)
        dic_out = df2dict(df_out)
    else:
        dic_out = ''
    return dic_out


def okr_create_n(dic_in, df, disease, drug_effect):
    type = dic_in['type']
    if type == 'fusion':
        mutation = 'fusion'
    elif type == 'cnv':
        mutation = 'amplification'
    elif dic_in['mu_name_usual'] == '19号外显子缺失突变':
        mutation = 'exon 19 deletion'
    else:
        mutation = dic_in['mu_name_usual'].split(' ')[1]
    gene = dic_in['gene']
    dic_out = okr_create(df, disease, gene, mutation, drug_effect)
    return dic_out


def grade_mutation(df, disease, gene, mutation, drug_effect):
    df_list, le_key = get_okr(df, disease, gene, mutation, drug_effect, 1)
    dic_p = get_mutation_parent()
    if ('fusion' in mutation) and (gene in mutation):
        par_l = get_parent_variant(mutation, dic_p, [])
    else:
        par_l = get_parent_variant('{} {}'.format(gene, mutation), dic_p, [])

    list_mu = set()
    for mu in par_l:
        for p in set(df['protein_alteration'].values):
            if p in mu:
                list_mu.add(p)
    levels = set()
    grade = ''
    if df_list:
        if le_key:
            for p in list_mu:
                le_list, _ = get_okr(df, disease, gene, p, le_key, 1)
                df_list.extend(le_list)
        df_out = pd.concat(df_list, sort=False)
        evidence_level = set(df_out['evidence_level'].values)
        for level in evidence_level:
            level = level.split(' ')[0]
            levels.add(level)
        for k in ['NCCN', 'FDA', 'ESMO', 'EMA']:
            if k in levels:
                grade = 'I类'
        if not grade:
            if 'Clinical' in levels:
                grade = 'II类'
            else:
                grade = 'III类'
    else:
        grade = 'III类'
    return grade


def get_grade(dic_in, df, disease, drug_effect):
    type = dic_in['type']
    if type == 'fusion':
        mutation = 'fusion'
    elif type == 'cnv':
        mutation = 'amplification'
    elif dic_in['mu_name_usual'] == '19号外显子缺失突变':
        mutation = 'exon 19 deletion'
    else:
        mutation = dic_in['mu_name_usual'].split(' ')[1]
    gene = dic_in['gene']
    grade = grade_mutation(df, disease, gene, mutation, drug_effect)
    return grade


def get_drug(list_dic):
    list_nccn = []
    list_clinical = []
    for dic_out in list_dic.values():
        for level in ['NCCN', 'Clinical + III', 'Clinical + II/III']:
            if level in dic_out['evidence_level']:
                for row in dic_out['drug'].split(','):
                    list_nccn.append(
                        {'drug': row, 'level': level, 'drug_effect': dic_out['drug_effect'], 'id': dic_out['id']})
        for level in ['Clinical + II', 'Clinical + I/II', 'Clinical + I']:
            if level in dic_out['evidence_level']:
                for row in dic_out['drug'].split(','):
                    list_clinical.append(
                        {'drug': row, 'level': level, 'drug_effect': dic_out['drug_effect'], 'id': dic_out['id']})
    if list_nccn:
        drug = list_nccn
    elif list_clinical:
        drug = list_clinical if len(list_clinical) < 6 else list_clinical[:5]
    else:
        drug = []
    drug_set = set()
    effect_set = set()
    out_drug = []

    rep_eff = {'indicated': '敏感', 'contraindicated': '禁忌',
               'resistance': '耐药', 'not_recommended': '不推荐'}

    if drug:
        for row in drug:
            effect_set.add(row['drug_effect'])
        if 'indicated' in effect_set and 'not_recommended' in effect_set:
            for row in drug:
                if 'not_recommended' in row['drug_effect']:
                    drug.remove(row)
        for row in drug:
            drug_set.add(row['drug'])
        for row in drug:
            if row['drug'] in drug_set:
                effect = row['drug_effect']
                row['drug_effect'] = convert_str(effect, rep_eff)
                out_drug.append(row)
                drug_set.remove(row['drug'])
    return out_drug


def convert_str(row, rep):
    rep = dict((re.escape(k), v) for k, v in rep.items())
    pat = re.compile('|'.join(rep.keys()))
    out = pat.sub(lambda n: rep[re.escape(n.group(0))], row)
    return out
