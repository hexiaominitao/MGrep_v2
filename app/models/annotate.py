from . import db


class Annotate(db.Model):
    __tablename__ = 'annotate'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mu_name_usual = db.Column(db.String(500), nullable=False)  # 临床常用名
    exon = db.Column(db.String(50), nullable=False)  # 外显子
    gene = db.Column(db.String(100), nullable=False)  # 基因
    mu_type = db.Column(db.String(100), nullable=False)  # 突变类型
    cancer = db.Column(db.String(500), nullable=False)  # 癌症类型
    annotate_c = db.Column(db.String(5000), nullable=False)  # 变异解读


# okr mysql -udebian-sys-maint -proqjjj6peel2eJMW
class ClinicInterpretation(db.Model):
    __tablename__ = 'clinic_interpretation'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    okr_version = db.Column(db.String(100), nullable=False)  # okr 版本
    okr = db.relationship('OKR', backref='clinic_interpretation', lazy='dynamic')


class OKR(db.Model):
    __tablename__ = 'okr'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    disease = db.Column(db.String(200))  # 癌症类型
    gene_name = db.Column(db.String(200))  # 基因名称
    protein_alteration = db.Column(db.String(200))  # 临床突变常用名称
    drug = db.Column(db.String(1000))  # 药物
    drug_effect = db.Column(db.String(200))
    evidence = db.Column(db.String(5000))  # 证据
    evidence_level = db.Column(db.String(200))  # 证据等级
    clinic_interpretation_id = db.Column(db.Integer(), db.ForeignKey('clinic_interpretation.id'))  # OK版本

    def to_dict(self):
        dict_tb = {
            'id': self.id,
            'disease': self.disease,
            'gene_name': self.gene_name,
            'protein_alteration': self.protein_alteration,
            'drug': self.drug,
            'drug_effect': self.drug_effect,
            'evidence': self.evidence,
            'evidence_level': self.evidence_level
        }

        return dict_tb
