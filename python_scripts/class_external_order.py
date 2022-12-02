"""Endpoints for External Orders"""

from flask_restful import Resource
from flask import request

from resource_functions import get_collection, get_resource, post_new_resource, post_update_existing_resource

from activities.external_activities.create_external_order import CreateExternalOrder
from activities.external_activities.update_external_order import UpdateExternalOrder
from activities.external_activities.external_order_update_status import ExternalOrderUpdateStatus
from activities.external_activities.external_order_update_account import ExternalOrderUpdateAccount
from activities.external_activities.external_order_payment_status import ExternalOrderPaymentStatus
from activities.external_activities.external_order_attach_document import ExternalOrderAttachDocument
from activities.external_activities.external_order_create_note import ExternalOrderCreateNote
from class_external_webhooks import firing_webhooks


class ExternalOrders(Resource):

    # Read all order records
    def get(self, organization_id=1):
        return get_collection(
            current_user=None,
            organization_id=organization_id,
            resource='orders')

    # Create New external order
    def post(self, organization_id=1):
        print("inside the external orders")
        """
        Add new external order record
        POST:{
            "name":"create_external_order",
            "crm_account_id": 254,
            "crm_account_name": "Test CRM 2",
            "description": null,
            "discount": 0.0,
            "discount_percent": 0.0,
            "due_date": "",
            "excise_tax": 0.0,
            "include_tax": true,
            "order_placed_by": "OrderTry",
            "order_received_date": "2021-01-19T05:00:00.000Z",
            "order_type": "patient",
            "ordered_stats": {},
            "provincial_tax": 0.0,
            "shipped_stats": {},
            "shipping_address":{   
                "address1": "412 Sheppard Ave",
                "address2": "",
                "city": "Pickering",
                "country": "Canada",
                "postalCode": "L1V 1E5",
                "province": "ON"
            },
            "shipping_status": "pending",
            "shipping_value": 0.0,
            "status": "awaiting_approval",
            "sub_total": 0.0,
            "tax_name": "HST",
            "timestamp": "2021-01-19T15:11:53.537564+00:00",
            "total": 0.0
        }
        """

        data = request.get_json()

        data['created_by'] = 1

        data['name'] = 'create_external_order'

        data['organization_id'] = organization_id

        external_order = CreateExternalOrder.do_activity(data, None)
        firing_webhooks(organization_id=organization_id, event='orders.created', event_data=data)
        return external_order


class ExternalOrder(Resource):

    # Read single Order by id
    def get(self, order_id, organization_id=1):
        return get_resource(
            current_user=None,
            resource_id=order_id,
            organization_id=organization_id,
            resource='orders')

    # Update single Order by id
    def patch(self, order_id, organization_id=1):
        """
        Update existing order record
        """
        data = request.get_json()

        data['created_by'] = 1

        data['organization_id'] = organization_id

        data['order_id'] = order_id

        result = {}

        # To update external order
        if data['name'] == 'update_external_order':
            result = UpdateExternalOrder.do_activity(data, None)

        # To update external order status
        if data['name'] == 'external_order_update_status':
            '''
                {
                    "name": "external_order_update_status",
                    "to_status": "approved"
                }
            '''
            result = ExternalOrderUpdateStatus.do_activity(data, None)

        # To update external order crm account
        if data['name'] == 'external_order_update_account':
            '''
                {
                    "name": "external_order_update_account",
                    "to_crm_account_id": 254,
                    "to_crm_account_name": "Test CRM 2",
                    "to_order_placed_by": "OrderTry",
                    "to_order_received_date": "2021-01-19T05:00:00.000Z",
                    "to_due_date": " ",
                    "to_shipping_address": {
                        "address1": "412 Sheppard Ave",
                        "address2": "",
                        "city": "Pickering",
                        "country": "Canada",
                        "postalCode": "L1V 1E4",
                        "province": "ON"
                    }
                }

            '''
            result = ExternalOrderUpdateAccount.do_activity(data, None)

        # To update external order payment status
        if data['name'] == 'external_order_payment_status':
            result = ExternalOrderPaymentStatus.do_activity(data, None)

        # To update external order attach document
        if data['name'] == 'external_order_attach_document':
            result = ExternalOrderAttachDocument.do_activity(data, None)

        # To update external order create note
        if data['name'] == 'external_order_create_note':
            result = ExternalOrderCreateNote.do_activity(data, None)

        firing_webhooks(organization_id=organization_id, event='orders.updated', event_data=data)
        return result
