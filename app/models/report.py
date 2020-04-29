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
    rep_code = db.Column(db.String(200), nullable=False)  # 系统内部报告编号 迈景编号+报告类型
    stage = db.Column(db.String(200))  # 当前步骤
    report_user = db.Column(db.String(255))  # 操作人
    check_f = db.Column(db.String(255))  # 审核人
    check_r = db.Column(db.String(255))  # 复核人
    sample_id = db.Column(db.Integer(), db.ForeignKey('sample_info_v.id'))
    mutation = db.relationship('Mutations', backref='report', uselist=False)  # 突变

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'rep_code': self.rep_code,
            'stage': self.stage,
            'report_user': self.report_user,
            'check_f': self.check_f,
            'check_r': self.check_f
        }
        return my_dict