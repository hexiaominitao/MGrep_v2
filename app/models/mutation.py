from . import db


class Mutation(db.Model):
    __tablename__ = 'mutation'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    report_id = db.Column(db.Integer(), db.ForeignKey('report.id'))
    snv = db.relationship('SNV_INDEL', backref='mutation', lazy='dynamic')  # snv/indel
    fusion = db.relationship('Fusion', backref='mutation', lazy='dynamic')  # fusion
    cnv = db.relationship('CNV', backref='mutation', lazy='dynamic')  # cnv
    chemo = db.relationship('Chemotherapy', backref='mutation', lazy='dynamic')  # chemotherapy


class SNV_INDEL(db.Model):
    __tablename__ = 'snv_indel'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    type = db.Column(db.String(200))
    gene = db.Column(db.String(200), nullable=False)  # 基因名称
    mu_type = db.Column(db.String(50), nullable=False)  # 检测的突变类型
    mu_name = db.Column(db.String(200), nullable=False)  # 变异全称
    mu_af = db.Column(db.String(50), nullable=False)  # 丰度
    mu_name_usual = db.Column(db.String(200), nullable=False)  # 临床突变常用名称
    reads = db.Column(db.String(50), nullable=False)  # 支持序列数
    maf = db.Column(db.String(50), nullable=True)  # maf
    exon = db.Column(db.String(50), nullable=False)  # 外显子
    fu_type = db.Column(db.String(50), nullable=False)  # 功能影响
    locus = db.Column(db.String(200), nullable=False)  # 位置
    grade = db.Column(db.String(200), nullable=True)  # 临床意义级别
    explanations = db.Column(db.String(2000), nullable=True)  # 结果注释
    status = db.Column(db.String(200))  # 状态
    mutation_id = db.Column(db.Integer(), db.ForeignKey('mutation.id'))
    okr_c_id = db.Column(db.Integer(), db.ForeignKey('okr.id'))
    okr_c = db.relationship('OKR')  # okr
    annotate_id = db.Column(db.Integer(), db.ForeignKey('annotate.id'))  # 注释id
    annotate = db.relationship('Annotate')  # 注释

    def to_dict(self):
        return {
            'id': self.id,
            'gene': self.gene,
            'mu_type': self.mu_type,
            'mu_name': self.mu_name,
            'mu_af': self.mu_af,
            'mu_name_usual': self.mu_name_usual,
            'reads': self.reads,
            'maf': self.maf,
            'exon': self.exon,
            'fu_type': self.fu_type,
            'locus': self.locus,
            'grade': self.grade,
            'status': self.status,
            'type': self.type
        }


class Fusion(db.Model):
    __tablename__ = 'fusion'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    type = db.Column(db.String(200))
    gene = db.Column(db.String(200), nullable=False)  # 基因
    mu_type = db.Column(db.String(50), nullable=False)  # 检测的突变类型
    mu_name = db.Column(db.String(200), nullable=False)  # 变异全称
    mu_af = db.Column(db.String(50), nullable=False)  # 丰度
    mu_name_usual = db.Column(db.String(200), nullable=False)  # 临床突变常用名称
    grade = db.Column(db.String(200), nullable=True)  # 临床意义级别
    status = db.Column(db.String(200))  # 状态
    mutation_id = db.Column(db.Integer(), db.ForeignKey('mutation.id'))
    okr_c_id = db.Column(db.Integer(), db.ForeignKey('okr.id'))
    okr_c = db.relationship('OKR')  # okr
    annotate_id = db.Column(db.Integer(), db.ForeignKey('annotate.id'))  # 注释id
    annotate = db.relationship('Annotate')  # 注释

    def to_dict(self):
        return {
            'id': self.id,
            'gene': self.gene,
            'mu_type': self.mu_type,
            'mu_name': self.mu_name,
            'mu_af': self.mu_af,
            'mu_name_usual': self.mu_name_usual,
            'grade': self.grade,
            'status': self.status,
            'type': self.type
        }


class CNV(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    type = db.Column(db.String(200))
    gene = db.Column(db.String(200), nullable=False)  # 基因
    mu_type = db.Column(db.String(50), nullable=False)  # 检测的突变类型
    mu_name = db.Column(db.String(200), nullable=False)  # 变异全称
    mu_af = db.Column(db.String(50), nullable=False)  # 丰度
    mu_name_usual = db.Column(db.String(200), nullable=False)  # 临床突变常用名称
    grade = db.Column(db.String(200), nullable=True)  # 临床意义级别
    status = db.Column(db.String(200))  # 状态
    mutation_id = db.Column(db.Integer(), db.ForeignKey('mutation.id'))
    okr_c_id = db.Column(db.Integer(), db.ForeignKey('okr.id'))
    okr_c = db.relationship('OKR')  # okr
    annotate_id = db.Column(db.Integer(), db.ForeignKey('annotate.id'))  # 注释id
    annotate = db.relationship('Annotate')  # 注释

    def to_dict(self):
        return {
            'id': self.id,
            'gene': self.gene,
            'mu_type': self.mu_type,
            'mu_name': self.mu_name,
            'mu_af': self.mu_af,
            'mu_name_usual': self.mu_name_usual,
            'grade': self.grade,
            'status': self.status,
            'type': self.type
        }


class Chemotherapy(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    gene = db.Column(db.String(200), nullable=False)  # 基因
    pos = db.Column(db.String(50), nullable=False)  # 检测位点
    chr = db.Column(db.String(50), nullable=False)  # 参考基因组位置
    ref = db.Column(db.String(50), nullable=False)  # 参考基因型
    alt = db.Column(db.String(50), nullable=False)  # 检测基因型
    mu = db.Column(db.String(50), nullable=False)  # 是否突变
    mutation_id = db.Column(db.Integer(), db.ForeignKey('mutation.id'))
