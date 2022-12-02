'''This module contains serializer schema used for backdate activities API'''

from marshmallow import Schema, fields, pre_load
from datetime import datetime

class BackdateActivitiesSchemaPutRequest(Schema):

    activity_ids = fields.List(fields.Int(required=True))
    reason_for_modification = fields.Str(required=True)
    timestamp = fields.DateTime(required=True)
    
