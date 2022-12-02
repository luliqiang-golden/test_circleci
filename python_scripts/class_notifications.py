"""Class for sop log"""
from flask_restful import Resource
from db_functions import select_from_db

from auth0_authentication import requires_auth
from resource_functions import get_collection



class Notifications(Resource):
    """Class responsible for SOP activities log

    Arguments:
        Resource {MethodView} -- Resource from flask_restful

    Raises:
        ClientBadRequest -- When the request is invalid this error is raised
    """
    
    @requires_auth
    def get(self, current_user, organization_id):
        """Fetches collection of SOP activities

        Arguments:
            organization_id {int} -- Organization id that is being queried on

        Returns:
            flask.Response -- A response containing the SOP activities as a json
        """
        resource = 'vw_sop_notifications'

        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource=resource)
