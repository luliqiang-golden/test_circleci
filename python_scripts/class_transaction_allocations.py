"""Endpoints for Transaction Allocations"""

from flask import jsonify, request
from flask_restful import Resource

from resource_functions import get_collection, get_resource

from class_errors import ClientBadRequest

from auth0_authentication import requires_auth


class TransactionAllocations(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='transaction_allocations')


class TransactionAllocation(Resource):

    # Read single Transaction Allocation by id
    @requires_auth
    def get(self, current_user, transaction_allocation_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=transaction_allocation_id,
            organization_id=organization_id,
            resource='transaction_allocations')
