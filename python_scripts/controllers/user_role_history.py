'''This resource module controls API related to user role history'''

from serializer.user_role_history import UserRoleHistorySchemaGetResponse
from models.user_role_history import UserRoleHistory
from auth0_authentication import requires_auth
from controllers import BaseController
from flask.json import jsonify
from flask import Blueprint


user_role_history_schema_get_response = UserRoleHistorySchemaGetResponse()


class UserRoleHistoryCollection(BaseController):
    @requires_auth
    def get(self, current_user, organization_id):
        
        response = self.deserialize_queryset(user_role_history_schema_get_response, UserRoleHistory.get_user_history(organization_id))
            
        return jsonify(response)


# Make blueprint for user role history API
user_role_history_bp = Blueprint('user_role_history', __name__)

# Define url_patterns related to user role history API here
user_role_history = UserRoleHistoryCollection.as_view('user_role_history')
user_role_history_bp.add_url_rule('/user_role_history', view_func=user_role_history, methods=['GET'])