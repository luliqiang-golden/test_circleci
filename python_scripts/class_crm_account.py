"""Endpoints for CRM Accounts"""


from flask_restful import Resource

from resource_functions import get_collection, get_resource


from auth0_authentication import requires_auth


class CRMAccounts(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='crm_accounts')


class CRMAccount(Resource):

    # Read single CRM Account by id
    @requires_auth
    def get(self, current_user, crm_account_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=crm_account_id,
            organization_id=organization_id,
            resource='crm_accounts')
