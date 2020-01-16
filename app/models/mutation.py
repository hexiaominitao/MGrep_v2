from app.models import db


class Mutation(db.Model):
    __tablename__ = 'mutation'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mg_id = db.Column(db.String(50), nullable=False)  # 迈景编号
    req_mg = db.Column(db.String(50), nullable=False)  # 申请单号
    gene = db.Column(db.String(200), nullable=False)  # 基因名称
    mu_type = db.Column(db.String(50), nullable=False)  # 检测的突变类型
    mu_name = db.Column(db.String(200), nullable=False)  # 变异全称
    mu_af = db.Column(db.String(50), nullable=False)  # 突变频率
    mu_name_usual = db.Column(db.String(200), nullable=False)  # 临床突变常用名称
    reads = db.Column(db.String(50), nullable=False)  # 支持序列数
    maf = db.Column(db.String(50), nullable=True)  # maf
    exon = db.Column(db.String(50), nullable=True)  # 外显子
    fu_type = db.Column(db.String(50), nullable=False)  # 功能影响
    locus = db.Column(db.String(200), nullable=False)
    grade = db.Column(db.String(200), nullable=True)  # 临床意义级别
    report_id = db.Column(db.Integer(), db.ForeignKey('report.id'))
    explanations = db.Column(db.String(2000), nullable=True)
    status = db.Column(db.String(50), nullable=False)  # 状态

    def to_dict(self):
        return {
            'id': self.id,
            'mg_id': self.mg_id,
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
            'explanations': self.explanations
        }
