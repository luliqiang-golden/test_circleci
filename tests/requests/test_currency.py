from flask import request, jsonify
from tests.requests import AuthenticatedTestCase
from serializer.currency import CurrencySchema

class TestCurrenciesResource(AuthenticatedTestCase):
    def test_post_with_correct_fields(self):
        args = {
            "alphabetic_code": "CAD",
            "entity": [
                "Canada"
            ],
            "minor_unit": 2,
            "name": "Canadian Dollar",
            "sign": "CA$"
        }
        response_data = jsonify({"currency_id": 1, "message": "success"})
        response = self.client.post('/v1/currencies', json=args)
        assert response.status_code == 201
        assert response.data == response_data.data
