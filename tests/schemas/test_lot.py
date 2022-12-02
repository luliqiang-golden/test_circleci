from flask import request, jsonify
from tests.requests import AuthenticatedTestCase
from serializer.lot import LotSchema

class TestLotSchema(AuthenticatedTestCase):

    def test_serializer_with_correct_data(self):
        args = {
            "name":"create_lot",
            "scale_name":"office",
            "lot_name":"czxczcz",
            "to_room":"Propagation Room",
            "variety":"213",
            "variety_id":444,
            "from_qty":10,
            "from_qty_unit":"dry",
            "to_qty":10,
            "to_qty_unit":"dry",
            "approved_by":"ajay@wilcompute.com",
            "checked_by":"ajay@wilcompute.com",
            "weighed_by":"ajay@wilcompute.com",
            "from_inventory_id":1,
            "inventory_type":"received-inventory",
            "timestamp":"2022-01-01 00:00:00"
          }
        response = {}
        error_message = LotSchema().validate(data=args)
        assert error_message == response


    def test_serializer_with_required_missing_fields(self):
        args = {
            "scale_name":"office",
            "lot_name":"czxczcz",
            "to_room":"Propagation Room",
            "variety":"213",
            "variety_id":444,
            "from_qty":10,
            "from_qty_unit":"dry",
            "to_qty":10,
            "to_qty_unit":"dry",
            "approved_by":"ajay@wilcompute.com",
            "checked_by":"ajay@wilcompute.com",
            "weighed_by":"ajay@wilcompute.com",
            "from_inventory_id":1,
            "inventory_type":"received-inventory",
            "timestamp": "2022-01-01 00:00:00"
          }
        response = {'name': ['Missing data for required field.']}
        error_message = LotSchema().validate(data=args)
        assert error_message == response

    def test_serializer_with_non_required_missing_fields(self):
        args = {
            "name":"create_lot",
            "scale_name":"office",
            "to_room":"Propagation Room",
            "variety":"213",
            "variety_id":444,
            "from_qty":10,
            "from_qty_unit":"dry",
            "to_qty":10,
            "to_qty_unit":"dry",
            "approved_by":"ajay@wilcompute.com",
            "checked_by":"ajay@wilcompute.com",
            "weighed_by":"ajay@wilcompute.com",
            "from_inventory_id":1,
            "inventory_type":"received-inventory",
            "timestamp": "2022-01-01 00:00:00"
          }
        response = {}
        error_message = LotSchema().validate(data=args)
        assert error_message == response


    def test_serializer_with_unknown_field(self):
        args = {
            "name":"create_lot",
            "scale_name":"office",
            "lot_name":"czxczcz",
            "to_room":"Propagation Room",
            "variety":"213",
            "variety_id":444,
            "from_qty":10,
            "from_qty_unit":"dry",
            "to_qty":10,
            "to_qty_unit":"dry",
            "approved_by":"ajay@wilcompute.com",
            "checked_by":"ajay@wilcompute.com",
            "weighed_by":"ajay@wilcompute.com",
            "from_inventory_id":1,
            "inventory_type":"received-inventory",
            "random_key": "random_value",
            "timestamp": "2022-01-01 00:00:00"
          }
        response = {'random_key': ['Unknown field.']}
        error_message = LotSchema().validate(data=args)
        assert error_message == response

    def test_validation_for_email_fields(self):
        args = {
            "name":"create_lot",
            "scale_name":"office",
            "lot_name":"czxczcz",
            "to_room":"Propagation Room",
            "variety":"213",
            "variety_id":444,
            "from_qty":10,
            "from_qty_unit":"dry",
            "to_qty":10,
            "to_qty_unit":"dry",
            "approved_by":"AJ",
            "checked_by":"ajay@wilcompute.com",
            "weighed_by":"ajay@wilcompute.com",
            "from_inventory_id":1,
            "inventory_type":"received-inventory",
            "timestamp":"2022-01-01 00:00:00"
          }
        response = {'approved_by': ["Not a valid email address."]}
        error_message = LotSchema().validate(data=args)
        assert error_message == response
          