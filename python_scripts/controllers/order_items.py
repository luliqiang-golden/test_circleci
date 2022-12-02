'''This resource module controls API related to order items'''
from flask import request, Blueprint, jsonify
from flask.helpers import make_response
from auth0_authentication import requires_auth
from models.shipments import Shipments
from models.order_item import OrderItem
from controllers import BaseController
from serializer.order_item import FillOrderItemSchema
from models.skus import Skus
from models.webhook import Webhook

fill_order_item_schema = FillOrderItemSchema()

class OrderItemsFillResource(BaseController):

    
    @requires_auth
    def post(self, current_user, organization_id, order_item_id):
        '''Creates handles order item requests'''
        
        params = self.serialize(fill_order_item_schema, request.get_json())
        created_by = params.get('created_by')
        lots = params.get('lots')
        sku_id = params.get('sku_id')
        shipment_id = params.get('shipment_id')


        if(not OrderItem.validate_request_total_quantity(order_item_id, lots)):
            return make_response(jsonify({"message": "Error while inserting data - Total quantity requested is different from order item quantity"}), 400)


        if(not params.get('shipment_id')):
            shipment_id = Shipments.create_shipment_from_order_item_id(organization_id, order_item_id, created_by)
        else:
            shipment_id = params.get('shipment_id')

        quantity_filled = OrderItem.fill_order_item(organization_id, order_item_id, sku_id, lots, created_by)
        OrderItem.add_order_item_shipment(organization_id, created_by, order_item_id, shipment_id, quantity_filled)
        sku_details = Skus.get_sku_detail_for_webhook(sku_id)
        Webhook().firing_webhooks(event='skus.updated', event_data=sku_details)
        return make_response(jsonify({'shipment_id': shipment_id,
                        'quantity_filled': quantity_filled}), 201)

# Make blueprint for order items API
order_items_bp = Blueprint('order_item', __name__)

# Define url_patterns related to order items API here
order_items_fill = OrderItemsFillResource.as_view('order_items_fill')
order_items_bp.add_url_rule('/order-items/<int:order_item_id>/fill', view_func=order_items_fill, methods=['POST'])

