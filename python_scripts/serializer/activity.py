'''This module contains serializer schema used for activities mapping API'''

from marshmallow import Schema, fields

class ActivitiesSchemaGetResponse(Schema):

    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.DateTime(format="iso")
    name = fields.Str()
    data = fields.Dict()
    parent_id = fields.Int()
    edited = fields.Bool()
    deleted = fields.Bool()