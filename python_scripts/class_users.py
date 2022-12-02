"""User management endpoints"""
import re

from flask_restful import Resource
from flask import jsonify, request
from auth0.v3 import Auth0Error

from db_functions import insert_into_db, update_into_db, delete_from_db, select_resource_from_db
from resource_functions import prep_args, get_collection, get_resource
from auth0_authentication import requires_auth, auth0_client
from auth0_authentication import auth0_reset_pw, AUTH0_CONNECTION, auth0_login

from class_errors import ClientBadRequest


class Users(Resource):
    """Class users"""
    # Read all client records
    @requires_auth
    def get(self, current_user, organization_id=None):
        """Get collection of users"""
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='Users')

class UserLoggedIn(Resource):
    """Get current user_id in current organization"""
    @requires_auth
    def get(self, current_user, organization_id):
        """Get a single user"""

        """this line use filter to get current user's account which in organization_id"""
        roles = [role for role in current_user["org_roles"] if role["organization"]["id"] == organization_id]
        """get this account's user_id"""
        user_info_id = roles[0]["user_id"]
        return get_resource(
            current_user=current_user,
            resource_id=user_info_id,
            organization_id=None,
            resource='Users')


class User(Resource):
    """User management endpoints"""
    # Read single client record by id
    @requires_auth
    def get(self, current_user, user_id, organization_id=None):
        """Get a single user"""
        return get_resource(
            current_user=current_user,
            resource_id=user_id,
            organization_id=organization_id,
            resource='Users')

    # Updates existing client record, along with meta
    @requires_auth
    def patch(self, current_user, user_id, organization_id=None):
        """Update a single user"""
        data = request.get_json(force=True)

        if 'name' not in data:
            raise ClientBadRequest({
                "code": "email_not_found",
                "message": "Email required in name field."
            }, 400)

        if 'enabled' not in data:
            raise ClientBadRequest({
                "code":
                "user_status_not_set",
                "message":
                "User enabled status must be set when updating a user."
            }, 400)

        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['name']):
            raise ClientBadRequest({
                "code":
                "incorrect_email_format",
                "message":
                "Email address does not appear to be properly formatted."
            }, 400)

        resource = 'Users'

        args = prep_args(resource, organization_id, current_user)

        db_result = update_into_db(resource, user_id, args)

        return jsonify(db_result)


class UserLogin(Resource):
    """Provides route for obtaining auth token"""

    def post(self):
        """Obtain a token for a user"""

        args = request.get_json(force=True)

        required_args = ['username', 'password']

        if not all(arg in args for arg in required_args):
            raise ClientBadRequest(
                {
                    "code": "missing_required_fields",
                    "message": "Missing one of {}".format(required_args)
                }, 400)

        token = auth0_login(args['username'], args['password'])

        return jsonify(token)
