'''This module contains serializer schema used for revert destruction activity API'''

from marshmallow import Schema, fields

class RevertDestructionsDataSchema(Schema):

    destruction_inventories = fields.List(fields.Str(required=True))
    reason_for_reversion = fields.Str(required=True)
    witness_1 = fields.Email(required=True)
    witness_2 = fields.Email(required=True)

class RevertDestructionsSchemaPostRequest(Schema):

    destruction_inventories = fields.List(fields.Str(required=True))
    reason_for_reversion = fields.Str(required=True)
    witness_1 = fields.Email(required=True)
    witness_2 = fields.Email(required=True)

class RevertDestructionsSchemaDeleteRequest(Schema):
    reason_for_reversion = fields.Str(required=True)
    
class RevertDestructionsSchemaResponse(Schema):
    
    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.Str()
    name = fields.Str()
    data = fields.Nested(RevertDestructionsDataSchema)
    parent_id = fields.Int()