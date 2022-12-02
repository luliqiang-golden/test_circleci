'''This module contains serializer schema used for user role API'''

from marshmallow import Schema, fields
from sqlalchemy import true

class UserRoleSchemaGetResponse(Schema):
    
    user_id = fields.Int()
    user_name = fields.Str()
    user_email = fields.Str()
    user_enabled = fields.Bool()
    job_title = fields.Str()
    role_id = fields.Int()
    role_name = fields.Str()
    role_description = fields.Str()
    organization_id = fields.Int()

    
class UserRoleSchemaPostRequest(Schema):

    user_id = fields.Int(required=true)
    role_id = fields.Int(required=true)


class UserRoleSchemaPutRequest(Schema):

    role_id = fields.Int(required=true)


class UserRoleSchemaDeleteRequest(Schema):

    role_id = fields.Int(required=true)