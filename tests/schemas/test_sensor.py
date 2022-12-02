from flask import request, jsonify
from tests.requests import AuthenticatedTestCase
from serializer.sensor import SensorSchema

class TestSensorSchema(AuthenticatedTestCase):

    def test_serializer_with_sensor_id_non_integer_value(self):
        args = {
            "sensor_reading": "32",
            "sensor_id": "some_string",
            "unit_type": "Fahrenheit",
            "sensor_type": "temperature",
            "reading_timestamp":"2021-05-25 11:22:36.543923+00"
        }
        response = {"sensor_id": [
            "Not a valid integer."
        ]}
        error_message = SensorSchema().validate(data=args)
        assert error_message == response


    def test_serializer_with_missing_fields(self):
        args = {
            "sensor_reading": "32",
            "unit_type": "Fahrenheit",
            "sensor_type": "temperature",
            "reading_timestamp":"2021-05-25 11:22:36.543923+00"
        }
        response =  {
            "sensor_id": [
                "Missing data for required field."
            ]
        }
        error_message = SensorSchema().validate(data=args)
        assert error_message == response


    def test_serializer_with_unknown_field(self):
        args = {
            "sensor_reading": "32",
            "sensor_id": 32,
            "unit_type": "Fahrenheit",
            "sensor_type": "temperature",
            "reading_timestamp":"2021-05-25 11:22:36.543923+00",
            "random_key":"random_value"
        }
        response = {'random_key': ['Unknown field.']}
        error_message = SensorSchema().validate(data=args)
        assert error_message == response

    def test_serializer_with_non_required_missing_fields(self):
        args = {
            "sensor_reading": "32",
            "sensor_id": 32,
            "unit_type": "Fahrenheit",
            "sensor_type": "temperature",
            "reading_timestamp":"2021-05-25 11:22:36.543923+00",
        }
        response = {}
        error_message = SensorSchema().validate(data=args)
        assert error_message == response

    def test_serializer_with_wrong_sensor_type(self):
        args = {
            "sensor_reading": "32",
            "sensor_id": 32,
            "unit_type": "Fahrenheit",
            "sensor_type": "xxx",
            "reading_timestamp":"2021-05-25 11:22:36.543923+00",
        }
        response = {
                    "sensor_type": [
                        "Not a valid sensor_type, please select from ('temperature', 'co2', 'humidity')"
                    ]
                }
        error_message = SensorSchema().validate(data=args)
        assert error_message == response

        