'''This module contains database schema model for crm_accounts table'''
from sqlalchemy.dialects.postgresql.json import JSONB
from app import db
from sqlalchemy import DateTime, func

class CRMAccounts(db.Model):
    
    '''Definition of crm_accounts table'''
    __tablename__ = 'crm_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    created_by = db.Column(db.Integer)
    data = db.Column(JSONB)
    name = db.Column(db.String)
    organization_id = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    attributes = db.Column(JSONB)
    account_type = db.Column(db.String)
    
    def find_by_name_and_id(id, name, organization_id):
        return db.session.query(CRMAccounts).filter(CRMAccounts.id==id, CRMAccounts.name==name, CRMAccounts.organization_id==organization_id).first()