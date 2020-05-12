from . import db

# sam_report = db.Table('sam_report',
#                       db.Column('sample_info_id', db.Integer(), db.ForeignKey('sample_info.id')),
#                       db.Column('report_id'), db.Integer(), db.ForeignKey('report.id'))

# sam_report = db.Table('sam_report',
#                       db.Column('report_id', db.Integer(), db.ForeignKey('report.id')),
#                       db.Column('sample_info_v_id', db.Integer(), db.ForeignKey('sample_info_v.id'))
#                       )


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    run_name = db.Column(db.String(200)) # run_name
    req_mg = db.Column(db.String(200)) # 迈景编号
    report_item = db.Column(db.String(200)) # 报告模板类型
    stage = db.Column(db.String(200))  # 当前步骤
    report_user = db.Column(db.String(255))  # 操作人
    check_f = db.Column(db.String(255))  # 审核人
    check_r = db.Column(db.String(255))  # 复核人
    sample_id = db.Column(db.Integer(), db.ForeignKey('sample_info_v.id'))
    auto_okr = db.Column(db.String(10)) # 是否自动下载okr
    mutation = db.relationship('Mutations', backref='report', uselist=False)  # 突变

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'run_name': self.run_name,
            'req_mg': self.req_mg,
            'report_item': self.report_item,
            'stage': self.stage,
            'report_user': self.report_user,
            'check_f': self.check_f,
            'check_r': self.check_f,
            'auto_okr': self.auto_okr
        }
        return my_dict