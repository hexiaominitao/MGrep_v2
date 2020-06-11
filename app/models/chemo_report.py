from . import db
from datetime import datetime


class ChemoDatabase(db.Model):
    __tablename__ = 'chemo_databse'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    rs = db.Column(db.String(200))
    gene = db.Column(db.String(200))
    level = db.Column(db.String(200))
    clin_type = db.Column(db.String(200))
    anno = db.Column(db.String(200))
    pmid = db.Column(db.String(256))
    re_gt = db.Column(db.String(200))
    good = db.Column(db.String(200))
    medium = db.Column(db.String(200))
    bed = db.Column(db.String(200))
    note = db.Column(db.String(200))
    drug = db.Column(db.String(200))
    cancer = db.Column(db.String(200))
    date = db.Column(db.String(200))

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'rs': self.rs,
            'gene': self.gene,
            'level': self.level,
            'clin_type': self.clin_type,
            'anno': self.anno,
            'pmid': self.pmid,
            're_gt': self.re_gt,
            'good': self.good,
            'medium': self.medium,
            'bed': self.bed,
            'note': self.note,
            'drug': self.drug,
            'cancer': self.cancer,
            'date': self.date
        }
        return my_dict


class ChemoReport(db.Model):
    __tablename__ = 'chemo_report'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mgid = db.Column(db.String(200))
    res_name = db.Column(db.String(200))
    state = db.Column(db.String(200))
    reporter = db.Column(db.String(200))
    report_temp = db.Column(db.String(200))
    report_cancer = db.Column(db.String(200))
    report_dir = db.Column(db.String(200))
    report_date = db.Column(db.String(200))
    submit_time = db.Column(db.DateTime, default=datetime.now())

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'mgid': self.mgid,
            'res_name': self.res_name,
            'state': self.state,
            'reporter': self.reporter,
            'report_temp': self.report_temp,
            'report_cancer': self.report_cancer,
            'report_dir': self.report_dir,
            'report_date': self.report_date
        }
        return my_dict


class ReportTemplet(db.Model):
    __tablename__ = 'report_template'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    name = db.Column(db.String(200))
    project = db.Column(db.String(200))
    doc_template = db.Column(db.String(200))
    version = db.Column(db.String(200))
    note = db.Column(db.String(200))
    submit_time = db.Column(db.DateTime, default=datetime.now())

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'name': self.name,
            'project': self.project,
            'doc_template': self.doc_template,
            'version': self.version,
            'note': self.note,
        }
        return my_dict
