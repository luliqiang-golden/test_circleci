"""Endpoints for product collections and resources"""

from flask_restful import Resource

from resource_functions import get_collection, post_new_resource
from resource_functions import get_resource, post_update_existing_resource, delete_resource
from auth0_authentication import requires_auth


class Products(Resource):

    # Read all client records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='Products')

    # Insert new client record, along with meta
    @requires_auth
    def post(self, current_user, organization_id=None):
        return post_new_resource(
            current_user=current_user,
            organization_id=organization_id,
            resource='Products')


class Product(Resource):

    # Read single client record by id
    @requires_auth
    def get(self, current_user, product_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=product_id,
            organization_id=organization_id,
            resource='Products')

    # Updates existing client record, along with meta
    @requires_auth
    def patch(self, current_user, product_id, organization_id=None):
        return post_update_existing_resource(
            current_user=current_user,
            resource_id=product_id,
            organization_id=organization_id,
            resource='Products')

    # Delete client record by id
    @requires_auth
    def delete(self, current_user, product_id, organization_id=None):
        return delete_resource(
            current_user=current_user,
            resource='Products',
            resource_id=product_id,
            organization_id=organization_id)
