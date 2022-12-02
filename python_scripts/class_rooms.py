"""Class for Rooms resources"""

from flask_restful import Resource
from resource_functions import get_collection, post_new_resource, get_resource
from resource_functions import post_update_existing_resource, delete_resource

from auth0_authentication import requires_auth


class Rooms(Resource):
    """Rooms Collection Endpoints"""

    @requires_auth
    def get(self, current_user, organization_id=None):
        """Read all Room records"""
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='Rooms')

    @requires_auth
    def post(self, current_user, organization_id=None):
        """Insert new Room record, along with meta"""
        return post_new_resource(
            current_user=current_user,
            organization_id=organization_id,
            resource='Rooms')


class Room(Resource):
    """Rooms Resource Endpoints"""

    @requires_auth
    def get(self, current_user, room_id, organization_id=None):
        """Read single Room record by id"""
        return get_resource(
            current_user=current_user,
            resource_id=room_id,
            organization_id=organization_id,
            resource='Rooms')

    @requires_auth
    def patch(self, current_user, room_id, organization_id=None):
        """Updates existing Room record, along with meta"""
        return post_update_existing_resource(
            current_user=current_user,
            resource_id=room_id,
            organization_id=organization_id,
            resource='Rooms')

    @requires_auth
    def delete(self, current_user, room_id, organization_id=None):
        """Delete Room record by id"""
        return delete_resource(
            current_user=current_user,
            resource='Rooms',
            resource_id=room_id,
            organization_id=organization_id)
