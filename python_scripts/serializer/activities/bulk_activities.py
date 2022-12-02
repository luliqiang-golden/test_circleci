'''This module contains serializer schema used for bulk activities API'''

from marshmallow import Schema, fields

class BulkActivitiesSchema(Schema):
    batch_list = fields.List(fields.Int(), required=True)
    activity = fields.Dict(required=True)