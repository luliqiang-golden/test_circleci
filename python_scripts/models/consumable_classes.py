'''This module contains database schema model for consumable_classes table'''
from sqlalchemy.dialects.postgresql.json import JSONB
from app import db
from sqlalchemy import DateTime, func


class ConsumableClasses(db.Model):
    
    '''Definition of consumable_classes table'''
    __tablename__ = 'consumable_classes'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    type = db.Column(db.String)
    subtype = db.Column(db.String)
    unit = db.Column(db.String)
    data = db.Column(JSONB)
    status = db.Column(db.String)
    
    
    def get_consumable_class_by_type_and_subtype(type, subtype, organization_id):
        res = db.session.query(ConsumableClasses).filter(ConsumableClasses.type==type, 
                                                         ConsumableClasses.subtype==subtype,
                                                         ConsumableClasses.organization_id==organization_id).first()
        return res