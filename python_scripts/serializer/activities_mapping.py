'''This module contains serializer schema used for activities mapping API'''

from marshmallow import Schema, fields

class ActivitiesMappingSchemaGetResponse(Schema):

    id = fields.Int()
    timestamp = fields.Str()
    name = fields.Str()
    friendly_name = fields.Str()
    is_editable = fields.Bool()
    is_deletable = fields.Bool()
    is_visible = fields.Bool()
    creates_inventory = fields.Bool()
    weight_adjustment = fields.Bool()