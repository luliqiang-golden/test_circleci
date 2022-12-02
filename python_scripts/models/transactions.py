'''This module contains database schema model for transactions table'''
from decimal import Decimal
from sqlalchemy.dialects.postgresql.json import JSONB
from app import db
from sqlalchemy import DateTime, func

from models.activity import Activity

class Transactions(db.Model):
    
    '''Definition of transactions table'''
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    description = db.Column(db.String)
    total_amount = db.Column(db.Numeric(14,2))
    data = db.Column(JSONB)
    crm_account_id = db.Column(db.Integer)
    purchase_order = db.Column(db.String)


    def find_transaction_by_po(po, organization_id):
        res = db.session.query(Transactions).filter(Transactions.purchase_order==po, Transactions.organization_id==organization_id).first()
        return res
    
    def create_transaction(organization_id, created_by, crm_account_id, description, po, total_amount):
        
        transaction = Transactions(
                organization_id = organization_id,
                created_by = created_by,
                description = description,
                total_amount = total_amount,
                crm_account_id = crm_account_id,
                purchase_order = po
                )

        db.session.add(transaction)
        db.session.commit()
        
        data = {
            'total_amount': total_amount,
            'crm_account_id': crm_account_id,
            'description': description,
            'purchase_order': po,
            'transaction_id': transaction.id
        }
         
        Activity.save_activities(organization_id, data, created_by, 'record_transaction')
        
        return transaction
        
    def update_transaction_total_amount(organization_id, created_by, transaction_id, amount):
        
        transaction_update = (Transactions.query
                .filter(Transactions.id == transaction_id).with_for_update().one())
        
        transaction_update.total_amount = transaction_update.total_amount + Decimal(amount)
        
        db.session.add(transaction_update)
        db.session.commit()
        
        data = {
            'transaction_id': transaction_id,
            'amount': amount
        }
         
        Activity.save_activities(organization_id, data, created_by, 'update_transaction_total_amount')
        
        return transaction_update