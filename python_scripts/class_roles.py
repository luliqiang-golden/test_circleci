"""Class for roles resource"""
from flask import jsonify
from flask_restful import Resource


from auth0_authentication import requires_auth
from activities import ACTIVITIES
from db_functions import TABLE_COLUMNS


class Roles(Resource):
    """Class for roles collection"""
    # Read all Role records
    @requires_auth
    def get(self, current_user, organization_id=None):
        """Get a list of roles"""

        role = {'data': [{'id': '1', 'name': 'Admin', 'organization_id': organization_id}]}
        return jsonify(role)

class Role(Resource):
    """Methods for dealing with single role"""

    @requires_auth
    def get(self, current_user, role_id, organization_id=None):
        """Get a single resource"""

        role = {'data': [{'id': '1', 'name': 'Admin', 'organization_id': organization_id}]}
        return jsonify(role)

class ActivitiesList(Resource):
    """Class for activities list endpoint"""

    # Read all activity names
    @requires_auth
    def get(self, current_user, organization_id=None):
        """Get a collection of activities"""
        return jsonify(list(ACTIVITIES.keys()))

class TablesList(Resource):
    """Class for tables list endpoint"""

    # Read all table names
    @requires_auth
    def get(self, current_user, organization_id=None):
        """Get a collection of tables"""
        return jsonify(list(TABLE_COLUMNS.keys()))
