'''This module contains serializer schema used for create activity log API'''

from marshmallow import Schema, fields

class UploadSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    content_type = fields.Str()
    category = fields.Str()

class CreateActivityLogDataSchema(Schema):
    description = fields.Str(required=True)
    detail = fields.Str(required=True)
    inventory_id = fields.Int(required=True)
    uploads = fields.List(fields.Nested(UploadSchema))

class CreateActivityLogSchemaPostRequest(Schema):

    description = fields.Str(required=True)
    detail = fields.Str(required=True)
    inventory_id = fields.Int(required=True)
    uploads = fields.List(fields.Nested(UploadSchema))

class CreateActivityLogSchemaPutRequest(Schema):

    description = fields.Str(required=True)
    detail = fields.Str(required=True)
    inventory_id = fields.Int(required=True)
    uploads = fields.List(fields.Nested(UploadSchema))
    reason_for_modification = fields.Str(required=True)
    timestamp = fields.Str()

class CreateActivityLogSchemaDeleteRequest(Schema):
    reason_for_modification = fields.Str(required=True)

class CreateActivityLogSchemaResponse(Schema):
    
    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.Str()
    name = fields.Str()
    data = fields.Nested(CreateActivityLogDataSchema)
    parent_id = fields.Int()