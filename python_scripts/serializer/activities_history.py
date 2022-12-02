'''This module contains serializer schema used for activities history API'''

from marshmallow import Schema, fields

class ActivitiesHistorySchemaGetResponse(Schema):

    id = fields.Int()
    organization_id = fields.Int()
    changed_by = fields.Str()
    changed_at = fields.Str()
    name = fields.Str()
    action = fields.Str()
    old_data = fields.Dict()
    new_data = fields.Dict()
    old_timestamp = fields.Str()
    new_timestamp = fields.Str()
    activity_id = fields.Int()
