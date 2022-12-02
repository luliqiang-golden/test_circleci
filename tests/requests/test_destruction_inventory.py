import json
from models.activity import Activity
from tests.requests import AuthenticatedTestCase
from models.inventory import Inventory
from tests.db_scripts.destruction_inventory import *
from app import db
from tests import TestCase

class TestDestructionInventory(AuthenticatedTestCase):

    def setUp(self):
        super(TestDestructionInventory, self).setUp()

    def test_dequeue_destroyed_seeds_to_batch_seeds(self):
        
        db.session.execute(destroyed_seeds_to_batch_seeds)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151556]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151555).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151556).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151556)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151555)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 10.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'seeds')
        
        self.assertEqual(to_inventory.stats['seeds'], 5000.0)
        self.assertEqual(from_inventory.stats['g-wet'], 0.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'destruction inventory')

    def test_dequeue_destroyed_seeds_to_batch_vegetative_plants(self):
        
        db.session.execute(destroyed_seeds_to_batch_vegetative_plant)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151559]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151558).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151559).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151559)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151558)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 10.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'seeds')
        
        self.assertEqual(to_inventory.stats['plants'], 4000.0)
        self.assertEqual(from_inventory.stats['seeds'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_seeds_to_batch_whole_plants(self):
        
        db.session.execute(destroyed_seeds_to_batch_whole_plant)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151562]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)

        to_inventory = Inventory.query.filter(Inventory.id == 151561).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151562).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151562)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151561)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 10.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'seeds')
        
        self.assertEqual(to_inventory.stats['plants'], 4000.0)
        self.assertEqual(from_inventory.stats['seeds'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_seeds_to_batch_g_wet(self):
        
        db.session.execute(destroyed_seeds_to_batch_g_wet)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151565]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)

        to_inventory = Inventory.query.filter(Inventory.id == 151564).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151565).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151565)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151564)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 10.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'seeds')
        
        self.assertEqual(to_inventory.stats['g-wet'], 40000.0)
        self.assertEqual(from_inventory.stats['seeds'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_seeds_to_batch_dry(self):
        
        db.session.execute(destroyed_seeds_to_batch_oil)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151571]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151570).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151571).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151571)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151570)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 10.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'seeds')
        
        self.assertEqual(to_inventory.stats['g-oil']['crude'], 10000.0)
        self.assertEqual(from_inventory.stats['seeds'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_vegetative_plants_to_vegetative_plants_batch(self):
        
        db.session.execute(destroyed_vegetative_plants_to_batch_vegetative_plants)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151574]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151573).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151574).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151574)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151573)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'plants')
        
        self.assertEqual(to_inventory.stats['plants'], 5000.0)
        self.assertEqual(from_inventory.stats['g-wet'], 0.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'destruction inventory')

    def test_dequeue_destroyed_vegetative_plants_to_whole_plants_batch(self):
        
        db.session.execute(destroyed_vegetative_plants_to_batch_whole_plants)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151577]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151576).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151577).one_or_none()
        update_stage_activity = (Activity.query
                                 .filter(Activity.data['inventory_id'].astext == str(151576))
                                 .filter(Activity.data['to_stage'].astext == 'flowering')
                                 .filter(Activity.data['unit'].astext == 'plants')
                                 .one_or_none())

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151577)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151576)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'plants')
        
        self.assertEqual(to_inventory.stats['plants'], 5000.0)
        self.assertEqual(from_inventory.stats['g-wet'], 0.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'destruction inventory')
        
        self.assertEqual(update_stage_activity.data['qty'], 5000)

    def test_dequeue_destroyed_vegetative_plants_to_g_wet_batch(self):
        
        db.session.execute(destroyed_vegetative_plants_to_batch_g_wet)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151580]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151579).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151580).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151580)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151579)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'plants')
        
        self.assertEqual(to_inventory.stats['g-wet'], 40000.0)
        self.assertEqual(from_inventory.stats['plants'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_vegetative_plants_to_dry_batch(self):
        
        db.session.execute(destroyed_vegetative_plants_to_batch_dry)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151583]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151582).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151583).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151583)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151582)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'plants')
        
        self.assertEqual(to_inventory.stats['g-dry']['dry'], 20000.0)
        self.assertEqual(from_inventory.stats['plants'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_vegetative_plants_to_oil_batch(self):
        
        db.session.execute(destroyed_vegetative_plants_to_batch_oil)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151586]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151585).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151586).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151586)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151585)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'plants')
        
        self.assertEqual(to_inventory.stats['g-oil']['crude'], 10000.0)
        self.assertEqual(from_inventory.stats['plants'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_whole_plants_to_whole_plants_batch(self):
        
        db.session.execute(destroyed_whole_plants_to_batch_whole_plants)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151589]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)

        to_inventory = Inventory.query.filter(Inventory.id == 151588).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151589).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151589)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151588)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'plants')

        self.assertEqual(to_inventory.stats['plants'], 5000.0)
        self.assertEqual(from_inventory.stats['g-wet'], 0.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'destruction inventory')

    def test_dequeue_destroyed_whole_plants_to_g_wet_batch(self):
        
        db.session.execute(destroyed_whole_plants_to_batch_g_wet)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151592]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151591).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151592).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151592)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151591)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'plants')
        
        self.assertEqual(to_inventory.stats['g-wet'], 40000.0)
        self.assertEqual(from_inventory.stats['plants'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_whole_plants_to_dry_batch(self):
        
        db.session.execute(destroyed_whole_plants_to_batch_dry)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151595]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151594).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151595).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151595)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151594)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'plants')
        
        self.assertEqual(to_inventory.stats['g-dry']['dry'], 20000.0)
        self.assertEqual(from_inventory.stats['plants'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_whole_plants_to_oil_batch(self):
        
        db.session.execute(destroyed_whole_plants_to_batch_oil)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151598]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151597).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151598).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151598)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151597)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'plants')
        
        self.assertEqual(to_inventory.stats['g-oil']['crude'], 10000.0)
        self.assertEqual(from_inventory.stats['plants'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')

    def test_dequeue_destroyed_g_wet_to_g_wet(self):
        
        db.session.execute(destroyed_g_wet_to_batch_g_wet)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151601]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151600).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151601).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151601)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151600)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'g-wet')
        
        self.assertEqual(to_inventory.stats['g-wet'], 5000.0)
        self.assertEqual(from_inventory.stats['g-wet'], 0.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'destruction inventory')
        
    def test_dequeue_destroyed_g_wet_to_dry(self):
        
        db.session.execute(destroyed_g_wet_to_batch_dry)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151604]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151603).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151604).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151604)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151603)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'g-wet')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'g-wet')
        
        self.assertEqual(to_inventory.stats['g-dry']['dry'], 2000.0)
        self.assertEqual(from_inventory.stats['g-wet'], 1000.0)
        self.assertEqual(to_inventory.type, 'batch')
        self.assertEqual(from_inventory.type, 'batch')
        
    def test_dequeue_destroyed_dry_to_dry(self):
        
        db.session.execute(destroyed_dry_to_batch_dry)
        
        payload = {
                    "reason_for_dequeue": "Test",
                    "witness_1": "current@wilcompute.com",
                    "witness_2": "current@wilcompute.com",
                    "destruction_inventories": [151606]
                }

        response = self.client.post('/v1/organizations/1/destruction_inventory/dequeue', json=payload)

        response_body = json.loads(response.data)
        
        to_inventory = Inventory.query.filter(Inventory.id == 151605).one_or_none()
        from_inventory = Inventory.query.filter(Inventory.id == 151606).one_or_none()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('data').get('from_inventory_id'), 151606)
        self.assertEqual(response_body[0].get('data').get('to_inventory_id'), 151605)
        self.assertEqual(response_body[0].get('data').get('from_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('to_qty'), 1000.0)
        self.assertEqual(response_body[0].get('data').get('from_qty_unit'), 'dry')
        self.assertEqual(response_body[0].get('data').get('to_qty_unit'), 'dry')
        
        self.assertEqual(to_inventory.stats['g-dry']['dry'], 10000.0)
        self.assertEqual(from_inventory.stats['g-dry']['dry'], 0.0)
        self.assertEqual(to_inventory.type, 'received inventory')
        self.assertEqual(from_inventory.type, 'destruction inventory')
