import json
from sqlalchemy import DateTime, func, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from flask import jsonify
from models.activity import Activity
from models.user import User

from app import db


class Signature(db.Model):
    __tablename__ = 'signatures'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    field = db.Column(db.String())
    timestamp  = db.Column(DateTime(timezone=True), default=func.now())
    created_by = db.Column(db.Integer)
    signed_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    activity_id = db.Column(ForeignKey('activities.id'), nullable=False)
    data = db.Column(JSONB)


    def __init__(self, field, timestamp, created_by, signed_by, organization_id, activity_id, data):
        self.field = field
        self.timestamp  = timestamp
        self.created_by = created_by
        self.signed_by = signed_by
        self.organization_id = organization_id
        self.activity_id = activity_id
        self.data = data
        
    @property
    def serialize(self):
       return {
        'id' :  self.id,
        'field' : self.field,
        'timestamp' : self.timestamp,
        'created_by' : self.created_by,
        'signed_by' : self.signed_by,
        'organization_id' : self.organization_id,
        'activity_id' : self.activity_id,
        'data' : self.data 
       }

    def find(id):
        res = db.session.query(Signature).filter(Signature.id==id)
        return jsonify(json_list=[i.serialize for i in res])

    def create_signature(activity_id, organization_id, created_by, field, user_email, parent_id = None, timestamp = None):
        user = User.find_by_email(user_email, organization_id)

        signature = Signature(field=field, 
                                timestamp= timestamp or func.now(), 
                                created_by=created_by, 
                                signed_by=user.id, 
                                organization_id=organization_id, 
                                activity_id=activity_id, 
                                data={})

        db.session.add(signature)
        db.session.flush()

        data = { 
            "field": field,
            "signed_by" : user.id,
            "activity_id" : activity_id,
            "signature_id" : signature.id,
        }
        db.session.commit()
        Activity.save_activities(organization_id, data,created_by, 'create_signature', parent_id, timestamp = timestamp)