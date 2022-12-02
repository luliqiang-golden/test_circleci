'''This module contains serializer schema used for currency API'''

from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from models.shipments import Shipments
from models.skus import Skus
from models.order_item import OrderItem

class FillOrderItemLotSchema(Schema):
    id = fields.Int(required=True)
    quantity_selected = fields.Int(required=True)

class FillOrderItemSchema(Schema):
    
    def validate_shipment_id(shipment_id):
        if(not Shipments.find_by_id(shipment_id)):
            raise ValidationError("Error while inserting data - shipment_id not found.")

    def validate_sku_id(sku_id):
        if(not Skus.find_by_id(sku_id)):
            raise ValidationError("Error while inserting data - sku_id not found.")
    
    @validates_schema
    def validate_lots_quantity_availability(self, data, **kwargs):
        validate_lots = OrderItem.validate_lots_quantity(data['lots'], data['sku_id'])
        if(not validate_lots[0]):
            raise ValidationError(f"Invalid quantity selected for lot {validate_lots[1]}.")
    
    shipment_id = fields.Int(required=False, validate=validate.And(validate_shipment_id))
    sku_id = fields.Int(required=True, validate=validate.And(validate_sku_id))
    lots = fields.List(fields.Nested(FillOrderItemLotSchema), required=True)
    created_by = fields.Int(required=True)
