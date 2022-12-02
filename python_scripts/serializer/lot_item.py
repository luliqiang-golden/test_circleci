from datetime import datetime
from marshmallow import Schema, fields
import pytz
class LotItemSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    variety = fields.Str(required=True)
    approved_by = fields.Email(required=True)
    sku_id = fields.Int(required=True)
    sku_name = fields.Str(required=True)
    lot_item_quantity = fields.Int(required=True)
    to_room =  fields.Str(required=True)
    unit = fields.Str(required=True)
    timestamp = fields.DateTime(format="iso", load_default=pytz.UTC.localize(datetime.now()))

