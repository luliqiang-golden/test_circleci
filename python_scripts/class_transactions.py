"""Endpoints for Transactions"""

from flask import jsonify, request
from flask_restful import Resource

from resource_functions import get_collection, get_resource

from class_errors import ClientBadRequest

from auth0_authentication import requires_auth


class Transactions(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='transactions')


class Transaction(Resource):

    # Read single Transaction by id
    @requires_auth
    def get(self, current_user, transaction_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=transaction_id,
            organization_id=organization_id,
            resource='transactions')
