"""Endpoints for Order Items"""

from flask_restful import Resource

from resource_functions import get_collection, get_resource

from auth0_authentication import requires_auth


class OrderItems(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='order_items')


class OrderItem(Resource):

    # Read single Order Item by id
    @requires_auth
    def get(self, current_user, order_item_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=order_item_id,
            organization_id=organization_id,
            resource='order_items')
