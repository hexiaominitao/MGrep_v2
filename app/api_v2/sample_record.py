import json

from flask import (jsonify, current_app)
from flask_restful import (reqparse, Resource, fields, request)
from sqlalchemy import and_

from app.models import db
from app.models.user import User
from app.models.record_config import  SalesInfo, HospitalInfo, \
    SampleType, SeqItems, CancerTypes
from app.models.sample_v import PatientInfoV, FamilyInfoV, TreatInfoV, ApplyInfo, \
    SendMethodV, SampleInfoV, ReportItem
from app.libs.ext import get_local_time, get_utc_time


class SampleInfoRecord(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('page', type=int, help='页码')
        self.parser.add_argument('per_page', type=int, help='每页数量')

    def get(self):
        args = self.parser.parse_args()
        page = args.get('page')
        per_page = args.get('per_page')

        token = request.headers.get('token')
        user = User.verify_auth_token(token)
        if not user:
            return {'msg': '无访问权限'}, 401

        applys = ApplyInfo.query.order_by(ApplyInfo.id.desc()). \
            paginate(page=page, per_page=per_page, error_out=False)
        list_apply = []
        total = len(ApplyInfo.query.all())
        for apply in applys.items:
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
            print(get_list_dic(sams))
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
            print([i.name for i in pat.treat_infos])

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
            dic_apply['seq_type'] = [i['name'] for i in get_list_dic(rep_item_infos)]
            dic_apply['send_methods'] = get_list_dic(apply.send_methods)[0]

            def is_snoke_i(str_s):
                if not str_s in ['', '无']:
                    return {'is_smoke': '有', 'smoke': str_s}
                else:
                    return {'is_smoke': str_s, 'smoke': ''}

            dic_apply['smoke_info'] = is_snoke_i(pat.smoke)
            list_apply.append(dic_apply)

        print(list_apply)
        return jsonify({'sample': list_apply, 'total': total, 'test': {'name': 'hah'}})

    def post(self):
        data = request.get_data()
        sams = (json.loads(data)['samples'])
        for sam in sams:
            mg_id = sam['mg_id']
            req_mg = sam['req_mg']
            name = sam['patient_info']['name']
            if name and req_mg:
                pass
            else:
                return {'msg': '请填写患者姓名和申请单号'}
            ID_number = sam['patient_info']['ID_number']
            code = req_mg[4:8]
            sale = SalesInfo.query.filter(SalesInfo.code == code).first()
            smoke = sam['smoke_info']['smoke'] if sam['smoke_info']['smoke'] else sam['smoke_info']['is_smoke']
            pat = PatientInfoV.query.filter(and_(PatientInfoV.ID_number == ID_number,
                                                 PatientInfoV.name == name)).first()
            if pat:
                pass
            else:
                pat = PatientInfoV(name=name, age=sam['patient_info']['age'],
                                   gender=sam['patient_info']['gender'], nation=sam['patient_info']['nation'],
                                   origo=sam['patient_info']['origo'], contact=sam['patient_info']['contact'],
                                   ID_number=ID_number, smoke=smoke, have_family=sam['patient_info']['have_family'],
                                   targeted_info=sam['patient_info']['targeted_info'],
                                   chem_info=sam['patient_info']['chem_info'],
                                   radio_info=sam['patient_info']['radio_info'])
                db.session.add(pat)
            for fam in sam['family_info']:
                if fam['relationship']:
                    family = FamilyInfoV(relationship=fam['relationship'], age=fam['age'],
                                         diseases=fam['diseases'])
                    db.session.add(family)
                    pat.family_infos.append(family)

            for treat in sam['treat_info']:
                if (treat['treat_date']):
                    start_t = treat['treat_date'][0]
                    end_t = treat['treat_date'][1]
                    treat_info = TreatInfoV(item=treat['item'], name=treat['name'], star_time=get_local_time(start_t),
                                            end_time=get_local_time(end_t), effect=treat['effect'])
                    db.session.add(treat_info)
                    pat.treat_infos.append(treat_info)

            apply = ApplyInfo.query.filter(and_(ApplyInfo.req_mg == req_mg, ApplyInfo.mg_id == mg_id)).first()
            if apply:
                pass
            else:
                apply = ApplyInfo(req_mg=req_mg, mg_id=mg_id, pi_name=sam['pi_name'], sales=sale.name,
                                  outpatient_id=sam['outpatient_id'], doctor=sam['doctor'], hosptial=sam['hosptial'],
                                  room=sam['room'], cancer_d=sam['cancer_d'], original=sam['original'],
                                  metastasis=sam['metastasis'], pathological=sam['pathological'],
                                  pathological_date=get_local_time(sam['pathological_date']), note=sam['note'])
                db.session.add(apply)
                pat.applys.append(apply)
            send_m = sam['send_methods']
            send = SendMethodV(the_way=send_m['the_way'], to=send_m['to'],
                               phone_n=send_m['phone_n'], addr=send_m['addr'])
            db.session.add(send)
            apply.send_methods.append(send)

            samples = sam['samplinfos']
            print(samples)
            for sample in samples:

                sample_id = '{}{}'.format(mg_id, sample['code'])
                print(sample_id)
                sample_info = SampleInfoV.query.filter(SampleInfoV.sample_id == sample_id).first()
                if sample_info:
                    pass
                else:
                    sample_info = SampleInfoV(sample_id=sample_id, pnumber=sample['pnumber'],
                                              sample_type=sample['sample_type'],
                                              Tytime=get_local_time(sample['Tytime']),
                                              mth=sample['mth'], mth_position=sample['mth_position'],
                                              sample_count=sample['counts'], note=sample['note'])
                    db.session.add(sample_info)
                    apply.sample_infos.append(sample_info)
            for item in sam['seq_type']:
                report_item = ReportItem.query.filter(and_(ReportItem.req_mg == req_mg,
                                                           ReportItem.name == item)).first()
                if report_item:
                    pass
                else:
                    report_item = ReportItem(req_mg=req_mg, name=item)
                    db.session.add(report_item)
                    apply.rep_item_infos.append(report_item)
            db.session.commit()

        return {'msg': '保存成功！！！'}

    def put(self):
        data = request.get_data()
        sams = (json.loads(data)['samples'])
        for sam in sams:
            mg_id = sam['mg_id']
            req_mg = sam['req_mg']
            pat_info = sam['patient_info']
            ID_number = pat_info['ID_number']
            code = req_mg[4:8]
            print(pat_info)
            sale = SalesInfo.query.filter(SalesInfo.code == code).first()
            apply = ApplyInfo.query.filter(ApplyInfo.id == sam['id']).first()
            ApplyInfo.query.filter(ApplyInfo.id == sam['id']).update({
                'req_mg': req_mg, 'mg_id': mg_id, 'pi_name': sam['pi_name'], 'sales': sale.name,
                'outpatient_id': sam['outpatient_id'], 'doctor': sam['doctor'], 'hosptial': sam['hosptial'],
                'room': sam['room'], 'cancer_d': sam['cancer_d'], 'original': sam['original'],
                'metastasis': sam['metastasis'], 'pathological': sam['pathological'],
                'pathological_date': get_local_time(sam['pathological_date']),
                'note': sam['note']
            })

            smoke = sam['smoke_info']['smoke'] if sam['smoke_info']['smoke'] else sam['smoke_info']['is_smoke']
            pat = apply.patient_info_v
            PatientInfoV.query. \
                filter(PatientInfoV.id == pat.id) \
                .update({'name': pat_info['name'], 'gender': pat_info['gender'],
                         'nation': pat_info['nation'], 'origo': pat_info['origo'],
                         'age': pat_info['age'], 'ID_number': ID_number,
                         'smoke': smoke, 'have_family': pat_info['have_family'],
                         'targeted_info': pat_info['targeted_info'], 'chem_info': pat_info['chem_info'],
                         'radio_info': pat_info['radio_info']
                         })
            for treat in sam['treat_info']:
                if treat['treat_date']:
                    start_t = treat['treat_date'][0]
                    end_t = treat['treat_date'][1]
                    if treat.get('id'):
                        TreatInfoV.query.filter(TreatInfoV.id == treat['id']).update({
                            'item': treat['item'], 'name': treat['name'], 'star_time': get_local_time(start_t),
                            'end_time': get_local_time(end_t), 'effect': treat['effect']
                        })
                    else:
                        treat_info = TreatInfoV(item=treat['item'], name=treat['name'],
                                                star_time=get_local_time(start_t),
                                                end_time=get_local_time(end_t), effect=treat['effect'])
                        db.session.add(treat_info)
                        pat.treat_infos.append(treat_info)
            for fam in sam['family_info']:
                if fam['relationship']:
                    if fam.get('id'):
                        FamilyInfoV.query.filter(FamilyInfoV.id == fam['id']).update({
                            'relationship': fam['relationship'], 'age': fam['age'],
                            'diseases': fam['diseases']
                        })
                    else:
                        family = FamilyInfoV(relationship=fam['relationship'], age=fam['age'],
                                             diseases=fam['diseases'])
                        db.session.add(family)
                        pat.family_infos.append(family)
            for sample in sam['samplinfos']:
                sample_id = '{}{}'.format(mg_id, sample['code'])
                if sample.get('id'):
                    SampleInfoV.query.filter(SampleInfoV.id == sample['id']).update({
                        'sample_id': sample_id, 'pnumber': sample['pnumber'],
                        'sample_type': sample['sample_type'],
                        'mth': sample['mth'], 'mth_position': sample['mth_position'],
                        'Tytime': get_local_time(sample['Tytime']),
                        'sample_count': sample['counts'], 'note': sample['note']
                    })
                else:
                    sample_info = SampleInfoV(sample_id=sample_id, pnumber=sample['pnumber'],
                                              sample_type=sample['sample_type'],
                                              Tytime=get_local_time(sample['Tytime']),
                                              mth=sample['mth'], mth_position=sample['mth_position'],
                                              sample_count=sample['counts'], note=sample['note'])
                    db.session.add(sample_info)
                    apply.sample_infos.append(sample_info)
            SendMethodV.query.filter(SendMethodV.id == sam['send_methods']['id']).update({
                'the_way': sam['send_methods']['the_way'], 'to': sam['send_methods']['to'],
                'phone_n': sam['send_methods']['phone_n'], 'addr': sam['send_methods']['addr'],
            })
            for item in apply.rep_item_infos:
                db.session.delete(item)
            for item in sam['seq_type']:
                report_item = ReportItem.query. \
                    filter(and_(ReportItem.req_mg == req_mg,
                                ReportItem.name == item)).first()
                if report_item:
                    pass
                else:
                    report_item = ReportItem(req_mg=req_mg, name=item)
                    db.session.add(report_item)
                    apply.rep_item_infos.append(report_item)
        db.session.commit()

        return {'msg': '更新成功！！！'}


class SalesHospitalType(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('item')

    def get(self):
        reslt = {}

        def get_info(sales):
            list_sale = []
            for sale in sales:
                list_sale.append(sale.to_dict())
            return list_sale

        reslt['sales'] = get_info(SalesInfo.query.all())
        reslt['hospital'] = get_info(HospitalInfo.query.all())
        reslt['type'] = get_info(SampleType.query.all())
        reslt['cancers'] = get_info(CancerTypes.query.all())
        reslt['seq_items'] = get_info(SeqItems.query.all())
        reslt['samples'] = get_info(ApplyInfo.query.all())
        # return jsonify({'sales': list_sale, 'hospital': list_hospital, 'type': list_type})
        return jsonify(reslt)
