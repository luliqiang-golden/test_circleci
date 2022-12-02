"""Endpoints for Sop departments"""
from flask_restful import Resource
from resource_functions import get_collection, get_resource
from auth0_authentication import requires_auth


class Departments(Resource):
    # Read all
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='departments')


class Department(Resource):
    @requires_auth
    def get(self, current_user, department_id, organization_id=None):
        """Get a single department by id"""
        return get_resource(
            current_user=current_user,
            resource_id=department_id,
            organization_id=organization_id,
            resource='departments')