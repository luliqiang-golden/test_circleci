'''This resource module controls API related to role permission history'''

from serializer.role_permission_history import RolePermissionHistorySchemaGetResponse
from models.role_permission_history import RolePermissionHistory
from auth0_authentication import requires_auth
from controllers import BaseController
from flask.json import jsonify
from flask import Blueprint


role_permission_history_schema_get_response = RolePermissionHistorySchemaGetResponse()


class RolePermissionHistoryCollection(BaseController):
    @requires_auth
    def get(self, current_user, organization_id):
        
        response = self.deserialize_queryset(role_permission_history_schema_get_response, RolePermissionHistory.get_permission_role_history(organization_id))
            
        return jsonify(response)


# Make blueprint for user role history API
role_permission_history_bp = Blueprint('role_permission_history', __name__)

# Define url_patterns related to user role history API here
role_permission_history = RolePermissionHistoryCollection.as_view('role_permission_history')
role_permission_history_bp.add_url_rule('/role_permission_history', view_func=role_permission_history, methods=['GET'])