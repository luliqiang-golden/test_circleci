"""Flask endpoints for taxonomies"""

from flask_restful import Resource
from resource_functions import get_collection, post_new_resource
from resource_functions import get_resource, post_update_existing_resource, delete_resource

from auth0_authentication import requires_auth


class Taxonomies(Resource):
    """Taxonomy collection endpoints"""
    # Read all client records
    @requires_auth
    def get(self, current_user, organization_id=None):
        """Get Taxonomies"""
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='Taxonomies')

    # Insert new client record, along with meta
    @requires_auth
    def post(self, current_user, organization_id=None):
        """Create new taxonomy"""
        return post_new_resource(
            current_user=current_user,
            organization_id=organization_id,
            resource='Taxonomies',
            meta=False)


class Taxonomy(Resource):
    """Taxonomy resource endpoints"""
    # Read single client record by id
    @requires_auth
    def get(self, current_user, taxonomy_id, organization_id=None):
        """Get single taxonomy"""
        return get_resource(
            current_user=current_user,
            resource_id=taxonomy_id,
            organization_id=organization_id,
            resource='Taxonomies',
            meta=False)

    # Updates existing client record, along with meta
    @requires_auth
    def patch(self, current_user, taxonomy_id, organization_id=None):
        """Update taxonomy"""
        return post_update_existing_resource(
            current_user=current_user,
            resource_id=taxonomy_id,
            organization_id=organization_id,
            resource='Taxonomies',
            meta=False)

    # Delete client record by id
    @requires_auth
    def delete(self, current_user, taxonomy_id, organization_id=None):
        """Delete Taxonomy"""
        return delete_resource(
            current_user=current_user,
            resource='Taxonomies',
            resource_id=taxonomy_id,
            organization_id=organization_id)
