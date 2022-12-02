'''This module contains database schema model for transaction_allocations table'''
from sqlalchemy.dialects.postgresql.json import JSONB
from app import db
from sqlalchemy import DateTime, func

from models.activity import Activity

class TransactionAllocations(db.Model):
    
    '''Definition of transaction_allocations table'''
    __tablename__ = 'transaction_allocations'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    amount = db.Column(db.Numeric(14,2))
    transaction_id = db.Column(db.Integer)
    data = db.Column(JSONB)
    description = db.Column(db.String)
    type = db.Column(db.String)
    
    
    def create_transaction_allocations(organization_id, created_by, type, transaction_id, amount, consumable_lot_id, description):
        
        transactionAllocations = TransactionAllocations(
                organization_id = organization_id,
                created_by = created_by,
                amount = amount,
                transaction_id = transaction_id,
                data = {'consumable_lot_id': consumable_lot_id},
                description = description,
                type = type
                )

        db.session.add(transactionAllocations)
        db.session.commit()
        
        data = {
            'type': type,
            'transaction_id': transaction_id,
            'amount': amount,
            'consumable_lot_id': consumable_lot_id,
            'description': description,
            'transaction_allocation_id': transactionAllocations.id
        }
         
        Activity.save_activities(organization_id, data, created_by, 'record_transaction_allocation')
        
        return transactionAllocations