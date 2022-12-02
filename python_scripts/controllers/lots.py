'''This resource module controls API related to lots'''

from flask import Blueprint, request
from flask.helpers import make_response
from flask.json import jsonify
from class_errors import ClientBadRequest
from auth0_authentication import requires_auth
from serializer.skus import SkusSchema
from serializer.inventory import InventorySchema
from models.inventory.lot import Lot
from controllers import BaseController
from serializer.lot import LotSchema, TransferLotSchema

lot_item_schema = InventorySchema()
lot_schema = InventorySchema()
skus_schema = SkusSchema()
create_lot_schema = LotSchema()
transfer_lot_schema = TransferLotSchema()

class LotsCollection(BaseController):

    @requires_auth
    def get(self, current_user, organization_id):

        '''Returns list of all the lots present in table'''

        queryparams = request.args
        
        queryset = Lot.get_available_lot_items(self, current_user, organization_id, queryparams)

        response = []

        for data in queryset:
            entity_response = {
            'lot_id': data.lot_id,
            'lot_name':  data.lot_name,
            'sku_id':  data.sku_id,
            'sku_name': data.sku_name,
            'timestamp': data.lot_timestamp,
            'items_available': data.count,
            }
            response.append(entity_response)

        return make_response(jsonify(response), 200)

    @requires_auth
    def post(self, current_user, organization_id):
        '''
        Transfer_recieved_inventory
        request body params example:
            {
                "name":"create_lot",
                "scale_name":"office",
                "lot_name":"czxczcz",
                "to_room":"Propagation Room",
                "variety":"213",
                "variety_id":444,
                "from_qty":10,
                "from_qty_unit":"dry",
                "to_qty":10,
                "to_qty_unit":"dry",
                "from_inventory_id":1234,
                "inventory_type:"received_inventory"
            }
        '''
        params = self.serialize(create_lot_schema, request.get_json())
        if params.get("inventory_type") in ['received_inventory', 'received-inventory', 'received inventory', 'batch']:
            return jsonify(Lot().transfer_inventory_to_lot(
                current_user.get("user_id"),
                organization_id,
                params, 
                params.get("from_inventory_id")
            ))
        else:
            raise ClientBadRequest({
                        "code": "bad_request",
                        "description": f"Can not create lot out of '{params.get('inventory_type')}' type of inventory"
                    }, 400)    


class TransferLotCollection(BaseController):

    @requires_auth
    def post(self, current_user, organization_id):
        '''
        Transfer_production_to_existing_lot
        request body params example:
            {
                "name":"transfer_inventory",
                "scale_name":"scale",
                "variety":"213",
                "variety_id":444,
                "from_qty":10,
                "from_qty_unit":"dry",
                "to_qty":10,
                "to_qty_unit":"dry",
                "from_inventory_id":1234,
                "to_inventory_id": 4321,
                "inventory_type": "received_inventory"
            }
        '''
        params = self.serialize(transfer_lot_schema, request.get_json())

        if params.get("inventory_type") in ['received_inventory', 'received-inventory', 'received inventory', 'batch']:
            return jsonify(Lot().transfer_production_to_existing_lot(
                current_user.get("user_id"),
                organization_id,
                params, 
                params.get("from_inventory_id")
            ))
        else:
            raise ClientBadRequest({
                    "code": "bad_request",
                    "description": f"Cannot transfer lot out of '{params.get('inventory_type')}' type of inventory"
                }, 400)


# Make blueprint for lots API
lots_bp = Blueprint('lots', __name__)

# Define url_patterns related to lots API here
lots = LotsCollection.as_view('lots')
lots_bp.add_url_rule('/lots', view_func=lots, methods=['GET', 'POST'])

transfer_lot = TransferLotCollection.as_view('transfer_lot')
lots_bp.add_url_rule('/lots/transfer-lot', view_func=transfer_lot, methods=['POST'])
