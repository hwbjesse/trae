from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import hashlib

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, pwd):
        self.password = hashlib.sha256(pwd.encode()).hexdigest()

    def check_password(self, pwd):
        return self.password == hashlib.sha256(pwd.encode()).hexdigest()


class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='客户姓名')
    wechat = db.Column(db.String(100), comment='微信号')
    phone = db.Column(db.String(20), comment='手机号')
    project_name = db.Column(db.String(200), comment='参加的项目名')
    contract_no = db.Column(db.String(100), comment='协议编号')
    payment_status = db.Column(db.String(50), comment='付费情况')
    payment_amount = db.Column(db.Float, default=0, comment='付费金额')
    city = db.Column(db.String(100), comment='客户所在城市')
    team_size = db.Column(db.String(50), comment='团队规模')
    project_share = db.Column(db.String(100), comment='项目分成')
    project_fee = db.Column(db.String(100), comment='项目收费')
    docking_sort = db.Column(db.String(50), comment='对接排序')
    join_date = db.Column(db.Date, comment='参加项目时间')
    remark = db.Column(db.Text, comment='客户备注')
    created_at = db.Column(db.Date, default=datetime.now)
    updated_at = db.Column(db.Date, default=datetime.now, onupdate=datetime.now)

    def to_dict(self):
        date_format = '%Y-%m-%d'
        return {
            'id': self.id,
            'name': self.name or '',
            'wechat': self.wechat or '',
            'phone': self.phone or '',
            'project_name': self.project_name or '',
            'contract_no': self.contract_no or '',
            'payment_status': self.payment_status or '',
            'payment_amount': self.payment_amount or 0,
            'city': self.city or '',
            'team_size': self.team_size or '',
            'project_share': self.project_share or '',
            'project_fee': self.project_fee or '',
            'created_at': self.created_at.strftime(date_format) if self.created_at else '',
            'updated_at': self.updated_at.strftime(date_format) if self.updated_at else ''
        }