'''This module contains serializer schema used for currency API'''

from marshmallow import Schema, fields, validate


class CurrencySchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    alphabetic_code = fields.Str(required=True)
    minor_unit = fields.Int(required=True, validate=[validate.Range(min=1, error="Value must be greater than 0")])
    sign = fields.Str(required=True)
    entity = fields.List(fields.Str(required=True))
    created_at = fields.Str()