'''This resource module controls API related to order items'''
from flask import request, Blueprint, jsonify
from flask.helpers import make_response
from auth0_authentication import requires_auth
from models.shipments import Shipments
from models.order_item import OrderItem
from controllers import BaseController
from serializer.order_item import FillOrderItemSchema
from models.skus import Skus
from models.inventory.lot import Lot
from models.webhook import Webhook

class ExternalOrderItemsFillResource(BaseController):
    
    @requires_auth
    def post(self, current_user, organization_id, external_order_item_id):
        """Handles Fulfill request for an Order Item.

        Args:
            current_user (_type_): _description_
            organization_id (_type_): _description_
            order_item_id (int): Order Item ID

        Returns:
            Json: {shipment_id, quantity_filled}
        """
        
        params = request.get_json()
        created_by = current_user.get('user_id')
        sku_id = params.get('sku_id')
            
        # Getting quantity to be filled
        order_item_id, order_item_quantity = OrderItem.get_order_item_quantity_to_be_filled(external_order_item_id)
        
        if order_item_quantity == 0:
            """If no quantity to be filled"""
            return make_response(jsonify({"message": "All quntities already filled."}), 200)
        
        # Getting available lot items
        all_lots = Lot.get_available_lot_items(self, current_user, organization_id, params)
        
        # Selecting lots to fulfill item quantity.
        order_item_quantity, lots = Lot.map_order_item_to_lots(order_item_quantity, all_lots)
        
        if order_item_quantity != 0:
            """If there is not enough lot items to fulfill then return."""
            
            return make_response(jsonify({"message": "Not enough lot items available to fulfill. Please create more lot items."}), 400)
        
        # Creating a new shipment and fulfilling Order Item.
        shipment_id = Shipments.create_shipment_from_order_item_id(organization_id, order_item_id, created_by)

        quantity_filled = OrderItem.fill_order_item(organization_id, order_item_id, sku_id, lots, created_by)
        OrderItem.add_order_item_shipment(organization_id, created_by, order_item_id, shipment_id, quantity_filled)
        sku_details = Skus.get_sku_detail_for_webhook(sku_id)
        Webhook().firing_webhooks(event='skus.updated', event_data=sku_details)
        
        return make_response(jsonify({'shipment_id': shipment_id,
                        'quantity_filled': quantity_filled}), 201)


# Make blueprint for order items API
external_order_items_bp = Blueprint('external_order_item', __name__)

# Define url_patterns related to order items API here
external_order_items_fill = ExternalOrderItemsFillResource.as_view('external_order_items_fill')
external_order_items_bp.add_url_rule('/external_order_items/<int:external_order_item_id>/fill', view_func=external_order_items_fill, methods=['POST'])

