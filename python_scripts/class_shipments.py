"""Endpoints for Shipments"""

from flask_restful import Resource

from resource_functions import get_collection, get_resource

from auth0_authentication import requires_auth


class Shipments(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='shipments')


class Shipment(Resource):

    # Read single Shipment by id
    @requires_auth
    def get(self, current_user, shipment_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=shipment_id,
            organization_id=organization_id,
            resource='shipments')
