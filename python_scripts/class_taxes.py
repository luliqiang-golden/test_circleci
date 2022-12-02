"""Class for Taxes resources"""

from flask_restful import Resource
from resource_functions import get_collection

from auth0_authentication import requires_auth


class Taxes(Resource):
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='taxes')