'''This resource module controls API related to user role'''

from serializer.user_role import UserRoleSchemaGetResponse, UserRoleSchemaPostRequest, UserRoleSchemaPutRequest, UserRoleSchemaDeleteRequest
from models.user_role_history import UserRoleHistory
from auth0_authentication import requires_auth
from controllers import BaseController
from models.user_role import UserRole
from flask import Blueprint, request
from flask.json import jsonify


user_role_get_schema_response = UserRoleSchemaGetResponse()
user_role_post_schema_request = UserRoleSchemaPostRequest()
user_role_put_schema_request = UserRoleSchemaPutRequest()
user_role_delete_schema_request = UserRoleSchemaDeleteRequest()


class UserRoleCollection(BaseController):
    @requires_auth
    def get(self, current_user, organization_id):
        
        queryparams = request.args
        
        role_id = queryparams.get('role_id')
        user_id = queryparams.get('user_id')
        
        if(not role_id and not user_id):
            response = self.deserialize_queryset(user_role_get_schema_response, UserRole.get_all_user_role(organization_id))
        else :
            if(role_id):
                response = self.deserialize_queryset(user_role_get_schema_response, UserRole.get_user_role_by_role_id(organization_id, role_id))
            else:
                response = self.deserialize_object(user_role_get_schema_response, UserRole.get_user_role_by_user_id(organization_id, user_id))
        
        return jsonify(response)
    
    @requires_auth
    def post(self, current_user, organization_id):
        
        params = self.serialize(user_role_post_schema_request, request.get_json())

        result = UserRole.add_user_role(organization_id, params.get('user_id'), params.get('role_id'))
        
        UserRoleHistory.add_history_entry(organization_id, current_user.get('user_id'), params.get('user_id'), "CREATE", None, params.get('role_id'))
        
        response = self.deserialize_object(user_role_get_schema_response, result)
        
        return jsonify(response)
        
    @requires_auth
    def put(self, current_user, organization_id, user_id):
        
        params = self.serialize(user_role_put_schema_request, request.get_json())
        
        old_role = self.deserialize_object(user_role_get_schema_response, UserRole.get_user_role_by_user_id(organization_id, user_id))

        result = UserRole.update_user_role(organization_id, params.get('role_id'), user_id)
        
        UserRoleHistory.add_history_entry(organization_id, current_user.get('user_id'), user_id, "UPDATE", old_role['role_id'], params.get('role_id'))
        
        response = self.deserialize_object(user_role_get_schema_response, result)
        
        return jsonify(response)
    
    @requires_auth
    def delete(self, current_user, organization_id, user_id):
        
        old_role = self.deserialize_object(user_role_get_schema_response, UserRole.get_user_role_by_user_id(organization_id, user_id))
        
        UserRole.delete_user_role(user_id)
        
        UserRoleHistory.add_history_entry(organization_id, current_user.get('user_id'), user_id, "DELETE", old_role['role_id'], None)
        
        return jsonify({})



# Make blueprint for user role API
user_role_bp = Blueprint('user_role', __name__)

# Define url_patterns related to role API here
user_role = UserRoleCollection.as_view('user_role')
user_role_bp.add_url_rule('/user_role', view_func=user_role, methods=['GET','POST'])
user_role_bp.add_url_rule('/user_role/<int:user_id>', view_func=user_role, methods=['PUT', 'DELETE'])