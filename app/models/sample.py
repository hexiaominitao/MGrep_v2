from datetime import datetime
from . import db


# 样本信息
class SampleInfo(db.Model):
    __tablename__ = 'sample_info'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mg_id = db.Column(db.String(50), nullable=False)  # 迈景编号
    req_mg = db.Column(db.String(50), nullable=False)  # 申请单号
    seq_item = db.Column(db.String(500), nullable=True)  # 检测项目
    seq_type = db.Column(db.String(50), nullable=True)  # 项目类型
    doctor = db.Column(db.String(50), nullable=True)  # 送检医生
    hosptial = db.Column(db.String(50), nullable=True)  # 送检单位
    room = db.Column(db.String(50), nullable=True)  # 送检科室
    cancer = db.Column(db.String(100))  # 结果解释用癌症类型
    diagnosis = db.Column(db.String(500), nullable=True)  # 临床诊断
    diagnosis_date = db.Column(db.Date(), nullable=True)
    pathological = db.Column(db.String(500), nullable=True)  # 病理诊断
    pathological_date = db.Column(db.Date(), nullable=True)
    recive_date = db.Column(db.Date(), nullable=True)  # 样本接受日期
    mode_of_trans = db.Column(db.String(50), nullable=True)  # 运输方式
    send_sample_date = db.Column(db.Date(), nullable=True)  # 送检日期
    reciver = db.Column(db.String(50), nullable=True)  # 送检人
    recive_room_date = db.Column(db.Date(), nullable=True)  # 收样日期
    sample_status = db.Column(db.String(50), nullable=True)  # 样本状态
    sample_type = db.Column(db.String(50), nullable=True)  # 样本类型
    sample_size = db.Column(db.String(50), nullable=True)  # 样本大小
    sample_count = db.Column(db.String(50), nullable=True)  # 样本数量
    seq_date = db.Column(db.Date(), nullable=True)  # 检测日期
    note = db.Column(db.String(500), nullable=True)  # 备注
    recorder = db.Column(db.String(50), nullable=True)  # 记录人
    reviewer = db.Column(db.String(50), nullable=True)  # 核对人
    # sample_qc = db.relationship('SampleQC', backref='sample_info', lazy='dynamic')  # 质控
    pathology_info = db.relationship('PathologyInfo', backref='sample_info', uselist=False)  # 病理信息
    patient_id = db.Column(db.Integer(), db.ForeignKey('patient_info.id'))  # 病人信息
    treat_info = db.relationship('TreatInfo', backref='sample_info', lazy='dynamic')  # 治疗信息
    operation_log = db.relationship('Operation', backref='sample_info', lazy='dynamic')  # 操作记录
    lab_operation_id = db.relationship('LabOperation', backref='sample_info', lazy='dynamic')  # 流转信息

    # operation_record = db.relationship('Tag', secondary=record, backref=db.backref('sample_info', lazy='dynamic'))
    # seq_info = db.relationship('SeqInfo', backref='sample_info', lazy='dynamic')

    def to_dict(self):
        dict = {
            "id": self.id,
            "mg_id": self.mg_id,
            "req_mg": self.req_mg,
            "seq_item": self.seq_item,
            "seq_type": self.seq_type,
            "doctor": self.doctor,
            "hosptial": self.hosptial,
            "room": self.room,
            'cancer':self.cancer,
            "diagnosis": self.diagnosis,
            "diagnosis_date": self.diagnosis_date,
            "pathological": self.pathological,
            "pathological_date": self.pathological_date,
            "recive_date": self.recive_date,
            "mode_of_trans": self.mode_of_trans,
            "send_sample_date": self.send_sample_date,
            "reciver": self.reciver,
            "recive_room_date": self.recive_room_date,
            "sample_status": self.sample_status,
            "sample_type": self.sample_type,
            "sample_size": self.sample_size,
            "sample_count": self.sample_count,
            "seq_date": self.seq_date,
            "note": self.note,
            "recorder": self.recorder,
            "reviewer": self.reviewer
        }
        return dict


#  病理信息
class PathologyInfo(db.Model):
    __tablename__ = 'pathology_info'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    pathology = db.Column(db.String(500), nullable=True)  # 病理审核
    view = db.Column(db.String(500), nullable=True)  # 镜下所见
    cell_count = db.Column(db.String(50), nullable=True)  # 样本内细胞数量
    cell_content = db.Column(db.Float(), nullable=True)  # 细胞含量
    spical_note = db.Column(db.String(500), nullable=True)  # 特殊说明
    sample_info_id = db.Column(db.Integer(), db.ForeignKey('sample_info.id'))

    # pathology_pic = db.relationship('PathologyPic', backref='pathology_info', lazy='dynamic')

    def to_dict(self):
        dict = {
            "id": self.id,
            'pathology': self.pathology,
            'view': self.view,
            'cell_count': self.cell_count,
            'cell_content': self.cell_content,
            'spical_note': self.spical_note
        }
        return dict


class TreatInfo(db.Model):
    __tablename__ = 'treat_info'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    is_treat = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(50), nullable=True)  # 项目
    star_time = db.Column(db.Date(), nullable=True)  # 开始时间
    end_time = db.Column(db.Date(), nullable=True)  # 结束时间
    effect = db.Column(db.String(100), nullable=True)  # 效果
    sample_info_id = db.Column(db.Integer(), db.ForeignKey('sample_info.id'))

    def to_dict(self):
        dict = {'id': self.id,
                'is_treat': self.is_treat,
                'name': self.name,
                'star_time': self.star_time,
                'end_time': self.end_time,
                'effect': self.effect,
                'is_family': self.is_family}
        return dict


class Operation(db.Model):
    __tablename__ = 'operation'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    time = db.Column(db.DateTime, default=datetime.now)  # 操作时间
    user = db.Column(db.String(255))  # 操作人
    name = db.Column(db.String(255))  # 操作步骤
    sample_info_id = db.Column(db.Integer(), db.ForeignKey('sample_info.id'))


class LabOperation(db.Model):
    __tablename__ = 'lab_operation'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    date = db.Column(db.Date())  # 结束时间
    user = db.Column(db.String(255))  # 操作人
    fill_time = db.Column(db.DateTime, default=datetime.now)  # 填写时间
    name = db.Column(db.String(255))  # 操作步骤
    lose_c = db.Column(db.Integer())  # 失控天数
    lose_reason = db.Column(db.String(225))  #
    time = db.Column(db.Integer())  # 环节天数
    status = db.Column(db.String(225))
    next_step = db.Column(db.String(225))
    not_transfer_reason = db.Column(db.String(500))
    sample_info_id = db.Column(db.Integer(), db.ForeignKey('sample_info.id'))
