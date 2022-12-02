'''This module contains serializer schema used for user role history API'''

from marshmallow import Schema, fields

class UserRoleHistorySchemaGetResponse(Schema):
    
    created_by = fields.Str()
    timestamp = fields.Str()
    user = fields.Str()
    action = fields.Str()
    old_role = fields.Str()
    new_role = fields.Str()
