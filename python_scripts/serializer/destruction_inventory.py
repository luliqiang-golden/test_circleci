'''This module contains serializer schema used for destruction inventory API'''

from marshmallow import Schema, fields

class DequeueSchemaPostRequest(Schema):

    destruction_inventories = fields.List(fields.Int(required=True))
    reason_for_dequeue = fields.Str(required=True)
    witness_1 = fields.Email(required=True)
    witness_2 = fields.Email(required=True)

class DequeueSchemaPostResponse(Schema):
    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    name = fields.Str()
    parent_id = fields.Int()
    data = fields.Dict()