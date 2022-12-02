'''This module contains serializer schema used for inventory API'''

from marshmallow import Schema, fields, validate

class InventorySchema(Schema):

    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.DateTime(format="iso")
    name = fields.Str()
    type = fields.Str()
    variety = fields.Str()
    data = fields.Dict()
    stats = fields.Dict()
    attributes = fields.Dict()
