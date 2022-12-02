from flask import request, jsonify
from tests.requests import AuthenticatedTestCase
from serializer.lot_item import LotItemSchema

class TestLotItemSchema(AuthenticatedTestCase):

    def test_serializer_with_correct_params(self):
        args = {
            "name":"create_lot_item",
            "variety":"213",
            "approved_by":"ajay@wilcompute.com",
            "sku_id":"1982",
            "sku_name":"213 1g", 
            "unit":"dry", 
            "lot_item_quantity":1000, 
            "to_room":"propagation"
        }
        response = {}
        error_message = LotItemSchema().validate(data=args)
        assert error_message == response


    def test_serializer_with_missing_fields(self):
        args = {
            "name":"create_lot_item",
            "variety":"213",
            "approved_by":"ajay@wilcompute.com",
            "sku_id":"1982",
            "sku_name":"213 1g", 
            "unit":"dry", 
            "lot_item_quantity":1000
        }
        response =  {
            "to_room": [
                "Missing data for required field."
            ]
        }
        error_message = LotItemSchema().validate(data=args)
        assert error_message == response


    def test_serializer_with_unknown_field(self):
        args = {
            "name":"create_lot_item",
            "variety":"213",
            "approved_by":"ajay@wilcompute.com",
            "sku_id":"1982",
            "sku_name":"213 1g", 
            "unit":"dry", 
            "lot_item_quantity":1000, 
            "to_room":"propagation",
            "random_key":"random_value"
        }
        response = {'random_key': ['Unknown field.']}
        error_message = LotItemSchema().validate(data=args)
        assert error_message == response

    def test_serializer_with_non_required_missing_fields(self):
        args = {
            "name":"create_lot_item",
            "variety":"213",
            "approved_by":"ajay@wilcompute.com",
            "sku_id":"1982",
            "sku_name":"213 1g", 
            "unit":"dry", 
            "lot_item_quantity":1000, 
            "to_room":"propagation"
        }
        response = {}
        error_message = LotItemSchema().validate(data=args)
        assert error_message == response


        