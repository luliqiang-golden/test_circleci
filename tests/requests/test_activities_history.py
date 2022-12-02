import json
from decimal import Decimal
from models.activities_history import ActivitiesHistory
from models.inventory import Inventory
from tests import TestCase
from tests.requests import AuthenticatedTestCase
from flask import jsonify
from app import db

class TestActivitiesHistory(AuthenticatedTestCase):
    
    def setUp(self):
        TestCase.tearDown(self)
        super(TestActivitiesHistory, self).setUp()
        
        activity = ActivitiesHistory(
            organization_id = '1',
            changed_by = 1,
            changed_at  = '2022-06-15 16:12:47.473 -0300',
            name = 'split_batch',
            action = 'UPDATE',
            old_data = {"to_qty": 5.0, "from_qty": 5.0, "scale_name": "", "to_qty_unit": "g-wet", "from_qty_unit": "g-wet", "to_inventory_id": 35930, "from_inventory_id": 35928},
            new_data = {"to_qty": 20.0, "from_qty": 20.0, "scale_name": "", "to_qty_unit": "g-wet", "from_qty_unit": "g-wet", "to_inventory_id": 35930, "from_inventory_id": 35928},
            old_timestamp = '2022-06-15 16:11:47.249 -0300',
            new_timestamp = '2022-06-15 16:11:47.249 -0300',
            reason_for_modification = 'test update',
            activity_id = 69818
        )

        db.session.add(activity)
        db.session.commit()
        
        
        
        activity = ActivitiesHistory(
            organization_id = '1',
            changed_by = 1,
            changed_at  = '2022-06-15 16:12:47.487 -0300',
            name = 'inventory_adjustment',
            action = 'UPDATE',
            old_data = {"unit": "g-wet", "quantity": 846508.0, "inventory_id": 35928, "activity_name": "split_batch", "invetory_type": "batch"},
            new_data = {"unit": "g-wet", "quantity": 846493.0, "inventory_id": 35928, "activity_name": "split_batch", "invetory_type": "batch"},
            old_timestamp = '2022-06-15 16:11:47.272 -0300',
            new_timestamp = '2022-06-15 16:11:47.272 -0300',
            reason_for_modification = 'test update',
            activity_id = 69821
        )

        db.session.add(activity)
        db.session.commit()
        
        
        
        
        activity = ActivitiesHistory(
            organization_id = '1',
            changed_by = 1,
            changed_at  = '2022-06-15 16:12:47.509 -0300',
            name = 'inventory_adjustment',
            action = 'UPDATE',
            old_data = {"unit": "g-wet", "quantity": 5.0, "inventory_id": 35930, "activity_name": "split_batch", "invetory_type": "batch"},
            new_data = {"unit": "g-wet", "quantity": 20.0, "inventory_id": 35930, "activity_name": "split_batch", "invetory_type": "batch"},
            old_timestamp = '2022-06-15 16:11:47.284 -0300',
            new_timestamp = '2022-06-15 16:11:47.284 -0300',
            reason_for_modification = 'test update',
            activity_id = 69822
        )

        db.session.add(activity)
        db.session.commit()




        activity = ActivitiesHistory(
            organization_id = '1',
            changed_by = 1,
            changed_at  = '2022-06-15 16:12:47.520 -0300',
            name = 'batch_plan_update',
            action = 'UPDATE',
            old_data = {"plan": {"end_type": "g-wet", "timeline": [{"name": "planning", "planned_length": None}, {"name": "germinating", "planned_length": None}, {"name": "propagation", "planned_length": None}, {"name": "vegetation", "planned_length": None}, {"name": "flowering", "planned_length": None}, {"name": "harvesting", "planned_length": None}, {"name": "qa", "planned_length": None}], "start_date": "2022-06-15T03:00:00.000Z", "start_type": "seeds"}, "inventory_id": 35930},
            new_data = {"plan": {"end_type": "g-wet", "timeline": [{"name": "planning", "planned_length": None}, {"name": "germinating", "planned_length": None}, {"name": "propagation", "planned_length": None}, {"name": "vegetation", "planned_length": None}, {"name": "flowering", "planned_length": None}, {"name": "harvesting", "planned_length": None}, {"name": "qa", "planned_length": None}], "start_date": "2022-06-15T03:00:00.000Z", "start_type": "seeds"}, "inventory_id": 35930},
            old_timestamp = '2022-06-15 16:11:47.256 -0300',
            new_timestamp = '2022-06-15 16:11:47.256 -0300',
            reason_for_modification = 'test update',
            activity_id = 69819
        )

        db.session.add(activity)
        db.session.commit()
        
        
        
        
        activity = ActivitiesHistory(
            organization_id = '1',
            changed_by = 1,
            changed_at  = '2022-06-15 16:12:47.534 -0300',
            name = 'update_stage',
            action = 'UPDATE',
            old_data = {"to_stage": "harvesting", "inventory_id": 35930},
            new_data = {"to_stage": "harvesting", "inventory_id": 35930},
            old_timestamp = '2022-06-15 16:11:47.267 -0300',
            new_timestamp = '2022-06-15 16:11:47.267 -0300',
            reason_for_modification = 'test update',
            activity_id = 69820
        )

        db.session.add(activity)
        db.session.commit()
        
        
        
        
        
        activity = ActivitiesHistory(
            organization_id = '1',
            changed_by = 1,
            changed_at  = '2022-06-15 16:12:47.543 -0300',
            name = 'create_signature',
            action = 'UPDATE',
            old_data = {"field": "prepared by", "signed_by": 34, "activity_id": 69818, "signature_id": 116},
            new_data = {"field": "prepared by", "signed_by": 34, "activity_id": 69818, "signature_id": 116},
            old_timestamp = '2022-06-15 16:11:47.297 -0300',
            new_timestamp = '2022-06-15 16:11:47.297 -0300',
            reason_for_modification = 'test update',
            activity_id = 69823
        )

        db.session.add(activity)
        db.session.commit()
        
        
        
        
        
        activity = ActivitiesHistory(
            organization_id = '1',
            changed_by = 1,
            changed_at  = '2022-06-15 16:12:47.555 -0300',
            name = 'create_signature',
            action = 'UPDATE',
            old_data = {"field": "reviewed by", "signed_by": 34, "activity_id": 69818, "signature_id": 117},
            new_data = {"field": "reviewed by", "signed_by": 34, "activity_id": 69818, "signature_id": 117},
            old_timestamp = '2022-06-15 16:11:47.304 -0300',
            new_timestamp = '2022-06-15 16:11:47.304 -0300',
            reason_for_modification = 'test update',
            activity_id = 69824
        )

        db.session.add(activity)
        db.session.commit()
        
        
        
        
        
        activity = ActivitiesHistory(
            organization_id = '1',
            changed_by = 1,
            changed_at  = '2022-06-15 16:12:47.565 -0300',
            name = 'create_signature',
            action = 'UPDATE',
            old_data = {"field": "approved by", "signed_by": 34, "activity_id": 69818, "signature_id": 118},
            new_data = {"field": "approved by", "signed_by": 34, "activity_id": 69818, "signature_id": 118},
            old_timestamp = '2022-06-15 16:11:47.315 -0300',
            new_timestamp = '2022-06-15 16:11:47.315 -0300',
            reason_for_modification = 'test update',
            activity_id = 69825
        )

        db.session.add(activity)
        db.session.commit()
        
        
        
        
        
    def test_get_activities_history(self):
        
        response = self.client.get(f'/v1/organizations/1/activities_history')
        
        response_body = json.loads(response.data)
        
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 8)
        self.assertEqual(response_body[0].get('name'), 'create_signature')
        self.assertEqual(response_body[1].get('name'), 'create_signature')
        self.assertEqual(response_body[2].get('name'), 'create_signature')
        self.assertEqual(response_body[3].get('name'), 'update_stage')
        self.assertEqual(response_body[4].get('name'), 'batch_plan_update')
        self.assertEqual(response_body[5].get('name'), 'inventory_adjustment')
        self.assertEqual(response_body[6].get('name'), 'inventory_adjustment')
        self.assertEqual(response_body[7].get('name'), 'split_batch')
    
    
    def test_get_activities_history_by_activity_id(self):
        
        response = self.client.get(f'/v1/organizations/1/activities_history/69818')
        
        response_body = json.loads(response.data)
        
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('name'), 'split_batch')
