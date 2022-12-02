
from sqlalchemy import DateTime, func

from app import db


class Permission(db.Model):
    __tablename__ = 'permission'

    id = db.Column(db.Integer, primary_key=True)
    timestamp  = db.Column(DateTime(timezone=True), default=func.now())
    name = db.Column(db.String())
    resource_type = db.Column(db.String())
    component_friendly_name = db.Column(db.String())
    parent_id = db.Column(db.Integer)


    def get_all_permissions():
        return db.session.query(Permission).all()


    def get_permission_by_id(permission_id):
        return db.session.query(Permission).filter(Permission.id==permission_id).one_or_none()
