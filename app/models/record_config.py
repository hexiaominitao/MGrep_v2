from . import db


class SalesInfo(db.Model):
    __tablename__ = 'sales_info'
    id = db.Column(db.Integer(), primary_key=True)
    code = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(50))
    status = db.Column(db.String(50))
    mail = db.Column(db.String(50))
    region = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    address = db.Column(db.String(50))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'code': self.code,
            'name': self.name, 'status': self.status,
            'mail': self.mail, 'region': self.region, 'phone': self.phone,
            'address': self.address
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class HospitalInfo(db.Model):
    __tablename__ = 'hospital_info'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name, 'label': self.name
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class SampleType(db.Model):
    __tablename__ = 'sample_type'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name, 'label': self.name
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class MethodSample(db.Model):
    __tablename__ = 'method_sample'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class CancerTypes(db.Model):
    __tablename__ = 'cancer_types'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    okr_name = db.Column(db.String(100))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name, 'okr_name': self.okr_name
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class SeqItems(db.Model):
    __tablename__ = 'seq_items'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class Barcode(db.Model):
    __tablename__ = 'barcode'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name,'full_name':self.full_name
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict


class FlowItem(db.Model):
    __tablename__ = 'flow_name'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100))

    def to_dict(self):
        my_dict = {
            'id': self.id, 'name': self.name,'type':self.type
        }
        for k, v in my_dict.items():
            if not v:
                my_dict[k] = ''
        return my_dict
