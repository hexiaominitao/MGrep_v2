from . import db


class Mutations(db.Model):
    __tablename__ = 'mutations'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    report_id = db.Column(db.Integer(), db.ForeignKey('report.id'))
    mutation = db.relationship('Mutation', backref='mutation', lazy='dynamic')  # snv/indel
    chemo = db.relationship('Chemotherapy', backref='mutation', lazy='dynamic')  # chemotherapy


class Mutation(db.Model):
    __tablename__ = 'mutation'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    type = db.Column(db.String(200))
    gene = db.Column(db.String(200), nullable=False)  # 基因名称
    transcript = db.Column(db.String(200))  # 转录本
    exon = db.Column(db.String(50))  # 外显子
    cHGVS = db.Column(db.String(200))  # 编码改变
    pHGVS_3 = db.Column(db.String(200))  # 氨基酸改变
    pHGVS_1 = db.Column(db.String(200))  # 氨基酸改变-简写
    chr_start_end = db.Column(db.String(500))  # 基因座
    function_types = db.Column(db.String(200))  # 功能影响
    ID_v = db.Column(db.String(200))  # id
    hotspot = db.Column(db.String(200))  # 是否hotspot
    mu_af = db.Column(db.String(50))  # 丰度
    depth = db.Column(db.String(200))  # 深度
    okr_mu = db.Column(db.String(200)) # OKR注释类型
    mu_type =db.Column(db.String(200)) # 报告类型
    maf = db.Column(db.String(50), nullable=True)  # maf
    grade = db.Column(db.String(200), nullable=True)  # 临床意义级别
    status = db.Column(db.String(200))  # 状态
    mutation_id = db.Column(db.Integer(), db.ForeignKey('mutations.id'))
    drug = db.relationship('OkrDrug', backref='mutation', lazy='dynamic')

    def to_dict(self):
        my_dict =  {
            'id': self.id,
            'type': self.type,
            'gene': self.gene,
            'transcript': self.transcript,
            'exon': self.exon,
            'cHGVS': self.cHGVS,
            'pHGVS_3': self.pHGVS_3,
            'pHGVS_1': self.pHGVS_1,
            'chr_start_end': self.chr_start_end,
            'function_types': self.function_types,
            'ID_v': self.ID_v,
            'hotspot': self.hotspot,
            'mu_af': self.mu_af,
            'grade': self.grade,
            'depth': self.depth,
            'okr_mu':self.okr_mu,
            'mu_type': self.mu_type,
            'maf': self.maf,
            'status': self.status
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class Chemotherapy(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    gene = db.Column(db.String(200), nullable=False)  # 基因
    pos = db.Column(db.String(50), nullable=False)  # 检测位点
    chr = db.Column(db.String(50), nullable=False)  # 参考基因组位置
    ref = db.Column(db.String(50), nullable=False)  # 参考基因型
    alt = db.Column(db.String(50), nullable=False)  # 检测基因型
    mu = db.Column(db.String(50), nullable=False)  # 是否突变
    mutation_id = db.Column(db.Integer(), db.ForeignKey('mutations.id'))
