'''This module contains database schema model for orders table'''

from sqlalchemy.dialects.postgresql.json import JSONB
from app import db
from sqlalchemy import DateTime, func

class Orders(db.Model):
    
    '''Definition of orders table'''
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    crm_account_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    description = db.Column(db.String)
    order_type = db.Column(db.String)
    order_received_date = db.Column(db.String)
    order_placed_by = db.Column(db.String)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    data = db.Column(JSONB)
    shipping_address = db.Column(JSONB)
    ordered_stats = db.Column(JSONB)
    shipped_stats = db.Column(JSONB)
    status = db.Column(db.String)
    shipping_status = db.Column(db.String)
    due_date = db.Column(db.String)
    sub_total = db.Column(db.Numeric(14,2))
    provincial_tax = db.Column(db.Numeric(14,2))
    excise_tax = db.Column(db.Numeric(14,2))
    discount_percent = db.Column(db.Numeric(14,2))
    discount = db.Column(db.Numeric(14,2))
    shipping_value = db.Column(db.Numeric(14,2))
    total = db.Column(db.Numeric(14,2))
    include_tax = db.Column(db.Boolean)
    
    