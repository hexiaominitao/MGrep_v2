from app.models import db


class Report(db.Model):
    __tablename__ = 'report'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    mg_id = db.Column(db.String(50), nullable=False)
    req_mg = db.Column(db.String(50), nullable=False)
    rep_item = db.Column(db.String(50), nullable=False)
    okr = db.Column(db.String(50), nullable=False)


