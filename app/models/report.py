from . import db
from app.models.sample import SampleInfo

# sam_report = db.Table('sam_report',
#                       db.Column('sample_info_id', db.Integer(), db.ForeignKey('sample_info.id')),
#                       db.Column('report_id'), db.Integer(), db.ForeignKey('report.id'))

sam_report = db.Table('sam_report',
                      db.Column('report_id', db.Integer(), db.ForeignKey('report.id')),
                      db.Column('sample_info_id', db.Integer(), db.ForeignKey('sample_info.id'))
                      )


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    rep_code = db.Column(db.String(200), nullable=False)  # 系统内部报告编号 迈景编号+报告类型
    samples = db.relationship('SampleInfo',
                              secondary=sam_report, backref=db.backref('reports', lazy='dynamic'))
    mutation = db.relationship('Mutation', backref='report', lazy='dynamic')  # 突变


class ReportTemplate(db.Model):
    __tablename__ = 'report_template'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    item = db.Column(db.String(200), nullable=False)  # 检测项目
