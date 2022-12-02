'''This resource module controls API related to destruction inventory'''
from dataclasses import dataclass
from serializer.destruction_inventory import DequeueSchemaPostRequest, DequeueSchemaPostResponse
from models.inventory.destruction_inventory import DestructionInventory
from auth0_authentication import requires_auth
from flask.helpers import make_response
from controllers import BaseController
from flask import Blueprint, request
from flask.json import jsonify

dequeue_schema_post_response = DequeueSchemaPostResponse()
dequeue_schema_post_request = DequeueSchemaPostRequest()

class DestructionInventoryCollection(BaseController):
    
    @requires_auth
    def post(self, current_user, organization_id):
        
        response = []
        
        data = self.serialize(dequeue_schema_post_request, request.get_json())
        
        for inventory_id in data.get('destruction_inventories'):
        
            destructionInventory = DestructionInventory(organization_id, current_user.get('user_id'), inventory_id)
            
            result = destructionInventory.dequeue_destruction_inventory(data)

            response.append(self.deserialize_object(dequeue_schema_post_response, result))
        
        return make_response(jsonify(response), 200)


# Make blueprint for role API
destruction_inventory_bp = Blueprint('destruction_inventory', __name__)

# Define url_patterns related to role API here
destruction_inventory = DestructionInventoryCollection.as_view('destruction_inventory')
destruction_inventory_bp.add_url_rule('/destruction_inventory/dequeue', view_func=destruction_inventory, methods=['POST'])
