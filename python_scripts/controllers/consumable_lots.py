'''This resource module controls API related to lot_items'''

from flask import Blueprint, request, jsonify
from flask.helpers import make_response
from auth0_authentication import requires_auth
from models.consumable_lots import ConsumableLots
from serializer.consumable_lots import ConsumableLotsSchema, ConsumableLotsResponseSchema, ConsumableLotsActivityLogSchema
from controllers import BaseController

consumable_lots_schema = ConsumableLotsSchema()
consumable_lots_response_schema = ConsumableLotsResponseSchema()
consumable_lots_activity_log_schema = ConsumableLotsActivityLogSchema()

class ConsumableLotsCollection(BaseController):

    @requires_auth
    def post(self, current_user, organization_id):
        
        data = self.serialize(consumable_lots_schema, request.get_json())
        
        ConsumableLotsSchema().validate_checked_by_and_approved_by(data['approved_by'], organization_id)
        ConsumableLotsSchema().validate_checked_by_and_approved_by(data['checked_by'], organization_id)
        ConsumableLotsSchema().validate_vendor_name_and_id(data['vendor_id'], data['vendor_name'], organization_id)
        ConsumableLotsSchema().validate_supply(data['supply_type'], data['subtype'], organization_id)

        consumable_lots = ConsumableLots.receive_consumable_lot(data, organization_id)

        response = self.deserialize_object(consumable_lots_response_schema, consumable_lots)
        
        return make_response(jsonify(response), 200)

class ConsumableLotsActivityLog(BaseController):
    
    @requires_auth
    def post(self, current_user, organization_id):
        
        data = self.serialize(consumable_lots_activity_log_schema, request.get_json())
        
        response = ConsumableLots.add_consumable_lot_activity_log(organization_id, int(current_user['user_id']), data['detail'], data['description'], data['consumable_lot_id'], data.get('upload_id'))
        
        return make_response(jsonify(response.serialize), 200)
    

# Make blueprint for lot_items API
consumable_lots_bp = Blueprint('consumable_lots', __name__)

# Define url_patterns related to lot_items API here
consumable_lots = ConsumableLotsCollection.as_view('consumable_lots')
consumable_lots_bp.add_url_rule('/consumable_lots', view_func=consumable_lots, methods=['POST'])

consumable_lots_log = ConsumableLotsActivityLog.as_view('consumable_lots_log')
consumable_lots_bp.add_url_rule('consumable_lots/log', view_func=consumable_lots_log, methods=['POST'])
