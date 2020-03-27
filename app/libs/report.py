import re

from flata import Flata
from flata.storages import JSONStorage
import docxtpl


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
                    annotate = snv.annotate
                    dic_snv = snv.to_dict()
                    if 'fu_type' not in dic_snv.keys():
                        dic_snv['fu_type'] = dic_snv['mu_name_usual']
                    if annotate:
                        dic_snv['annotate_c'] = annotate.annotate_c
                    else:
                        dic_snv['annotate_c'] = ''
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
