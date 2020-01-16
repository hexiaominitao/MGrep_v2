from app.models import db


class Annotate(db.Model):
    __tablename__ = 'annotate'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mu_name_usual = db.Column(db.String(500), nullable=False)  # 临床常用名
    exon = db.Column(db.String(50), nullable=False)  # 外显子
    gene = db.Column(db.String(100), nullable=False)  # 基因
    mu_type = db.Column(db.String(100), nullable=False)  # 突变类型
    annotate_c = db.Column(db.String(5000), nullable=False)  # 解释
    drugs = db.Column(db.String(500), nullable=True)
