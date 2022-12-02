"""Endpoints for External Shipments"""

from flask_restful import Resource
from flask import request

from resource_functions import get_collection, get_resource

from activities.external_activities.create_external_shipment import CreateExternalShipment
from activities.external_activities.external_shipment_packaged import ExternalShipmentPackaged
from activities.external_activities.external_shipment_shipped import ExternalShipmentShipped
from activities.external_activities.external_shipment_delivered import ExternalShipmentDelivered
from activities.external_activities.external_shipment_update_delivered_date import ExternalShipmentUpdateDeliveredDate
from activities.external_activities.external_shipment_update_shipped_date import ExternalShipmentUpdateShippedDate
from activities.external_activities.external_shipment_update_shipping_address import ExternalShipmentUpdateShippingAddress
from activities.external_activities.external_shipment_update_tracking_number import ExternalShipmentUpdateTrackingNumber

class ExternalShipments(Resource):

    # Read all article records
    def get(self, organization_id=1):
        return get_collection(
            current_user=None,
            organization_id=organization_id,
            resource='shipments')

    def post(self, organization_id=1):
        '''
        post: {
                "name":"create_external_shipment",
                "crm_account_id": 254,
                "shipping_address": {
                    "address1": "412 Sheppard Ave",
                    "address2": "",
                    "city": "Pickering",
                    "country": "Canada",
                    "postalCode": "L1V 1E4",
                    "province": "ON"
                }    
        }
        '''

        data = request.get_json()

        data['created_by'] = 1

        data['organization_id'] = organization_id

        return CreateExternalShipment.do_activity(data, None)


class ExternalShipment(Resource):

    # Read single Shipment by id
    def get(self, shipment_id, organization_id=1):
        return get_resource(
            current_user=None,
            resource_id=shipment_id,
            organization_id=organization_id,
            resource='shipments')

    def patch(self, shipment_id, organization_id=1):
      
        
        data = request.get_json()

        data['shipment_id'] = shipment_id
        data['created_by'] = 1
        data['organization_id'] = organization_id

        if(data['name'] == 'external_shipment_packaged'):
            '''
                {
                    "name":"external_shipment_packaged",
                    "to_room": "Grow Bay 1"
                    
                }
            '''
            return ExternalShipmentPackaged.do_activity(data, None)

        if(data['name'] == 'external_shipment_shipped'):
            '''
                {
                    "name":"external_shipment_shipped",
                }
            '''
            return ExternalShipmentShipped.do_activity(data, None)

        if(data['name'] == 'external_shipment_delivered'):
            '''
                {
                    "name":"external_shipment_delivered",
                }
            '''
            return ExternalShipmentDelivered.do_activity(data, None)

        if(data['name'] == 'external_shipment_update_shipped_date'):
            '''
                {
                    "name":"external_shipment_update_shipped_date",
                    "to_shipped_date":"2021-01-29T15:16:26.723976+00:00"
                }
            '''
            return ExternalShipmentUpdateShippedDate.do_activity(data, None)

        if(data['name'] == 'external_shipment_update_delivered_date'):
            '''
                {
                    "name":"external_shipment_update_delivered_date",
                    "to_delivered_date":"2021-01-29T15:16:26.723976+00:00"
                }
            '''
            return ExternalShipmentUpdateDeliveredDate.do_activity(data, None)

        if(data['name'] == 'external_shipment_update_shipping_address'):
            '''
                {
                    "name":"external_shipment_update_shipping_address",
                    "to_shipping_address": {   
                        "address1": "412 Sheppard Ave",
                        "address2": "",
                        "city": "Pickering",
                        "country": "Canada",
                        "postalCode": "L1V 1E5",
                        "province": "ON"
                    }
                }
            '''
            return ExternalShipmentUpdateShippingAddress.do_activity(data, None)

        if(data['name'] == 'external_shipment_update_tracking_number'):
            '''
                {
                    "name":"external_shipment_update_tracking_number",
                    "to_tracking_number":"123"
                }
            '''
            return ExternalShipmentUpdateTrackingNumber.do_activity(data, None)
