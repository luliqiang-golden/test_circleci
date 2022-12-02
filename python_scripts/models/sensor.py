'''This module contains database schema model for Sensor table'''

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from app import db
from class_errors import ClientBadRequest
from models.equipment import Equipment
from models.organization import Organization
from models.user import User

class SensorData(db.Model):
    __tablename__ = 'sensors_data'

    id = Column(Integer, primary_key=True)
    sensor_reading = Column(String, nullable=False)
    sensor_id = Column(ForeignKey(Equipment.id), nullable=False)
    data = Column(JSONB(astext_type=Text()))
    organization_id = Column(ForeignKey(Organization.id))
    created_by = Column(ForeignKey(User.id), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=func.now())
    sensor_type = Column(String)
    reading_timestamp = Column(DateTime(True))


    @classmethod
    def get_converted_unit_type_value(cls, unit_type, default_unit_type, value):
        if default_unit_type.lower() == unit_type.lower():
            return value
        if default_unit_type.lower() == 'celsius':
            if unit_type.lower() == 'fahrenheit':
                return round(((value - 32) * 5) / 9, 3)
            elif unit_type.lower() == 'kelvin':
                return value - 273.15
            else:
                raise ClientBadRequest({
                "code": "unknown_unit_type",
                "message": "Provided unit type doesn't supported"
            }, 400)
        if default_unit_type.lower() == 'ppm' or 'parts per million' in default_unit_type.lower():
            if unit_type.lower() == 'micromol' or unit_type.lower() == 'mg/l':
                return value
            else:
                raise ClientBadRequest({
                "code": "unknown_unit_type",
                "message": "Provided unit type doesn't supported"
            }, 400)
        return value

    @classmethod
    def deserialize_sensor_object(self, obj):
        if obj:
            return {
                "created_by": obj.created_by,
                "id": obj.id,
                "organization_id": obj.organization_id,
                "reading_timestamp": obj.reading_timestamp,
                "sensor_id": obj.sensor_id,
                "sensor_reading": obj.sensor_reading,
                "sensor_type": obj.sensor_type,
                "timestamp": obj.timestamp,
                "unit_type": obj.data.get("unit_type")
            }
        raise ClientBadRequest({"message": "No record found"}, 404)
        
    
    @classmethod
    def deserialize_sensor_queryset(self, queryset):
        '''Returns list of deserialized objects'''
        if len(queryset) > 0:
            return [self.deserialize_sensor_object(obj) for obj in queryset]
        raise ClientBadRequest({"message": "No record found"}, 404)
