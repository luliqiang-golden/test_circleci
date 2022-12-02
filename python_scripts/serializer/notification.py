from marshmallow import Schema, fields

class NotificationSchemaGetResponse(Schema):
    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.DateTime()
    content = fields.Str()
    type = fields.Str()
