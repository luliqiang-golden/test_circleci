'''This module contains serializer schema used for role permission history API'''

from marshmallow import Schema, fields

class RolePermissionHistorySchemaGetResponse(Schema):
    
    created_by = fields.Str()
    timestamp = fields.Str()
    role = fields.Str()
    action = fields.Str()
    old_permission = fields.List(fields.Dict())
    new_permission = fields.List(fields.Dict())
