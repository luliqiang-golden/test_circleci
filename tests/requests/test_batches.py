import json
import secrets
from models.inventory import Inventory
from models.user import User
from models.signature import Signature
from models.organization import Organization
from decimal import Decimal
from app import db
from python_scripts.models.activity import Activity
from datetime import datetime, timezone
from tests.requests import AuthenticatedTestCase
from tests.db_scripts.batch import *

class TestBatches(AuthenticatedTestCase):
    organization_id = 0
    created_by_id = 0
    signed_by_id = 0
    activity_id = 0
    approver_id = 0
    recorder_id = 0
    def setUp(self):
        super(TestBatches, self).setUp()

        org_radom_name = "GrowerIQ-"  + str(secrets.token_hex(nbytes=8))
        organizations = Organization(name=org_radom_name, timestamp='2021-01-01 00:00:00', data='{}')
        db.session.add(organizations)
        db.session.commit()
        self.organization_id = organizations.id
        
        created_by = User(organization_id=self.organization_id, name="Created By", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='creator@wilcompute.com')
        db.session.add(created_by)
        db.session.commit()
        self.created_by_id = created_by.id
        self.signed_by_id  = created_by.id
        
        approver = User(organization_id=self.organization_id, name="Approver", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='approver@wilcompute.com')
        db.session.add(approver)
        db.session.flush()
        self.approver_id = approver.id

        recorder = User(organization_id=self.organization_id, name="Recorder", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='recorder@wilcompute.com')
        db.session.add(recorder)
        db.session.commit()
        self.recorder_id = recorder.id
        
        activity = Activity(organization_id=self.organization_id,created_by=approver.id, timestamp='2021-07-27 15:17:00',name='signature',data='{}')
        db.session.add(activity)
        db.session.commit()
        self.activity_id = activity.id
        
    def test_post_germination_seeds(self):
        initial_stats = { "seeds": 150.0 }
        inventory = Inventory(organization_id=self.organization_id, name='candies', created_by=self.created_by_id, variety="Candyland" , stats=initial_stats, type='batch', timestamp='2021-07-27 15:17:00', attributes={'room': 'Propagation Room', 'stage': 'germinating', 'test_status': '', 'seeds_weight': 30, 'seed_weight': 0.2})
        db.session.add(inventory)
        db.session.commit()
        inventory_id = inventory.id
        params = {
                "approved_by": "approver@wilcompute.com",
                "recorded_by": "recorder@wilcompute.com",
                "scale_name": "",
                "quantity": 150,
                "timestamp": "2021-07-27 15:17:00",
                }
        response = self.client.post(f'/v1/organizations/{self.organization_id}/batches/{inventory_id}/germinate-seeds', json=params)
        assert response.status_code == 200
        self.assertEqual(Inventory.query.count(), 1)
        inventory = Inventory.query.get(inventory_id)
        assert inventory.stats == {'seeds': 0, 'plants': 150 }
        assert inventory.attributes == {'room': 'Propagation Room', 'stage': 'germinating', 'test_status': "", 'seeds_weight': 30, 'seed_weight': Decimal('0.2')}
        assert Signature.query.count() == 2
        assert Signature.query.with_entities(Signature.field, Signature.signed_by, Signature.created_by).all() == [('Recorded By', self.recorder_id, self.current_user_id), ('Approved By', self.approver_id, self.current_user_id)]


    def test_post_germination_seeds_missing_params(self):
        inventory = Inventory(organization_id=self.organization_id, name='candies', created_by=self.created_by_id, variety="Candyland", stats={'seeds': 150}, type='batch', attributes={'room': 'Propagation Room', 'stage': 'germinating', 'test_status': '', 'seeds_weight': 0.3})
        db.session.add(inventory)
        db.session.commit()
        params = {
                "scale_name": "",
                "quantity": 150,
                "timestamp": "2021-07-27 15:17:00",
                }
        response = self.client.post(f'/v1/organizations/{self.organization_id}/batches/{inventory.id}/germinate-seeds', json=params)
        self.assertEqual(response.status_code, 400)

    def test_post_germination_seeds_missing_batch(self):
        params = {
                "approved_by": "approver@wilcompute.com",
                "recorded_by": "recorder@wilcompute.com",
                "scale_name": "",
                "quantity": 150,
                "timestamp": "2021-07-27 15:17:00",
                }
        response = self.client.post('/v1/organizations/1/batches/9999/germinate-seeds', json=params)
        self.assertEqual(response.status_code, 404)

    def test_post_germination_seeds_with_more_germination_than_seeds(self):
        inventory = Inventory(organization_id=self.organization_id, name='candies', created_by=self.created_by_id, variety="Candyland", stats={'seeds': 150}, type='batch', attributes={'room': 'Propagation Room', 'stage': 'germinating', 'test_status': '', 'seeds_weight': 0.3, 'seed_weight': 0.2})
        db.session.add(inventory)
        db.session.commit()
        params = {
                "approved_by": "approver@wilcompute.com",
                "recorded_by": "recorder@wilcompute.com",
                "scale_name": "",
                "quantity": 200,
                "timestamp": "2021-07-27 15:17:00",
                }
        response = self.client.post(f'/v1/organizations/{self.organization_id}/batches/{inventory.id}/germinate-seeds', json=params)
        self.assertEqual(response.status_code, 403)

    def test_post_germination_seeds_with_in_a_wrong_stage(self):
        inventory = Inventory(organization_id=self.organization_id, name='candies', created_by=self.created_by_id, variety="Candyland", stats={'seeds': 150}, type='batch', timestamp='2021-07-27 15:17:00', attributes={'room': 'Propagation Room', 'stage': 'planning', 'test_status': '', 'seeds_weight': 0.3, 'seed_weight': 0.2})
        db.session.add(inventory)
        db.session.commit()
        params = {
                "approved_by": "approver@wilcompute.com",
                "recorded_by": "recorder@wilcompute.com",
                "scale_name": "",
                "quantity": 150,
                "timestamp": "2021-07-27 15:17:00",
                }
        response = self.client.post(f'/v1/organizations/{self.organization_id}/batches/{inventory.id}/germinate-seeds', json=params)
        self.assertEqual(response.status_code, 403)

    def test_post_multiple_harvest_plants(self):
        
        db.session.execute(multiple_harvest_data_post)
        
        payload = {
                    "plants_harvested": 500,
                    "harvested_quantity": 50000,
                    "weighed_by": "current@wilcompute.com",
                    "checked_by": "current@wilcompute.com",
                    "approved_by": "current@wilcompute.com",
                    "scale_name": ""
                }

        response = self.client.post('/v1/organizations/1/batches/35919/harvest_multiple', json=payload)

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('attributes').get("stage"), "harvesting")
        self.assertEqual(response_body.get('data').get("plan").get("end_type"), "cured")
        self.assertEqual(response_body.get('data').get("plan").get("start_type"), "plants")
        self.assertEqual(response_body.get('data').get("variety_id"), 51)
        self.assertEqual(response_body.get('is_child'), True)
        self.assertEqual(response_body.get('is_parent'), False)
        self.assertEqual(response_body.get('parent_id'), 35919)
        self.assertIn(' - child', response_body.get('name'))
        self.assertEqual(response_body.get('stats').get("g-wet"), 50000)

    def test_post_harvest_whole_plants(self):
        
        db.session.execute(multiple_harvest_data_post)
        
        payload = {
                    "harvested_quantity": 100000,
                    "weighed_by": "current@wilcompute.com",
                    "checked_by": "current@wilcompute.com",
                    "approved_by": "current@wilcompute.com",
                    "scale_name": ""
                }

        response = self.client.post('/v1/organizations/1/batches/35920/harvest_whole_plant', json=payload)

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('attributes').get("stage"), "harvesting")
        self.assertEqual(response_body.get('data').get("plan").get("end_type"), "cured")
        self.assertEqual(response_body.get('data').get("plan").get("start_type"), "plants")
        self.assertEqual(response_body.get('data').get("variety_id"), 51)
        self.assertEqual(response_body.get('is_child'), False)
        self.assertEqual(response_body.get('is_parent'), False)
        self.assertEqual(response_body.get('parent_id'), None)
        self.assertNotIn(response_body.get('name'), ' - child')
        self.assertEqual(response_body.get('stats').get("g-wet"), 100000)
    
    def test_get_related_child_batches_multiple_harvest(self):
        
        db.session.execute(multiple_harvest_data_get)

        response = self.client.get('/v1/organizations/1/batches/35919/harvest_multiple')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body[0].get('parent_id'), 35919)
        self.assertEqual(response_body[1].get('parent_id'), 35919)
        self.assertEqual(response_body[0].get('is_child'), True)
        self.assertEqual(response_body[1].get('is_child'), True)
    
    def test_post_merge_multiple_harvest(self):
        
        db.session.execute(merge_multiple_harvest_data_post)
        
        payload = {
            "child_batches_ids": [36011, 36012, 36013],
            "approved_by": "current@wilcompute.com",
            "recorded_by": "current@wilcompute.com"
        }

        response = self.client.post('/v1/organizations/1/batches/36010/merge_harvest_multiple', json=payload)

        response_body = json.loads(response.data)
        
        child_1 = Inventory.query.filter(Inventory.id == 36011).one_or_none()
        child_2 = Inventory.query.filter(Inventory.id == 36012).one_or_none()
        child_3 = Inventory.query.filter(Inventory.id == 36013).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('name'), 'Afghan Kush-36-22')
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(response_body.get('data').get('plan').get('end_type'), 'dry')
        self.assertEqual(response_body.get('stats').get('g-wet'), 10000)
        self.assertEqual(response_body.get('attributes').get('stage'), 'harvesting')
        self.assertEqual(child_1.stats.get('g-wet'), 0)
        self.assertEqual(child_2.stats.get('g-wet'), 0)
        self.assertEqual(child_3.stats.get('g-wet'), 0)
        
    def test_post_merge_multiple_harvest(self):
        
        db.session.execute(merge_multiple_harvest_data_post)
        
        payload = {
            "child_batches_ids": [36011, 36012, 36013],
            "approved_by": "current@wilcompute.com",
            "recorded_by": "current@wilcompute.com"
        }

        response = self.client.post('/v1/organizations/1/batches/36010/merge_harvest_multiple', json=payload)

        response_body = json.loads(response.data)
        
        child_1 = Inventory.query.filter(Inventory.id == 36011).one_or_none()
        child_2 = Inventory.query.filter(Inventory.id == 36012).one_or_none()
        child_3 = Inventory.query.filter(Inventory.id == 36013).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('name'), 'Afghan Kush-36-22')
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(response_body.get('data').get('plan').get('end_type'), 'dry')
        self.assertEqual(response_body.get('stats').get('g-wet'), 10000)
        self.assertEqual(response_body.get('attributes').get('stage'), 'harvesting')
        self.assertEqual(child_1.stats.get('g-wet'), 0)
        self.assertEqual(child_2.stats.get('g-wet'), 0)
        self.assertEqual(child_3.stats.get('g-wet'), 0)
    
    def test_post_merge_multiple_harvest_different_stages(self):
        
        db.session.execute(merge_multiple_harvest_data_post_different_stages)

        try:
            payload = {
            "child_batches_ids": [36016, 36017, 36018],
            "approved_by": "current@wilcompute.com",
            "recorded_by": "current@wilcompute.com"
            }
            response = self.client.post('/v1/organizations/1/batches/36015/merge_harvest_multiple', json=payload)
            assert response.status_code == 200
        except(Exception) as exception:
            self.assertEqual(exception.status_code, 400)
            self.assertEqual(exception.error['message'], 'Inventories should be in the same stage to merge batches')

    def test_post_merge_multiple_harvest_different_types(self):
        
        db.session.execute(merge_multiple_harvest_data_post_different_types)

        try:
            payload = {
            "child_batches_ids": [36016, 36017, 36018],
            "approved_by": "current@wilcompute.com",
            "recorded_by": "current@wilcompute.com"
            }
            response = self.client.post('/v1/organizations/1/batches/36015/merge_harvest_multiple', json=payload)
            assert response.status_code == 200
        except(Exception) as exception:
            self.assertEqual(exception.status_code, 400)
            self.assertEqual(exception.error['message'], 'Inventories should be of the same type to merge batches')

    def test_post_merge_multiple_harvest_invalid_source_id(self):
        
        db.session.execute(merge_multiple_harvest_data_post)

        try:
            payload = {
            "child_batches_ids": [36012, 36013],
            "approved_by": "current@wilcompute.com",
            "recorded_by": "current@wilcompute.com"
            }
            response = self.client.post('/v1/organizations/1/batches/36011/merge_harvest_multiple', json=payload)
            assert response.status_code == 200
        except(Exception) as exception:
            self.assertEqual(exception.status_code, 400)
            self.assertEqual(exception.error['message'], 'Source inventory is not a parent')

    def test_put_weight_adjustment_wet_partial_harvest(self):
        
        db.session.execute(weight_adjustment_wet_partial_harvest)
        
        payload = {
            "adjusted_weight": 200,
            "reason_for_modification": "test",
            "approved_by": "current@wilcompute.com",
            "checked_by": "current@wilcompute.com"
        }

        response = self.client.put('/v1/organizations/1/batches/36047/weight_adjustment', json=payload)

        response_body = json.loads(response.data)
        
        original_activity = (Activity.query
                             .filter(Activity.id == 71157)
                             .one_or_none())
        
        inventory_adjustment_activity = (Activity.query
                                        .filter(Activity.id == 71159)
                                        .one_or_none())
        
        weight_adjustment_activity = Activity.query.filter(Activity.name == 'weight_adjustment').one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('stats').get('g-wet'), 200.0)
        self.assertEqual(response_body.get('is_child'), True)
        self.assertEqual(response_body.get('parent_id'), 36046)
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(original_activity.data.get('to_qty'), 200.0)
        self.assertEqual(original_activity.data.get('description'), 'Child batch created: ID 36047. Harvested weight: 200.0g.')
        self.assertEqual(inventory_adjustment_activity.data.get('quantity'), 200.0)
        self.assertEqual(weight_adjustment_activity.data.get('description'), 'From: 100g wet to: 200.0g')
    
    def test_put_weight_adjustment_wet(self):
        
        db.session.execute(weight_adjustment_wet)
        
        payload = {
            "adjusted_weight": 200,
            "reason_for_modification": "test",
            "approved_by": "current@wilcompute.com",
            "checked_by": "current@wilcompute.com"
        }

        response = self.client.put('/v1/organizations/1/batches/36049/weight_adjustment', json=payload)

        response_body = json.loads(response.data)
        
        original_activity = (Activity.query
                             .filter(Activity.id == 71185)
                             .one_or_none())
        
        inventory_adjustment_activity = (Activity.query
                                        .filter(Activity.id == 71187)
                                        .one_or_none())
        
        weight_adjustment_activity = Activity.query.filter(Activity.name == 'weight_adjustment').one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('stats').get('g-wet'), 200.0)
        self.assertEqual(response_body.get('is_child'), False)
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(original_activity.data.get('to_qty'), 200.0)
        self.assertEqual(original_activity.data.get('description'), 'All plants harvested. Harvested weight: 200.0g')
        self.assertEqual(inventory_adjustment_activity.data.get('quantity'), 200.0)
        self.assertEqual(weight_adjustment_activity.data.get('description'), 'From: 1000g wet to: 200.0g')
    
    def test_put_weight_adjustment_dry(self):
        
        db.session.execute(weight_adjustment_dry)
        
        payload = {
            "adjusted_weight": 200,
            "reason_for_modification": "test",
            "approved_by": "current@wilcompute.com",
            "checked_by": "current@wilcompute.com"
        }

        response = self.client.put('/v1/organizations/1/batches/36049/weight_adjustment', json=payload)

        response_body = json.loads(response.data)
        
        original_activity = (Activity.query
                             .filter(Activity.id == 71192)
                             .one_or_none())
        
        inventory_adjustment_activity = (Activity.query
                                        .filter(Activity.id == 71194)
                                        .one_or_none())
        
        weight_adjustment_activity = Activity.query.filter(Activity.name == 'weight_adjustment').one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('stats').get('g-dry').get('dry'), 200.0)
        self.assertEqual(response_body.get('is_child'), False)
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(original_activity.data.get('to_qty'), 200.0)
        self.assertEqual(inventory_adjustment_activity.data.get('quantity'), 200.0)
        self.assertEqual(weight_adjustment_activity.data.get('description'), 'From: 800.0g dry to: 200.0g')
    
    def test_put_weight_adjustment_cured(self):
        
        db.session.execute(weight_adjustment_cured)
        
        payload = {
            "adjusted_weight": 200,
            "reason_for_modification": "test",
            "approved_by": "current@wilcompute.com",
            "checked_by": "current@wilcompute.com"
        }

        response = self.client.put('/v1/organizations/1/batches/36051/weight_adjustment', json=payload)

        response_body = json.loads(response.data)
        
        original_activity = (Activity.query
                             .filter(Activity.id == 71227)
                             .one_or_none())
        
        inventory_adjustment_activity = (Activity.query
                                        .filter(Activity.id == 71229)
                                        .one_or_none())
        
        weight_adjustment_activity = Activity.query.filter(Activity.name == 'weight_adjustment').one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('stats').get('g-dry').get('cured'), 200.0)
        self.assertEqual(response_body.get('is_child'), False)
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(original_activity.data.get('to_qty'), 200.0)
        self.assertEqual(inventory_adjustment_activity.data.get('quantity'), 200.0)
        self.assertEqual(weight_adjustment_activity.data.get('description'), 'From: 800.0g cured to: 200.0g')
    
    def test_put_weight_adjustment_crude(self):
        
        db.session.execute(weight_adjustment_crude)
        
        payload = {
            "adjusted_weight": 200,
            "reason_for_modification": "test",
            "approved_by": "current@wilcompute.com",
            "checked_by": "current@wilcompute.com"
        }

        response = self.client.put('/v1/organizations/1/batches/36053/weight_adjustment', json=payload)

        response_body = json.loads(response.data)
        
        original_activity = (Activity.query
                             .filter(Activity.id == 71251)
                             .one_or_none())
        
        inventory_adjustment_activity = (Activity.query
                                        .filter(Activity.id == 71253)
                                        .one_or_none())
        
        weight_adjustment_activity = Activity.query.filter(Activity.name == 'weight_adjustment').one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('stats').get('g-oil').get('crude'), 200.0)
        self.assertEqual(response_body.get('is_child'), False)
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(original_activity.data.get('to_qty'), 200.0)
        self.assertEqual(inventory_adjustment_activity.data.get('quantity'), 200.0)
        self.assertEqual(weight_adjustment_activity.data.get('description'), 'From: 900.0g crude to: 200.0g')
    
    def test_put_weight_adjustment_distilled(self):
        
        db.session.execute(weight_adjustment_distilled)
        
        payload = {
            "adjusted_weight": 200,
            "reason_for_modification": "test",
            "approved_by": "current@wilcompute.com",
            "checked_by": "current@wilcompute.com"
        }

        response = self.client.put('/v1/organizations/1/batches/36053/weight_adjustment', json=payload)

        response_body = json.loads(response.data)
        
        original_activity = (Activity.query
                             .filter(Activity.id == 71257)
                             .one_or_none())
        
        inventory_adjustment_activity = (Activity.query
                                        .filter(Activity.id == 71259)
                                        .one_or_none())
        
        weight_adjustment_activity = Activity.query.filter(Activity.name == 'weight_adjustment').one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('stats').get('g-oil').get('distilled'), 200.0)
        self.assertEqual(response_body.get('is_child'), False)
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(original_activity.data.get('to_qty'), 200.0)
        self.assertEqual(inventory_adjustment_activity.data.get('quantity'), 200.0)
        self.assertEqual(weight_adjustment_activity.data.get('description'), 'From: 800.0g distilled to: 200.0g')
    
    def test_put_weight_adjustment_twice_in_row(self):
        
        db.session.execute(weight_adjustment_distilled)
        
        payload = {
            "adjusted_weight": 200,
            "reason_for_modification": "test",
            "approved_by": "current@wilcompute.com",
            "checked_by": "current@wilcompute.com"
        }

        response = self.client.put('/v1/organizations/1/batches/36053/weight_adjustment', json=payload)
        
        payload = {
            "adjusted_weight": 100,
            "reason_for_modification": "test",
            "approved_by": "current@wilcompute.com",
            "checked_by": "current@wilcompute.com"
        }

        response = self.client.put('/v1/organizations/1/batches/36053/weight_adjustment', json=payload)

        response_body = json.loads(response.data)
        
        original_activity = (Activity.query
                             .filter(Activity.id == 71257)
                             .one_or_none())
        
        inventory_adjustment_activity = (Activity.query
                                        .filter(Activity.id == 71259)
                                        .one_or_none())
        
        weight_adjustment_activity = Activity.query.filter(Activity.name == 'weight_adjustment').order_by(Activity.timestamp.desc()).first()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('stats').get('g-oil').get('distilled'), 100.0)
        self.assertEqual(response_body.get('is_child'), False)
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(original_activity.data.get('to_qty'), 100.0)
        self.assertEqual(inventory_adjustment_activity.data.get('quantity'), 100.0)
        self.assertEqual(weight_adjustment_activity.data.get('description'), 'From: 200.0g distilled to: 100.0g')
    
    def test_put_weight_adjustment_invalid_stage_or_activity(self):
        
        db.session.execute(weight_adjustment_invalid_stage_or_activity)

        try:

            payload = {
                "adjusted_weight": 200,
                "reason_for_modification": "test",
                "approved_by": "current@wilcompute.com",
                "checked_by": "current@wilcompute.com"
            }

            response = self.client.put('/v1/organizations/1/batches/36055/weight_adjustment', json=payload)

            assert response.status_code == 200

        except(Exception) as exception:

            self.assertEqual(exception.status_code, 400)

            self.assertEqual(exception.error['message'], '''Batch doesn't have one of the allowed activities. Batch should have at least of the following: ['batch_record_bud_harvest_weight', 'batch_record_harvest_weight', 'batch_record_dry_weight', 'batch_record_cured_weight', 'batch_record_crude_oil_weight', 'batch_record_distilled_oil_weight', 'batch_record_harvest_weight_partially']''')
    
    def test_put_weight_adjustment_invalid_inventory_type(self):
        
        db.session.execute(weight_adjustment_invalid_inventory_type)

        try:

            payload = {
                "adjusted_weight": 200,
                "reason_for_modification": "test",
                "approved_by": "current@wilcompute.com",
                "checked_by": "current@wilcompute.com"
            }

            response = self.client.put('/v1/organizations/1/batches/36054/weight_adjustment', json=payload)

            assert response.status_code == 200

        except(Exception) as exception:

            self.assertEqual(exception.status_code, 400)

            self.assertEqual(exception.error['message'], '''Inventory must be a batch''')
    
    def test_put_weight_adjustment_invalid_stage_valid_activity_in_activity_log(self):
        
        db.session.execute(weight_adjustment_invalid_stage_valid_activity_in_activity_log)

        try:

            payload = {
                "adjusted_weight": 200,
                "reason_for_modification": "test",
                "approved_by": "current@wilcompute.com",
                "checked_by": "current@wilcompute.com"
            }

            response = self.client.put('/v1/organizations/1/batches/36057/weight_adjustment', json=payload)

            assert response.status_code == 200

        except(Exception) as exception:

            self.assertEqual(exception.status_code, 400)

            self.assertEqual(exception.error['message'], '''Inventory must be in one of the following stages: ['g-wet', 'dry', 'cured', 'crude', 'distilled']''')
    
    def test_post_merge_multiple_harvest_archived_source(self):
        
        db.session.execute(merge_multiple_harvest_data_post_archived_source)
        
        payload = {
            "child_batches_ids": [35869, 35870],
            "approved_by": "current@wilcompute.com",
            "recorded_by": "current@wilcompute.com"
        }

        response = self.client.post('/v1/organizations/1/batches/35868/merge_harvest_multiple', json=payload)

        response_body = json.loads(response.data)
        
        child_1 = Inventory.query.filter(Inventory.id == 35869).one_or_none()
        child_2 = Inventory.query.filter(Inventory.id == 35870).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('name'), 'Afghan Kush-39-22')
        self.assertEqual(response_body.get('type'), 'batch')
        self.assertEqual(response_body.get('data').get('plan').get('end_type'), 'dry')
        self.assertEqual(response_body.get('stats').get('g-wet'), 2000.0)
        self.assertEqual(response_body.get('attributes').get('stage'), 'harvesting')
        self.assertEqual(child_1.stats.get('g-wet'), 0)
        self.assertEqual(child_2.stats.get('g-wet'), 0)
        