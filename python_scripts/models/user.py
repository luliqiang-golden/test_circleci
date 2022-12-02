
from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from flask import jsonify

from app import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    organization_id = db.Column(db.Integer)
    auth0_id = db.Column(db.String())
    enabled = db.Column(db.Boolean)
    created_by = db.Column(db.Integer)
    timestamp  = db.Column(DateTime(timezone=True), default=func.now())
    data = db.Column(JSONB)
    email = db.Column(db.String())
    job_title =  db.Column(db.String())

    @property
    def serialize(self):
       return {
        'id' : self.id,
        'name' : self.name,
        'organization_id' : self.organization_id,
        'auth0_id' : self.auth0_id,
        'enabled' : self.enabled,
        'created_by' : self.created_by,
        'timestamp'  : self.timestamp,
        'data' : self.data,
        'email' : self.email,
        'job_title' : self.job_title
       }

    def find_by_email(email, organization_id):
        return db.session.query(User).filter(User.email==email, User.organization_id==organization_id).first()
