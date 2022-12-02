from flask import request, jsonify
from tests.requests import AuthenticatedTestCase
from serializer.currency import CurrencySchema

class TestCurrenciesSchema(AuthenticatedTestCase):

    def test_serializer_with_minor_unit_less_than_one(self):
        args = {
            "alphabetic_code": "CAD",
            "entity": [
                "Canada"
            ],
            "minor_unit": 0,
            "name": "Canadian Dollar",
            "sign": "CA$"
        }
        response = {'minor_unit': ['Value must be greater than 0']}
        error_message = CurrencySchema().validate(data=args)
        assert error_message == response


    def test_serializer_with_missing_fields(self):
        args = {
            "entity": [
                "Canada"
            ],
            "minor_unit": 2,
            "name": "Canadian Dollar",
            "sign": "CA$"
        }
        response = {'alphabetic_code': ['Missing data for required field.']}
        error_message = CurrencySchema().validate(data=args)
        assert error_message == response


    def test_serializer_with_unknown_field(self):
        args = {
            "alphabetic_code": "CAD",
            "entity": [
                "Canada"
            ],
            "minor_unit": 2,
            "name": "Canadian Dollar",
            "sign": "CA$",
            "random_key": "random_value"
        }
        response = {'random_key': ['Unknown field.']}
        error_message = CurrencySchema().validate(data=args)
        assert error_message == response
        