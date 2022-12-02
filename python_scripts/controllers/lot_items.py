'''This resource module controls API related to lot_items'''

from flask import Blueprint, request
from flask.json import jsonify
from auth0_authentication import requires_auth
from models.inventory.lot_item import LotItem
from serializer.lot_item import LotItemSchema
from class_errors import ClientBadRequest
from controllers import BaseController

lot_item_schema = LotItemSchema()

class LotItemCollection(BaseController):

    @requires_auth
    def post(self, current_user, organization_id, lot_id):
        '''
        Create lot item request body example:
        {
            "name":"create_lot_item",
            "variety":"Variety name",
            "approved_by":"current@wilcompute.com",
            "sku_id":1,
            "sku_name":"213 1g", 
            "unit":"dry", 
            "lot_item_quantity":3, 
            "to_room":"propagation"
        }
        '''
        params = self.serialize(lot_item_schema, request.get_json())
        return jsonify(LotItem().transfer_lot_to_lot_items(
            current_user.get('user_id'),
            organization_id,
            params,
            lot_id
        ))

# Make blueprint for lot_items API
lot_item_bp = Blueprint('lot_items', __name__)

# Define url_patterns related to lot_items API here
lot_items = LotItemCollection.as_view('lot_items')
lot_item_bp.add_url_rule('/lots/<int:lot_id>/lot-items', view_func=lot_items, methods=['POST'])
