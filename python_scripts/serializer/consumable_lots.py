from marshmallow import Schema, fields
from class_errors import ClientBadRequest
from models.consumable_classes import ConsumableClasses
from models.crm_accounts import CRMAccounts

from models.user import User

class ConsumableLotsSchema(Schema):
    
    upload_id = fields.List(fields.Dict(required=False, allow_none=True), allow_none=True)
    po = fields.Str(required=True)
    vendor_name = fields.Str(required=True)
    vendor_id = fields.Str(required=True)
    vendor_lot_number = fields.Str(allow_none=True)
    initial_qty = fields.Float(required=True)
    expiration_date = fields.Str(allow_none=True)
    intended_use = fields.Str(allow_none=True)
    damage_to_shipment = fields.Bool(required=True)
    delivery_matches_po = fields.Bool(required=True)
    checked_by = fields.Str(required=True)
    approved_by = fields.Str(required=True)
    amount = fields.Float(required=True)
    delivery_details = fields.Str(allow_none=True)
    damage_details = fields.Str(allow_none=True)
    unit = fields.Str(required=True)
    supply_type = fields.Str(required=True)
    subtype = fields.Str(required=True)
    created_by = fields.Int(required=True)
    
    def validate_vendor_name_and_id(self, vendor_id, vendor_name, organization_id):
        if(not CRMAccounts.find_by_name_and_id(vendor_id, vendor_name, organization_id)):
            raise ClientBadRequest({'message': f"Error while inserting data - vendor id: {vendor_id} named: {vendor_name} not found for organization {organization_id}."}, 400)
        
    def validate_checked_by_and_approved_by(self, user_email, organization_id):
        if(not User.find_by_email(user_email, organization_id)):
            raise ClientBadRequest({'message': f"Error while inserting data - {user_email} not found for organization {organization_id}."}, 400)
    
    def validate_supply(self, supply_type, subtype, organization_id):
        consumableLot = ConsumableClasses.get_consumable_class_by_type_and_subtype(supply_type, subtype, organization_id)
        if(not consumableLot):
            raise ClientBadRequest({'message': f"Error while inserting data - {supply_type} - {subtype} not found for organization {organization_id}."}, 400)

class ConsumableLotsResponseSchema(Schema):
    
    id = fields.Int(allow_none=True)
    organization_id = fields.Int(allow_none=True)
    created_by = fields.Int(required=True)
    status = fields.Str(required=True)
    expiration_date = fields.Str(required=True)
    class_id = fields.Int(required=True)
    current_qty = fields.Float(required=True)
    initial_qty = fields.Float(required=True)
    unit = fields.Str(required=True)
    data = fields.Dict(required=True)
    vendor_lot_number = fields.Str(required=True)

class ConsumableLotsActivityLogSchema(Schema):
    description = fields.Str(required=True)
    detail = fields.Str(required=True)
    consumable_lot_id = fields.Int(required=True)
    upload_id = fields.List(fields.Dict(required=False))