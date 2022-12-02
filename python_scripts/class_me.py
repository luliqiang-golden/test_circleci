"""Endpoint for current user information"""

from flask_restful import Resource
from auth0_authentication import requires_auth

from db_functions import select_user_active_orgs_and_roles


class Me(Resource):
    """Return information about user based on access token"""

    @requires_auth
    def get(self, current_user):
        """Return user object with orgs and role"""

        return select_user_active_orgs_and_roles(current_user['email'])
