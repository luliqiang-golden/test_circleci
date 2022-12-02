"""Flask classes for the taxonomy options endpoints"""

from flask_restful import Resource
from resource_functions import get_collection, post_new_resource, get_resource, delete_resource
from resource_functions import post_update_existing_resource, select_collection_from_db
from auth0_authentication import requires_auth
from class_errors import ClientBadRequest


class TaxonomyOptions(Resource):
    """Flask resources for taxonomy options collections"""
    # Read all Taxonomy Option records
    @requires_auth
    def get(self, current_user, taxonomy_id, organization_id=None):
        filters = []

        if taxonomy_id and taxonomy_id.isdigit():
            filters.append(('taxonomy_id', '=', taxonomy_id))
        elif taxonomy_id:
            taxonomy_results, count = select_collection_from_db(
                'taxonomies',
                organization_id,
                meta=False,
                filters=[('name', '=', taxonomy_id)],
                per_page=1)
            if not count['count']:
                raise ClientBadRequest({
                    "code": "invalid_taxonomy_name",
                    "message": "Invalid taxonomy name"
                }, 400)

            filters.append(('taxonomy_id', '=', taxonomy_results[0]['id']))

        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            filters=filters,
            resource='taxonomy_options')

    # Insert new Taxonomy Option record, along with meta
    @requires_auth
    def post(self, current_user, taxonomy_id, organization_id=None):

        if taxonomy_id and not taxonomy_id.isdigit():
            taxonomy_results, count = select_collection_from_db(
                'taxonomies',
                organization_id,
                meta=False,
                filters=[('name', '=', taxonomy_id)],
                per_page=1)
            if not count['count']:
                raise ClientBadRequest({
                    "code": "invalid_taxonomy_name",
                    "message": "Invalid taxonomy name"
                }, 400)

            taxonomy_id = taxonomy_results[0]['id']

        return post_new_resource(
            current_user=current_user,
            organization_id=organization_id,
            taxonomy_id=taxonomy_id,
            resource='taxonomy_options')


class TaxonomyOption(Resource):
    """Flask resources for taxonomy options resources"""
    # Read single Taxonomy Option record by id
    @requires_auth
    def get(self, current_user, option_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=option_id,
            organization_id=organization_id,
            resource='taxonomy_options')

    # Updates existing Taxonomy Option record, along with meta
    @requires_auth
    def patch(self, current_user, option_id, organization_id=None):
        return post_update_existing_resource(
            current_user=current_user,
            resource_id=option_id,
            organization_id=organization_id,
            resource='taxonomy_options')

    # Delete Taxonomy Option record by id
    @requires_auth
    def delete(self, current_user, option_id, organization_id=None):
        return delete_resource(
            current_user=current_user,
            resource='taxonomy_options',
            resource_id=option_id,
            organization_id=organization_id)
