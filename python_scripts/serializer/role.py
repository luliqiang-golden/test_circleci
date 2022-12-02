'''This module contains serializer schema used for role API'''

from marshmallow import Schema, fields
from sqlalchemy import true

class RoleSchemaGetResponse(Schema):
    
    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.Str()
    name = fields.Str()
    role_description = fields.Str()
    
class RoleSchemaPostRequest(Schema):

    name = fields.Str(required=true)
    role_description = fields.Str(default=None, allow_none=True)