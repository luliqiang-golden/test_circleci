"""Endpoints for Consumable Lots"""

from flask_restful import Resource

from resource_functions import get_collection, get_resource

from auth0_authentication import requires_auth


class ConsumableLots(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='consumable_lots')


class ConsumableLot(Resource):

    # Read single Consumable Lot by id
    @requires_auth
    def get(self, current_user, consumable_lot_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=consumable_lot_id,
            organization_id=organization_id,
            resource='consumable_lots')
