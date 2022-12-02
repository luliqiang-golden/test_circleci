import datetime
import json
from tests.requests import AuthenticatedTestCase
from models.inventory import Inventory
from models.activity import Activity
from tests.db_scripts.backdate_activity import *
from app import db

class TestBackdateActivity(AuthenticatedTestCase):

    def setUp(self):
        super(TestBackdateActivity, self).setUp()

    def test_backdate_receive_inventory(self):
        
        db.session.execute(backdate_activity_receive_inventory)
        
        payload = {
                    "activity_ids": [70031],
                    "reason_for_modification": "test",
                    "timestamp": "2022-08-10T14:48:00.000Z"
                }

        response = self.client.put('/v1/organizations/1/backdate_activity', json=payload)

        response_body = json.loads(response.data)

        receive_inventory_activity = Activity.query.filter(Activity.id == 70031).one_or_none()
        inventory_adjustment = Activity.query.filter(Activity.id == 70032).one_or_none()
        inventory = Inventory.query.filter(Inventory.id == 35932).one_or_none()
        other_activity = Activity.query.filter(Activity.id == 70033).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('message'), 'success')
        
        self.assertEqual(receive_inventory_activity.timestamp.strftime('%Y-%m-%d'), '2022-08-10')
        self.assertEqual(inventory_adjustment.timestamp.strftime('%Y-%m-%d'), '2022-08-10')
        self.assertEqual(inventory.timestamp.strftime('%Y-%m-%d'), '2022-08-10')
        self.assertEqual(other_activity.timestamp.strftime('%Y-%m-%d'), '2022-08-17')
        
        
    def test_backdate_create_lot(self):
    
        db.session.execute(backdate_activity_create_lot)
        
        payload = {
                    "activity_ids": [70043, 70045],
                    "reason_for_modification": "test",
                    "timestamp": "2022-08-10T14:48:00.000Z"
                }

        response = self.client.put('/v1/organizations/1/backdate_activity', json=payload)

        response_body = json.loads(response.data)

        create_lot_activity = Activity.query.filter(Activity.id == 70043).one_or_none()
        transfer_inventory_activity = Activity.query.filter(Activity.id == 70045).one_or_none()
        inventory_adjustment_1 = Activity.query.filter(Activity.id == 70046).one_or_none()
        inventory_adjustment_2 = Activity.query.filter(Activity.id == 70047).one_or_none()
        lot_inventory = Inventory.query.filter(Inventory.id == 35934).one_or_none()
        other_inventory = Inventory.query.filter(Inventory.id == 35933).one_or_none()
        other_activity = Activity.query.filter(Activity.id == 70037).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('message'), 'success')
        
        self.assertEqual(create_lot_activity.timestamp.strftime('%Y-%m-%d'), '2022-08-10')
        self.assertEqual(transfer_inventory_activity.timestamp.strftime('%Y-%m-%d'), '2022-08-10')
        self.assertEqual(inventory_adjustment_1.timestamp.strftime('%Y-%m-%d'), '2022-08-10')
        self.assertEqual(inventory_adjustment_2.timestamp.strftime('%Y-%m-%d'), '2022-08-10')
        self.assertEqual(lot_inventory.timestamp.strftime('%Y-%m-%d'), '2022-08-10')
        self.assertEqual(other_inventory.timestamp.strftime('%Y-%m-%d'), '2022-08-17')
        self.assertEqual(other_activity.timestamp.strftime('%Y-%m-%d'), '2022-08-17')
        