'''This module contains serializer schema used for batch API'''

from marshmallow import Schema, fields
from datetime import datetime
import pytz


class BatchGenericResponse(Schema):
    
    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.DateTime()
    name = fields.Str()
    type = fields.Str()
    variety = fields.Str()
    data = fields.Dict()
    stats = fields.Dict()
    attributes = fields.Dict()
    is_child = fields.Boolean()
    is_parent = fields.Boolean()
    parent_id = fields.Int()

class BatchHarvestWholePlantSchemaPostRequest(Schema):

    harvested_quantity = fields.Int(required=True)
    weighed_by = fields.Email(required=True)
    checked_by = fields.Email(required=True)
    approved_by = fields.Email(required=True)
    scale_name = fields.Str(allow_none=True)
    timestamp = fields.DateTime(format="iso", load_default=pytz.UTC.localize(datetime.now()))

class BatchHarvestMultipleSchemaPostRequest(Schema):

    plants_harvested = fields.Int(allow_none=True, load_default = 0)
    harvested_quantity = fields.Int(required=True)
    weighed_by = fields.Email(required=True)
    checked_by = fields.Email(required=True)
    approved_by = fields.Email(required=True)
    scale_name = fields.Str(allow_none=True)
    timestamp = fields.DateTime(format="iso", load_default=pytz.UTC.localize(datetime.now()))

class BatchHarvestSchemaPostResponse(Schema):
    
    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.DateTime()
    name = fields.Str()
    type = fields.Str()
    variety = fields.Str()
    data = fields.Dict()
    stats = fields.Dict()
    attributes = fields.Dict()
    is_child = fields.Boolean()
    is_parent = fields.Boolean()
    parent_id = fields.Int()


class BatchMergeHarvestSchemaPostRequest(Schema):

    child_batches_ids = fields.List(fields.Int(required=True))
    approved_by = fields.Str(required=True)
    recorded_by = fields.Str(required=True)


class BatchWeightAdjustmentSchemaPutRequest(Schema):
    
    adjusted_weight = fields.Float(required=True)
    reason_for_modification = fields.Str(required=True)
    approved_by = fields.Email(required=True)
    checked_by = fields.Email(required=True)