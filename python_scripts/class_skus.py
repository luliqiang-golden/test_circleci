"""Endpoints for SKUs"""
from flask_restful import Resource

from resource_functions import delete_resource
from resource_functions import get_collection, get_resource

from auth0_authentication import requires_auth


class SKUs(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='Skus')

    # Insert new article record, along with meta
    # @requires_auth
    # def post(self, current_user, organization_id=None):
        # return post_new_resource(
        #     current_user=current_user,
        #     organization_id=organization_id,
        #     resource='Skus')


class SKU(Resource):

    # Read single SKU by id
    @requires_auth
    def get(self, current_user, sku_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=sku_id,
            organization_id=organization_id,
            resource='Skus')

    # Updates existing SKU record, along with meta
    # @requires_auth
    # def patch(self, current_user, inventory_id, organization_id=None):
    #     return post_update_existing_resource(
    #         current_user=current_user,
    #         resource_id=inventory_id,
    #         organization_id=organization_id,
    #         resource='Skus')

    @requires_auth
    def delete(self, current_user, sku_id, organization_id=None):
        return delete_resource(
            current_user=current_user,
            resource='Skus',
            resource_id=sku_id,
            organization_id=organization_id)
