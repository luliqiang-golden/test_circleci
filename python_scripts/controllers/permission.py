'''This resource module controls API related to permission'''

from serializer.permission import PermissionSchemaGetResponse
from models.permission import Permission
from auth0_authentication import requires_auth
from controllers import BaseController
from flask.json import jsonify
from flask import Blueprint


permission_schema_get_response = PermissionSchemaGetResponse()


class PermissionCollection(BaseController):
    @requires_auth
    def get(self, current_user, organization_id):
        
        response = self.deserialize_queryset(permission_schema_get_response, Permission.get_all_permissions())
            
        return jsonify(response)


# Make blueprint for permission API
permission_bp = Blueprint('permissions', __name__)

# Define url_patterns related to permission API here
permission = PermissionCollection.as_view('permissions')
permission_bp.add_url_rule('/permissions', view_func=permission, methods=['GET'])