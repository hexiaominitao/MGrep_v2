from . import db


class Annotate(db.Model):
    __tablename__ = 'annotate'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mu_name_usual = db.Column(db.String(500), nullable=False)  # 临床常用名
    exon = db.Column(db.String(50))  # 外显子
    gene = db.Column(db.String(100))  # 基因
    mu_type = db.Column(db.String(100))  # 突变类型
    cancer = db.Column(db.String(500), nullable=False)  # 癌症类型
    annotate_c = db.Column(db.String(5000), nullable=False)  # 变异解读

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'mu_name_usual': self.mu_name_usual,
            'exon': self.exon,
            'gene': self.gene,
            'mu_type': self.mu_type,
            'cancer': self.cancer,
            'annotate_c': self.annotate_c,
        }
        return my_dict

class OkrDrug(db.Model):
    __tablename__ = 'okr_drug'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    drug = db.Column(db.String(500))
    level = db.Column(db.String(500))
    drug_effect = db.Column(db.String(500))
    mutation_id = db.Column(db.Integer(), db.ForeignKey('mutation.id'))

    def to_dict(self):
        my_dict = {
            'id':self.id,
            'drug': self.drug,
            'level': self.level,
            'drug_effect': self.drug_effect
        }
        return my_dict


class AnnotateAuto(db.Model):  # 自动注释库
    __tablename__ = 'annotate_auto'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mu_name_usual = db.Column(db.String(500), nullable=False)  # 临床常用名
    cancer = db.Column(db.String(500), nullable=False)  # 癌症类型
    annotate_c = db.Column(db.String(5000), nullable=False)  # 变异解读
    status = db.Column(db.String(200))  # 结果解释状态

    def to_dict(self):
        my_dict = {
            'id': self.id,
            'mu_name_usual': self.mu_name_usual,
            'cancer': self.cancer,
            'annotate_c': self.annotate_c,
            'status': self.status
        }


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
    grade = db.Column(db.String(200))  #突变等级
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
            'grade': self.grade,
            'evidence_level': self.evidence_level
        }

        return dict_tb
