"""Endpoints for External Orders Items"""

from flask_restful import Resource
from flask import request

from resource_functions import get_collection, get_resource, post_new_resource, post_update_existing_resource

# from activities.create_order import CreateOrder
# from activities.order_update import OrderUpdate
from activities.external_activities.create_external_order import CreateExternalOrder
from activities.external_activities.update_external_order import UpdateExternalOrder
from activities.external_activities.external_order_add_item import ExternalOrderAddItem
from activities.external_activities.external_order_item_update import ExternalOrderItemUpdate
from activities.external_activities.external_order_cancel_item import ExternalOrderCancelItem
from activities.external_activities.external_order_item_map_to_lot_item import ExternalOrderItemMapToLotItem
from activities.external_activities.external_order_item_add_shipment import ExternalOrderItemAddShipment
from class_external_webhooks import firing_webhooks


class ExternalOrderItems(Resource):

    # Read all order_items records

    def get(self, organization_id=1):
        return get_collection(
            current_user=None,
            organization_id=organization_id,
            resource='order_items')

    def post(self, organization_id=1):
        '''
        post: {
            "name":"external_order_add_item",
            "price": 12,
            "sku_id": "84",
            "to_qty": 2,
            "variety": "Candyland",
            "order_id": "41",
            "quantity": 1,
            "sku_name": "candy",
            "include_tax": true,
            "shipment_id": "",
            "to_qty_unit": "dry"
        }
        '''

        data = request.get_json()

        data['created_by'] = 1

        data['organization_id'] = organization_id

        if data['name'] == 'external_order_add_item':
            result = ExternalOrderAddItem.do_activity(data, None)
            firing_webhooks(organization_id=organization_id, event='order_items.created', event_data=data)
            return result


class ExternalOrderItem(Resource):

    # Read single Order_item by id

    def get(self, order_item_id, organization_id=1):
        return get_resource(
            current_user=None,
            resource_id=order_item_id,
            organization_id=organization_id,
            resource='order_items')

    def patch(self, order_item_id, organization_id=1):

        data = request.get_json()

        data['order_item_id'] = order_item_id
        data['created_by'] = 1
        data['organization_id'] = organization_id
        result = {}
        if data['name'] == 'external_order_item_update':
            '''
                {
                    "name":"external_order_item_update",
                    "order_id": "41",
                    "price": 12,
                    "include_tax": true
                }
            '''

            result = ExternalOrderItemUpdate.do_activity(data, None)

        if data['name'] == 'external_order_cancel_item':
            '''
                {
                    "name":"external_order_cancel_item",
                    "order_id": 41,
                    "to_status": "cancelled",
                    "cancelled_by": "xyz",
                    "include_tax": false
                }   
            '''
            result = ExternalOrderCancelItem.do_activity(data, None)

        if data['name'] == 'external_order_item_map_to_lot_item':
            '''
                {
                    "name":"external_order_item_map_to_lot_item",
                    "order_item_id": 106,
                    "inventory_id": 35862
                }   
            '''
            result = ExternalOrderItemMapToLotItem.do_activity(data, None)

        if data['name'] == 'external_order_item_add_shipment':
            '''
                {
                    "name":"external_order_item_add_shipment",
                    "order_item_id": 106,
                    "shipment_id":15,
                    "quantity_filled" : 1
                }   
            '''
            result = ExternalOrderItemAddShipment.do_activity(data, None)

        firing_webhooks(organization_id=organization_id, event='order_items.updated', event_data=data)
        return result
