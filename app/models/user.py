"""
Users model
"""

from app.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    name = db.Column(db.String(32))
    is_admin = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=False)
    authenticated = db.Column(db.Boolean, default=False)

    def get_id(self):
        return self.id

    def is_active(self):
        return self.active

    def is_authenticated(self):
        return self.authenticated

    def admin(self):
        return self.is_admin


class UserDepartment(db.Model):
    __tablename__ = 'user_department'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    department_id = db.Column(db.Integer)

