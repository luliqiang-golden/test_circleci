'''This resource module controls API related to role permission'''

from serializer.role_permission import RolePermissionSchemaPostRequest, RolePermissionSchemaPutRequest, RolePermissionSchemaGetResponse, RolePermissionBatchSchemaPutRequest
from models.role_permission_history import RolePermissionHistory
from models.role_permission import RolePermission
from auth0_authentication import requires_auth
from controllers import BaseController
from flask import Blueprint, request
from flask.json import jsonify
from models.role import Role

role_permission_schema_post_request = RolePermissionSchemaPostRequest()
role_permission_schema_put_request = RolePermissionSchemaPutRequest()
role_permission_batch_schema_put_request = RolePermissionBatchSchemaPutRequest(many=True)
class RolePermissionCollection(BaseController):

    @requires_auth
    def get(self, current_user, organization_id, role_id=None):
        
        response = []

        if(not role_id):
            roles = RolePermission.get_all_role_permission(organization_id)
            for role in roles:
                response = response + RolePermission.get_role_permission_by_id(organization_id, role.role_id)
        else:
            response = RolePermission.get_role_permission_by_id(organization_id, role_id)

        return jsonify(RolePermissionSchemaGetResponse(many=True).dump(response))

    @requires_auth
    def post(self, current_user, organization_id):

        params = self.serialize(role_permission_schema_post_request, request.get_json())



        role_result = Role.add_role(organization_id, current_user.get('user_id'), params.get('name'), params.get('role_description'))

        RolePermission.add_role_permission(role_result.id, params.get('permission_ids'))


        response = RolePermission.get_role_permission_by_id(organization_id, role_result.id)
        response = RolePermissionSchemaGetResponse(many=True).dump(response)


        new_permission_set = [{'component_friendly_name': permission['component_friendly_name'], 'resource_type': permission['resource_type']} for permission in response[0]['permissions']]

        RolePermissionHistory.add_history_entry(organization_id, current_user.get('user_id'), role_result.id, "CREATE", [], new_permission_set)


        return jsonify(response)

    @requires_auth
    def put(self, current_user, organization_id, role_id=None):


        params = self.serialize(role_permission_schema_put_request, request.get_json())


        if(params.get('name')):
            Role.update_role(organization_id, role_id, params.get('name'))



        old_permission = RolePermission.get_role_permission_by_id(organization_id, role_id)
        old_permission = RolePermissionSchemaGetResponse(many=True).dump(old_permission)
        
        old_permission_set = [{'component_friendly_name': permission['component_friendly_name'], 'resource_type': permission['resource_type']} for permission in old_permission[0]['permissions']]



        if(params.get('permission_ids')):
            RolePermission.delete_role(role_id)
            RolePermission.add_role_permission(role_id, params.get('permission_ids'))


        response = RolePermission.get_role_permission_by_id(organization_id, role_id)
        response = RolePermissionSchemaGetResponse(many=True).dump(response)


        new_permission_set = [{'component_friendly_name': permission['component_friendly_name'], 'resource_type': permission['resource_type']} for permission in response[0]['permissions'] if permission['has_access'] == True]

        RolePermissionHistory.add_history_entry(organization_id, current_user.get('user_id'), role_id, "UPDATE", old_permission_set, new_permission_set)


        return jsonify(response)

    @requires_auth
    def delete(self, current_user, organization_id, role_id):

        old_permission = RolePermission.get_role_permission_by_id(organization_id, role_id)
        old_permission = RolePermissionSchemaGetResponse(many=True).dump(old_permission)

        old_permission_set = [{'component_friendly_name': permission['component_friendly_name'], 'resource_type': permission['resource_type']} for permission in old_permission[0]['permissions'] if permission['has_access'] == True]

        Role.delete_role(role_id)

        RolePermissionHistory.add_history_entry(organization_id, current_user.get('user_id'), role_id, "DELETE", old_permission_set, {})

        return jsonify({})


class RolePermissionBatchCollection(BaseController):
    
    @requires_auth
    def put(self, current_user, organization_id):

        payload = self.serialize(role_permission_batch_schema_put_request, request.get_json())
        
        response = []
        
        for entry in payload:

            if(entry.get('name')):
                Role.update_role(organization_id, entry.get('role_id'), entry.get('name'))

            old_permission = RolePermission.get_role_permission_by_id(organization_id, entry.get('role_id'))
            old_permission = RolePermissionSchemaGetResponse(many=True).dump(old_permission)
            
            old_permission_set = [{'component_friendly_name': permission['component_friendly_name'], 'resource_type': permission['resource_type']} for permission in old_permission[0]['permissions'] if permission['has_access'] == True]

            if(entry.get('permission_ids')):
                RolePermission.delete_role(entry.get('role_id'))
                RolePermission.add_role_permission(entry.get('role_id'), entry.get('permission_ids'))

            res = RolePermission.get_role_permission_by_id(organization_id, entry.get('role_id'))
            res = RolePermissionSchemaGetResponse(many=True).dump(res)
            response = response + res


            new_permission_set = [{'component_friendly_name': permission['component_friendly_name'], 'resource_type': permission['resource_type']} for permission in res[0]['permissions'] if permission['has_access'] == True]

            RolePermissionHistory.add_history_entry(organization_id, current_user.get('user_id'), entry.get('role_id'), "UPDATE", old_permission_set, new_permission_set)

        return jsonify(response)


# Make blueprint for role_permission API
role_permission_bp = Blueprint('role_permission', __name__)

# Define url_patterns related to role_permission API here
role_permission = RolePermissionCollection.as_view('role_permission')
role_permission_batch = RolePermissionBatchCollection.as_view('role_permission_batch')
role_permission_bp.add_url_rule('/role_permission', view_func=role_permission, methods=['GET', 'POST'])
role_permission_bp.add_url_rule('/role_permission/<int:role_id>', view_func=role_permission, methods=['GET', 'PUT', 'DELETE'])
role_permission_bp.add_url_rule('/role_permission/batch', view_func=role_permission_batch, methods=['PUT'])