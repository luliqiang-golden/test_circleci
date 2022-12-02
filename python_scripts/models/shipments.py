'''This module contains database schema model for order items table'''
from sqlalchemy.dialects.postgresql.json import JSONB
from app import db
from models.order_item import OrderItem
from sqlalchemy import DateTime, func
from models.activity import Activity
from models.orders import Orders

class Shipments(db.Model):
    
    '''Definition of shipments table'''
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String)
    shipped_date = db.Column(DateTime(timezone=True), default=None)
    delivered_date = db.Column(DateTime(timezone=True), default=None)
    created_by = db.Column(db.Integer)
    organization_id = db.Column(db.Integer)
    timestamp = db.Column(DateTime(timezone=True), default=func.now())
    shipping_address = db.Column(JSONB)
    crm_account_id = db.Column(db.Integer)
    status = db.Column(db.String)
    data = db.Column(JSONB)
    attributes = db.Column(JSONB)
    
    def find_by_id(shipment_id):
        return (Shipments.query
                        .filter(Shipments.id == shipment_id).first())

    def create_shipment_from_order_item_id(organization_id, order_item_id, created_by):
 
            order_item = (OrderItem.query
                        .filter(OrderItem.id == order_item_id).first())

            order_details = (Orders.query
                    .filter(order_item.order_id == Orders.id)
                    .first())


            shipments = Shipments(
                created_by = created_by,
                organization_id = organization_id,
                shipping_address = order_details.shipping_address,
                crm_account_id = order_details.crm_account_id,
                status = 'pending')

            db.session.add(shipments)
            db.session.commit()

            data_create_shipment = {
                "shipment_id": shipments.id,
                "crm_account_id" : order_details.crm_account_id,
                "shipping_address" : order_details.shipping_address
            }
            
            data_shipment_update_shipping_address = {
                "shipment_id": shipments.id,
                "shipping_address" : order_details.shipping_address
            }
            
            Activity.save_activities(organization_id, data_create_shipment, created_by, 'create_shipment')
            Activity.save_activities(organization_id, data_shipment_update_shipping_address, created_by, 'shipment_update_shipping_address')

            return shipments.id


