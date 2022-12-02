'''This module contains database schema model for consumable_lots table'''
from sqlalchemy.dialects.postgresql.json import JSONB
from app import db
from sqlalchemy import DateTime, func

from models.activity import Activity
from models.consumable_classes import ConsumableClasses
from models.transaction_allocations import TransactionAllocations
from models.transactions import Transactions

class ConsumableLots(db.Model):
    
    '''Definition of consumable_lots table'''
    __tablename__ = 'consumable_lots'
    
    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer)
    created_by = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    status = db.Column(db.String)
    expiration_date = db.Column(DateTime(timezone=True))
    class_id = db.Column(db.String)
    current_qty = db.Column(db.Integer)
    initial_qty = db.Column(db.Integer)
    unit = db.Column(db.String)
    data = db.Column(JSONB)
    vendor_lot_number = db.Column(db.String)
    
    
    def receive_consumable_lot(data, organization_id):
        
        transaction = Transactions.find_transaction_by_po(data['po'], organization_id)
        class_id = ConsumableClasses.get_consumable_class_by_type_and_subtype(data['supply_type'], data['subtype'], organization_id).id
        
        consumable_lot = ConsumableLots.receive_consumable_lot_activity(organization_id, data['created_by'], data['expiration_date'], class_id, data['initial_qty'], data['initial_qty'], 
                                              data['unit'], data['vendor_lot_number'], data['po'], data['upload_id'], data['vendor_id'], data['checked_by'],
                                              data['approved_by'], data['vendor_name'], data['intended_use'], data['damage_details'], data['amount'], data['delivery_details'],
                                              data['damage_to_shipment'], data['delivery_matches_po'])
        
        if(not transaction):
            transaction = Transactions.create_transaction(organization_id, data['created_by'], data['vendor_id'], 
                                                        data['delivery_details'], data['po'], data['amount'])
        else:
            transaction = Transactions.update_transaction_total_amount(organization_id, data['created_by'], transaction.id, data['amount'])
            
        TransactionAllocations.create_transaction_allocations(organization_id, data['created_by'], 'debit', transaction.id, 
                                                              data['amount'], consumable_lot.id, data['damage_details'])

        return consumable_lot

    def receive_consumable_lot_activity(organization_id, created_by, expiration_date, class_id, current_qty, initial_qty, unit, vendor_lot_number,
                               po, upload_id, vendor_id, checked_by, approved_by, vendor_name, intended_use, damage_details,
                               amount, delivery_details, damage_to_shipment, delivery_matches_po):
        
        consumableLot = ConsumableLots(
                organization_id = organization_id,
                created_by = created_by,
                status = 'awaiting_approval',
                expiration_date = expiration_date,
                class_id = class_id,
                current_qty = current_qty,
                initial_qty = initial_qty,
                unit = unit,
                data = {},
                vendor_lot_number = vendor_lot_number
            )

        db.session.add(consumableLot)
        db.session.commit()
        
        data = {'po': po, 
                'unit': unit, 
                'amount': amount, 
                'upload_id': upload_id, 
                'vendor_id': vendor_id, 
                'checked_by': checked_by, 
                'approved_by': approved_by, 
                'initial_qty': initial_qty, 
                'vendor_name': vendor_name, 
                'vendor_lot_number': vendor_lot_number,
                'intended_use': intended_use, 
                'damage_details': damage_details, 
                'expiration_date': expiration_date, 
                'delivery_details': delivery_details, 
                'consumable_lot_id': consumableLot.id, 
                'damage_to_shipment': damage_to_shipment, 
                'consumable_class_id': class_id, 
                'delivery_matches_po': delivery_matches_po}
        
        Activity.save_activities(organization_id, data, created_by, 'receive_consumable_lot')
        
        return consumableLot
    
    def add_consumable_lot_activity_log(organization_id, created_by, details, description, consumable_lot_id, upload_id):
        
        data = {
                'detail': details, 
                'upload_id': upload_id, 
                'description': description,
                'consumable_lot_id': consumable_lot_id}
        
        activity = Activity.save_activities(organization_id, data, created_by, 'create_consumable_lot_activity_log')
        
        return activity