from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import JSONB

from app import db


class Organization(db.Model):
    __tablename__ = 'organizations'
    name = db.Column(db.String())
    id = db.Column(db.Integer, primary_key=True)
    timestamp  = db.Column(DateTime, default=func.now())
    data = db.Column(JSONB)
    
    @property
    def serialize(self):
        return {
            'name' : self.name,
            'id' : self.id,
            'timestamp'  : self.timestamp,
            'data' : self.data
        }
        
