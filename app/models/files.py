"""
Files model
"""

from app.extensions import db


class Files(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    department_id = db.Column(db.Integer)
    title = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.String(20))
    parent_id = db.Column(db.Integer)
    active = db.Column(db.Integer)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    updated_by = db.Column(db.Integer)

    def __str__(self):
        return self.title


class FilePermissions(db.Model):
    __tablename__ = 'file_permissions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    file_id = db.Column(db.Integer)






