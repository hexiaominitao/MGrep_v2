from . import db


class PatientInfoV(db.Model):
    __tablename__ = 'patient_info_v'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)  # 姓名
    age = db.Column(db.String(50), nullable=True)  # 年龄
    gender = db.Column(db.String(50), nullable=True)  # 性别
    nation = db.Column(db.String(50), nullable=True)  # 民族
    origo = db.Column(db.String(50), nullable=True)  # 籍贯
    contact = db.Column(db.String(50), nullable=True)  # 联系方式
    ID_number = db.Column(db.String(50), nullable=True)  # 身份证号
    address = db.Column(db.String(50), nullable=True)  # 地址
    smoke = db.Column(db.String(50), nullable=True)  # 吸烟史

    applys = db.relationship('ApplyInfo', backref='patient_info_v', lazy='dynamic')  # 申请信息
    family_infos = db.relationship('FamilyInfoV', backref='patient_info_v', lazy='dynamic')  # 家族史信息
    treat_infos = db.relationship('TreatInfoV', backref='patient_info_v', lazy='dynamic')  # 治疗信息

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name,
            'age': self.age, 'gender': self.gender,
            'nation': self.nation, 'origo': self.origo, 'contact': self.contact,
            'ID_number': self.ID_number, 'address': self.address, 'smoke': self.smoke
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class FamilyInfoV(db.Model):
    __tablename__ = 'family_info_v'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    relationship = db.Column(db.String(100))  # 血亲
    age = db.Column(db.String(100))  # 年龄
    diseases = db.Column(db.String(500))  # 疾病
    patient_info_id = db.Column(db.Integer(), db.ForeignKey('patient_info_v.id'))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'relationship': self.relationship,
            'age': self.age, 'diseases': self.diseases
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class TreatInfoV(db.Model):
    __tablename__ = 'treat_info_v'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)  # 项目
    star_time = db.Column(db.Date(), nullable=True)  # 开始时间
    end_time = db.Column(db.Date(), nullable=True)  # 结束时间
    effect = db.Column(db.String(100), nullable=True)  # 效果
    patient_info_id = db.Column(db.Integer(), db.ForeignKey('patient_info_v.id'))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name,
            'star_time': self.star_time, 'end_time': self.end_time,
            'effect': self.effect
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class ApplyInfo(db.Model):
    __tablename__ = 'apply_info'
    id = db.Column(db.Integer(), primary_key=True)
    req_mg = db.Column(db.String(50), nullable=False)  # 申请单号
    pi_name = db.Column(db.String(50))  # PI姓名
    sales = db.Column(db.String(50))  # 销售代表
    outpatient_id = db.Column(db.String(50))  # 门诊号/住院号
    doctor = db.Column(db.String(50), nullable=True)  # 送检医生
    hosptial = db.Column(db.String(50), nullable=True)  # 送检单位
    room = db.Column(db.String(50), nullable=True)  # 送检科室
    pnumber = db.Column(db.String(100))  # 病理号
    cancer = db.Column(db.String(100))  # 结果解释用癌症类型
    cancer_d = db.Column(db.String(100))  # 肿瘤类型
    original = db.Column(db.String(500))  # 原发部位
    metastasis = db.Column(db.String(500))  # 转移部位
    pathological = db.Column(db.String(500), nullable=True)  # 病理诊断
    pathological_date = db.Column(db.Date(), nullable=True)  # 病理诊断日期

    patient_info_id = db.Column(db.Integer(), db.ForeignKey('patient_info_v.id'))  # 患者信息

    send_methods = db.relationship('SendMethodV', backref='apply_info', lazy='dynamic')  # 报告发送信息
    sample_infos = db.relationship('SampleInfoV', backref='apply_info', lazy='dynamic')  # 样本信息

    def to_dict(self):
        my_dict = {
            'id': self.id, 'req_mg': self.req_mg, 'pi_name': self.pi_name, 'sales': self.sales,
            'outpatient_id': self.outpatient_id, 'doctor': self.doctor, 'hosptial': self.hosptial,
            'room': self.room,'pnumber': self.pnumber,'cancer': self.cancer,'cancer_d': self.cancer_d,
            'original': self.original,'metastasis': self.metastasis,'pathological': self.pathological,
            'pathological_date': self.pathological_date
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class SendMethodV(db.Model):
    __tablename__ = 'send_method_v'
    id = db.Column(db.Integer(), primary_key=True)
    the_way = db.Column(db.String(20))
    to = db.Column(db.String(200))
    phone_n = db.Column(db.String(50))
    addr = db.Column(db.String(120))

    apply_info_id = db.Column(db.Integer(), db.ForeignKey('apply_info.id'))  # 申请信息

    def to_dict(self):
        my_dict = {
            'id': self.id, 'the_way': self.the_way,
            'to': self.to, 'phone_n': self.phone_n,
            'addr': self.addr
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class SampleInfoV(db.Model):
    __tablename__ = 'sample_info_v'
    id = db.Column(db.Integer(), primary_key=True)
    mg_id = db.Column(db.String(50), nullable=False)  # 迈景编号
    seq_type = db.Column(db.String(50), nullable=True)  # 项目类型
    sample_type = db.Column(db.String(50), nullable=True)  # 样本类型
    mth = db.Column(db.String(100))  # 采样方式
    mth_position = db.Column(db.String(100))  # 采样部位
    Tytime = db.Column(db.Date(), nullable=True)  # 采样时间
    sample_count = db.Column(db.String(50), nullable=True)  # 样本数量
    note = db.Column(db.String(500), nullable=True)  # 备注

    apply_info_id = db.Column(db.Integer(), db.ForeignKey('apply_info.id'))  # 申请信息

    report_items = db.relationship('ReportItem', backref='sample_info_v', lazy='dynamic')

    def to_dict(self):
        my_dict = {
            'id': self.id, 'mg_id': self.mg_id, 'seq_type': self.seq_type, 'sample_type': self.sample_type,
            'mth': self.mth, 'mth_position': self.mth_position, 'Tytime': self.Tytime,
            'sample_count': self.sample_count,
            'note': self.note
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class ReportItem(db.Model):
    __tablename__ = 'report_item'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))

    sample_info_id = db.Column(db.Integer(), db.ForeignKey('sample_info_v.id'))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict
