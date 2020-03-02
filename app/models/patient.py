from . import db
from .sample import SampleInfo


# 病人信息
class PatientInfo(db.Model):
    __tablename__ = 'patient_info'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=True)  # 姓名
    age = db.Column(db.String(50), nullable=True)  # 年龄
    gender = db.Column(db.String(50), nullable=True)  # 性别
    nation = db.Column(db.String(50), nullable=True)  # 民族
    origo = db.Column(db.String(50), nullable=True)  # 籍贯
    contact = db.Column(db.String(50), nullable=True)  # 联系方式
    ID_number = db.Column(db.String(50), nullable=True)  # 身份证号
    diagnosis = db.Column(db.String(500), nullable=True)  # 临床诊断
    diagnosis_date = db.Column(db.Date(), nullable=True)  # 临床诊断日期
    pathological = db.Column(db.String(500), nullable=True)  # 病理诊断
    pathological_date = db.Column(db.Date(), nullable=True)  # 病理诊断日期
    other_diseases = db.Column(db.String(500), nullable=True)  # 其他疾病
    smoke = db.Column(db.String(50), nullable=True)  # 吸烟史
    # sample_info = db.relationship('SampleInfo', backref='patient_info', lazy='dynamic')
    family_info = db.relationship('FamilyInfo', backref='patient_info', lazy='dynamic')

    def to_dict(self):
        dict = {'id': self.id,
                'name': self.name,
                'age': self.age,
                'gender': self.gender,
                'nation': self.nation,
                'origo': self.origo,
                'contact': self.contact,
                'ID_number': self.ID_number,
                'other_diseases': self.other_diseases,
                'smoke': self.smoke}
        return dict


# 家族史
class FamilyInfo(db.Model):
    __tablename__ = 'family_info'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    is_family = db.Column(db.String(50), nullable=True)
    relationship = db.Column(db.String(50), nullable=True)
    diseases = db.Column(db.String(500), nullable=True)
    patient_id = db.Column(db.Integer(), db.ForeignKey('patient_info.id'))

    def to_dict(self):
        dict = {'is_family': self.is_family,
                'id': self.id,
                'relationship': self.relationship,
                'diseases': self.diseases}
        return dict
