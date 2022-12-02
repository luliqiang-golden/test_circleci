'''Class for Sop Assignments'''

from flask_restful import Resource
from resource_functions import get_collection
from auth0_authentication import requires_auth

class SopAssignments(Resource):
    
    @requires_auth
    def get(self, current_user, sop_id, organization_id=None):

        resource = 'vw_sop_assignments'

        filters = [
            ('id', '=', sop_id),
            ('status', '!=', 'disabled')
        ]

        collection = get_collection(
            current_user=current_user,
            organization_id=organization_id,
            filters=filters,
            resource=resource)

        return collection

class SopSignatures(Resource):

    '''
    serves as the endpoint for SOP signatures
    '''
    
    @requires_auth
    def get(self, current_user, organization_id=None):

        resource = 'vw_sop_assignments'

        filters = [
            ('status', '!=', 'disabled'),
            ('signature_status', '!=', 'unsigned'),
        ]

        collection = get_collection(
            current_user=current_user,
            organization_id=organization_id,
            filters=filters,
            resource=resource)

        return collection
