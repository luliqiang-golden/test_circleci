'''This resource module controls API related to role'''
from serializer.role import RoleSchemaGetResponse, RoleSchemaPostRequest
from auth0_authentication import requires_auth
from controllers import BaseController
from flask import Blueprint
from flask.json import jsonify
from models.role import Role

role_schema_get_response = RoleSchemaGetResponse()
role_schema_post_request = RoleSchemaPostRequest()

class RoleCollection(BaseController):
    
    @requires_auth
    def get(self, current_user, organization_id, role_id=None):
        
        if(not role_id):
            response = self.deserialize_queryset(role_schema_get_response, Role.get_all_roles(organization_id))
        else:
            response = self.deserialize_object(role_schema_get_response, Role.get_role_by_id(organization_id, role_id))
            
        return jsonify(response)


# Make blueprint for role API
role_bp = Blueprint('role', __name__)

# Define url_patterns related to role API here
role = RoleCollection.as_view('role')
role_bp.add_url_rule('/role', view_func=role, methods=['GET'])
role_bp.add_url_rule('/role/<int:role_id>', view_func=role, methods=['GET'])
