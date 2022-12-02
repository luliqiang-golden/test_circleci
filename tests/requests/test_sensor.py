from ast import Or
from flask import request, jsonify
from tests.requests import AuthenticatedTestCase
from models.equipment import Equipment
from models.organization import Organization
from app import db


class TestSensorResource(AuthenticatedTestCase):
    def test_post_with_correct_fields(self):
        organization = Organization(name="Test Organization")
        db.session.add(organization)
        db.session.commit()
        equipment = Equipment(
            organization_id=organization.id,
            created_by=1,
            name='test_sensor',
            type='sensor',
            data={"model": "DS18B20","default_unit_type": "celcius"},
            external_id=1,
            stats={"stats":"test"},
            default_unit_type="celsius"
        )
        db.session.add(equipment)
        db.session.commit()
        args = {
            "sensor_reading": "32",
            "sensor_id": 1,
            "unit_type": "Fahrenheit",
            "sensor_type": "temperature",
            "reading_timestamp":"2021-05-25 11:22:36.543923+00"
        }
        response_data = jsonify({"sensor_data_id": 1, "message": "success"})
        response = self.client.post('/v1/organizations/1/sensors', json=args)
        assert response.status_code == 200
        assert response.data == response_data.data



