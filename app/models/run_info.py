from . import db


class RunInfo(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    start_T = db.Column(db.DateTime())
    end_T = db.Column(db.DateTime())
    platform = db.Column(db.String(255))
    seq_info = db.relationship('SeqInfo', backref='run_info', lazy='dynamic')

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name, 'start_T': self.start_T,
            'end_T': self.end_T, 'platform': self.platform
        }
        return my_dict


class SeqInfo(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    sample_name = db.Column(db.String(255))  # 迈景编号
    sample_mg = db.Column(db.String(255))  # 申请单号
    item = db.Column(db.String(255))  # 检测项目
    sam_type = db.Column(db.String(255))  # 样本类型
    barcode = db.Column(db.String(255))  # Barcode编号
    cell_percent = db.Column(db.String(255)) # 肿瘤细胞比例
    note = db.Column(db.String(255))  # 备注
    cancer = db.Column(db.String(255))  # 报告用癌症类型
    report_item = db.Column(db.String(255))  # 报告模板类型
    status = db.Column(db.String(255))  # 状态
    run_info_id = db.Column(db.Integer(), db.ForeignKey('run_info.id'))
    sample_info_id = db.Column(db.Integer(), db.ForeignKey('sample_info_v.id'))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'sample_name': self.sample_name,
            'sample_mg': self.sample_mg, 'item': self.item,
            'barcode': self.barcode, 'note': self.note,
            'status': self.status, 'cancer': self.cancer,
            'report_item': self.report_item, 'cell_percent':self.cell_percent,
            'sam_type': self.sam_type
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict
