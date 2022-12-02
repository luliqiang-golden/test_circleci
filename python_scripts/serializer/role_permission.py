'''This module contains serializer schema used for role permission API'''
from marshmallow import Schema, ValidationError, fields, pre_dump, pre_load, validates
from models.role_permission import RolePermission
from models.user_role import UserRole
from sqlalchemy import true

def partition(items, container_name):
    seen = []
    
    return [
        {
            'role_id': i['role_id'],
            'role_name': i['role_name'], 
            'organization_id': i['organization_id'], 
            'role_description': i['role_description'],
            'users_qty': UserRole.get_user_count_by_role_id(i['role_id']),
            'sections_qty': RolePermission.get_count_of_groups_by_role_id(i['role_id']),
            container_name: [item for item in items if item['role_id'] == i['role_id']],
        }
        for i in reversed(items) if i['role_id'] not in seen and not seen.append(i['role_id'])
    ]
class PermissionsSchema(Schema):
    class Meta:
        fields = (
            'id',
            'name',
            'component_friendly_name',
            'resource_type',
            'parent_id',
            'has_access'
        )
class RolePermissionSchemaGetResponse(Schema):

    permissions = fields.Nested(PermissionsSchema, many=True)
    class Meta:
        fields = (
            'role_id', 
            'role_name', 
            'organization_id', 
            'role_description',
            'users_qty',
            'sections_qty',
            'permissions'
        )

    @pre_dump(pass_many=True)
    def partition_permissions(self, data, many):
        return partition(data, 'permissions')

class RolePermissionSchemaPostRequest(Schema):

    name = fields.Str(required=true)
    permission_ids = fields.List(fields.Int, required=true)
    
    @pre_load
    def strip_name(self, in_data, **kwargs):
        in_data['name'] = in_data.get('name').strip()
        return in_data
    
    @validates('permission_ids')
    def validate_length(self, value):
        if len(value) < 1:
            raise ValidationError('Permissions quantity must be greater than 0.')
    
class RolePermissionSchemaPutRequest(Schema):

    name = fields.Str()
    permission_ids = fields.List(fields.Int)
    
    @pre_load
    def strip_name(self, in_data, **kwargs):
        if(in_data.get('name')):
            in_data['name'] = in_data.get('name').strip()
        return in_data

    
    @validates('permission_ids')
    def validate_length(self, value):
        if len(value) < 1:
            raise ValidationError('Permissions quantity must be greater than 0.')

class RolePermissionBatchSchemaPutRequest(Schema):

    role_id = fields.Int(required=true)
    name = fields.Str()
    permission_ids = fields.List(fields.Int)
    
    @pre_load
    def strip_name(self, in_data, **kwargs):
        if(in_data.get('name')):
            in_data['name'] = in_data.get('name').strip()
        return in_data
    
    @validates('permission_ids')
    def validate_length(self, value):
        if len(value) < 1:
            raise ValidationError('Permissions quantity must be greater than 0.') 