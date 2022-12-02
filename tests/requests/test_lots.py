import json
from decimal import Decimal
from tests.requests import AuthenticatedTestCase
from flask import jsonify
from models.inventory import Inventory
from models.skus import Skus
from app import db

class TestLots(AuthenticatedTestCase):
    
    def setUp(self):
        super(TestLots, self).setUp()
        #create original batch
        inventory_batch = Inventory(organization_id='1',
                                    created_by=1,
                                    variety='Afghan Kush',
                                    name='dry',
                                    data={'plan': {'end_type': 'dry', 'timeline': [{'name': 'planning', 'planned_length': None}, {'name': 'germinating', 'planned_length': None}, {'name': 'propagation', 'planned_length': None}, {'name': 'vegetation', 'planned_length': None}, {'name': 'flowering', 'planned_length': None}, {'name': 'harvesting', 'planned_length': None}, {'name': 'drying', 'planned_length': None}, {'name': 'qa', 'planned_length': None}], 'start_date': '2022-01-11T03:00:00.000Z', 'start_type': 'seeds'}, 'variety_id': 51}, 
                                    stats={'g-dry': {'dry': 1995.0}, 'g-wet': 0.0, 'seeds': 0.0, 'plants': 0.0}, 
                                    type='batch', 
                                    attributes={'room': 'Grow Bay 1', 'stage': 'qa', 'seed_weight': 1.0, 'test_status': 'batch-release', 'seeds_weight': 900.0})
        db.session.add(inventory_batch)
        db.session.commit()
        inventory_batch_id = inventory_batch.id
        
        #create lot 1
        inventory_lot_1 = Inventory(organization_id='1',
                                    created_by=1,
                                    variety='Afghan Kush',
                                    name='dry', 
                                    data={'variety_id': 51, 'from_inventory_id': inventory_batch_id},
                                    timestamp='2022-01-11 10:46:32.315',
                                    stats={'g-dry': {'dry': 4845.0}}, 
                                    type='lot', 
                                    attributes={'room': 'Grow Bay 1'})
        db.session.add(inventory_lot_1)
        db.session.commit()
        inventory_lot_1_id = inventory_lot_1.id
        
        #create lot 2
        inventory_lot_2 = Inventory(organization_id='1',
                                    created_by=1,
                                    variety='Afghan Kush',
                                    name='dry2', 
                                    data={'variety_id': 51, 'from_inventory_id': inventory_batch_id},
                                    timestamp='2022-01-15 10:46:32.315 -0300',
                                    stats={'g-dry': {'dry': 1980.0}}, 
                                    type='lot', 
                                    attributes={'room': 'Grow Bay 1'})
        db.session.add(inventory_lot_2)
        db.session.commit()
        inventory_lot_2_id = inventory_lot_2.id
        
        #create sku 1
        sku_1 = Skus(organization_id='1',
                        created_by=1,
                        name='SKU=afkush:Dry:Whs:pac:10g', 
                        variety='Afghan Kush', 
                        cannabis_class='dried cannabis', 
                        target_qty=10, 
                        data={"type": "packaged"},
                        attributes={"status": "enabled", "reserved": 0},
                        target_qty_unit='dry',
                        sales_class='wholesale',
                        price=15,
                        current_inventory=1)
        db.session.add(sku_1)
        db.session.commit()
        sku_1_id = sku_1.id
        sku_1_name = sku_1.name
        
        #create sku 2
        sku_2 = Skus(organization_id='1',
                        created_by=1,
                        name='SKU=afkush:Dry:Whs:pac:15g', 
                        variety='Afghan Kush', 
                        cannabis_class='dried cannabis', 
                        target_qty=15, 
                        data={"type": "packaged"},
                        attributes={"status": "enabled", "reserved": 0},
                        target_qty_unit='dry',
                        sales_class='wholesale',
                        price=20,
                        current_inventory=1)
        db.session.add(sku_2)
        db.session.commit()
        sku_2_id = sku_2.id
        sku_2_name = sku_2.name
        
        #create lot item 1
        inventory_lot_item_1 = Inventory(organization_id='1',
                                            created_by=1,
                                            variety='Afghan Kush',
                                            name='Afghan Kush-2-22', 
                                            data={"sku_id": sku_1_id, "sku_name": sku_1_name, "from_inventory_id": inventory_lot_1_id},
                                            stats={"g-dry": {"dry": 10.0}}, 
                                            type='lot item', 
                                            attributes={"room": "Grow Bay 1"})
        db.session.add(inventory_lot_item_1)
        db.session.commit()
        
        #create lot item 2
        inventory_lot_item_2 = Inventory(organization_id='1',
                                            created_by=1,
                                            variety='Afghan Kush',
                                            name='Afghan Kush-2-22',
                                            data={"sku_id": sku_2_id, "sku_name": sku_2_name, "from_inventory_id": inventory_lot_2_id},
                                            stats={"g-dry": {"dry": 15.0}},
                                            type='lot item',
                                            attributes={"room": "Grow Bay 1"})
        db.session.add(inventory_lot_item_2)
        db.session.commit()

 
    def test_get_available_lot_items_without_filter(self):

        response = self.client.get('/v1/organizations/1/lots')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0].get('lot_id'), 2)
        self.assertEqual(response_body[1].get('lot_id'), 3)
        self.assertEqual(response_body[0].get('sku_id'), 1)
        self.assertEqual(response_body[1].get('sku_id'), 2)
        self.assertEqual(response_body[0].get('items_available'), 1)
        self.assertEqual(response_body[1].get('items_available'), 1)

    def test_get_available_lot_items_minimum_timestamp_filter(self):

        response = self.client.get('/v1/organizations/1/lots?min_timestamp=2022-01-14 00:00:00')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('lot_id'), 3)
        self.assertEqual(response_body[0].get('sku_id'), 2)
        self.assertEqual(response_body[0].get('items_available'), 1)

    def test_get_available_lot_items_maximum_timestamp_filter(self):

        response = self.client.get('/v1/organizations/1/lots?max_timestamp=2022-01-14 00:00:00')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('lot_id'), 2)
        self.assertEqual(response_body[0].get('sku_id'), 1)
        self.assertEqual(response_body[0].get('items_available'), 1)

    def test_get_available_lot_items_name_filter(self):

        response = self.client.get('/v1/organizations/1/lots?name=dry2')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('lot_id'), 3)
        self.assertEqual(response_body[0].get('sku_id'), 2)
        self.assertEqual(response_body[0].get('lot_name'), 'dry2')
        self.assertEqual(response_body[0].get('items_available'), 1)

    def test_get_available_lot_items_sku_id_filter(self):

        response = self.client.get('/v1/organizations/1/lots?sku_id=1')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('lot_id'), 2)
        self.assertEqual(response_body[0].get('sku_id'), 1)
        self.assertEqual(response_body[0].get('lot_name'), 'dry')
        self.assertEqual(response_body[0].get('items_available'), 1)

    def test_get_available_lot_items_min_items_available_filter(self):

        response = self.client.get('/v1/organizations/1/lots?min_items_available=1')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0].get('lot_id'), 2)
        self.assertEqual(response_body[1].get('lot_id'), 3)
        self.assertEqual(response_body[0].get('sku_id'), 1)
        self.assertEqual(response_body[1].get('sku_id'), 2)
        self.assertGreaterEqual(response_body[0].get('items_available'), 1)
        self.assertGreaterEqual(response_body[1].get('items_available'), 1)


    def test_post_with_correct_fields(self):
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
                "approved_by":"current@wilcompute.com",
                "checked_by":"current@wilcompute.com",
                "weighed_by":"current@wilcompute.com",
                "from_inventory_id":1,
                "inventory_type":"received-inventory",
                "timestamp": "2022-01-01 00:00:00",
            }
        response_data = jsonify({
            "inventory_id":6,
            "activity_id": 1
        })
        response = self.client.post('/v1/organizations/1/lots', json=args)
        assert response.status_code == 200
        assert response.data == response_data.data

    def test_post_lot_stats_for_decimal_qty(self):
        args = {
                "name":"create_lot",
                "scale_name":"office",
                "lot_name":"czxczcz",
                "to_room":"Propagation Room",
                "variety":"213",
                "variety_id":444,
                "from_qty":10.50,
                "from_qty_unit":"dry",
                "to_qty":10.50,
                "to_qty_unit":"dry",
                "approved_by":"current@wilcompute.com",
                "checked_by":"current@wilcompute.com",
                "weighed_by":"current@wilcompute.com",
                "from_inventory_id":1,
                "inventory_type":"received-inventory",
                "timestamp": "2022-01-01 00:00:00",
            }
        response = self.client.post('/v1/organizations/1/lots', json=args)
        response_data = eval(response.data)
        lot = Inventory.query.get(response_data.get("inventory_id"))
        expected_stats = {'g-dry': {'dry': Decimal('10.5'), 'cured': 0}}
        self.assertEqual(lot.stats, expected_stats)

    def test_post_transfer_to_existing_lot_with_correct_fields(self):
        args = {
            "name": "transfer_inventory",
            "scale_name": "scale",
            "variety": "Afghan Kush",
            "variety_id": 51,
            "from_qty": 20.0,
            "from_qty_unit": "dry",
            "to_qty": 20.0,
            "to_qty_unit": "dry",
            "from_inventory_id": 1,
            "to_inventory_id": 3,
            "inventory_type": "batch",
            "approved_by": "current@wilcompute.com",
            "checked_by": "current@wilcompute.com",
            "weighed_by": "current@wilcompute.com",
            "timestamp": "2022-01-01 00:00:00",
        }
        response = self.client.post('/v1/organizations/1/lots/transfer-lot', json=args)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        response_data = eval(response.data)

        destiny_inventory = Inventory.query.get(response_data['inventory_id'])
        expected_stats_lot = {'g-dry': {'dry': Decimal('2000.0')}}
        self.assertEqual(destiny_inventory.stats, expected_stats_lot)
        assert response.status_code == 200        


    def test_post_transfer_to_existing_lot_with_diff_source_inventories(self):
        #create receive_inventory
        receive_inventory = Inventory(organization_id='1',
                                        created_by=1,
                                        variety='Afghan Kush',
                                        name='Afghan Kush-2-22',
                                        data={"variety_id": 51, "package_type": "unpackaged"},
                                        stats={"g-dry": {"dry": 200.0}},
                                        type='receive inventory',
                                        attributes={"room": "Grow Bay 1"})
        db.session.add(receive_inventory)
        db.session.commit()

        try:
            args = {
                "name": "transfer_inventory",
                "scale_name": "scale",
                "variety": "Afghan Kush",
                "variety_id": 51,
                "from_qty": 10.0,
                "from_qty_unit": "dry",
                "to_qty": 10.0,
                "to_qty_unit": "dry",
                "from_inventory_id": 6,
                "to_inventory_id": 3,
                "inventory_type": "batch",
                "approved_by": "current@wilcompute.com",
                "checked_by": "current@wilcompute.com",
                "weighed_by": "current@wilcompute.com",
                "timestamp": "2022-01-01 00:00:00",
            }

            response = self.client.post('/v1/organizations/1/lots/transfer-lot', json=args)
            assert response.status_code == 200
        except(Exception) as exception:
            self.assertEquals(exception.status_code, 400)
            self.assertEquals(exception.error['code'], 'transfer_lot_mismatch_source_inventory')
