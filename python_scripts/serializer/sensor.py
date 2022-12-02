'''This module contains serializer schema used for Sensor API'''

from marshmallow import Schema, fields, validates, ValidationError


class SensorSchema(Schema):

    SENSOR_CHOICES = ('temperature', 'co2', 'humidity')

    id = fields.Int()
    sensor_reading = fields.Decimal(required=True)
    sensor_id = fields.Int(required=True)
    sensor_type = fields.Str(required=True)
    unit_type = fields.Str(required=True)
    reading_timestamp = fields.DateTime(required=True)
    organization_id = fields.Int()
    created_by = fields.Int()
    timestamp = fields.DateTime()

    @validates('sensor_type')
    def validate_sensor_type(self, sensor_type):
        return self._validate_choices(
            sensor_type,
            self.SENSOR_CHOICES,
            'sensor_type'
        )
    
    @classmethod
    def _validate_choices(cls, value, choices, entity):
        if value not in choices:
            raise ValidationError(f"Not a valid {entity}, please select from {choices}")

        


 

        