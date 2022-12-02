'''This module contains serializer schema used for role permission history API'''

from marshmallow import Schema, fields

class PermissionSchemaGetResponse(Schema):
    
    id = fields.Int()
    name = fields.Str()
    resource_type = fields.Str()
    component_friendly_name = fields.Str()
    has_access = fields.Bool(default=False,
                                   missing=False)
    parent_id = fields.Int()