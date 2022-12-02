'''This module contains database schema model for taxonomies table'''
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy import DateTime, func
from app import db

class Taxonomies(db.Model):

    '''Definition of taxonomies table'''
    __tablename__ = 'taxonomies'
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    name = db.Column(db.String)
    data = db.Column(JSONB)
