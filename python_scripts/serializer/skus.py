'''This module contains serializer schema used for skus API'''

from marshmallow import Schema, fields, EXCLUDE

class SkusSchema(Schema):
    
    id = fields.Int()
    organization_id = fields.Int(required=True)
    created_by = fields.Int()
    timestamp = fields.DateTime(format="iso")
    name = fields.Str(required=True)
    variety = fields.Str(required=True)
    cannabis_class = fields.Str()
    target_qty = fields.Float()
    data = fields.Dict()
    attributes = fields.Dict()
    target_qty_unit = fields.Str(required=True)
    sales_class = fields.Str()
    price = fields.Decimal(as_string=True)
    current_inventory = fields.Int()
    package_type = fields.Str(required=True)
    
    class Meta:
        unknown = EXCLUDE
        


class SkusUpdateSchema(Schema):
    
    id = fields.Int()
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.DateTime(format="iso")
    name = fields.Str()
    variety = fields.Str()
    cannabis_class = fields.Str()
    target_qty = fields.Float()
    data = fields.Dict()
    attributes = fields.Dict()
    target_qty_unit = fields.Str()
    sales_class = fields.Str()
    price = fields.Decimal(as_string=True)
    current_inventory = fields.Int()
    package_type = fields.Str()
    
    class Meta:
        unknown = EXCLUDE