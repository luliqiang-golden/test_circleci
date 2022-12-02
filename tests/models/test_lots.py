import secrets
from tests import TestCase

from models.inventory.lot import Lot
from models.inventory import Inventory
from app import db
from models.user import User
from models.organization import Organization

class TestLots(TestCase):

    organization_id = 1
    user_id=1
    def setUp(self):
        super(TestLots, self).setUp()
        
        org_radom_name = "GrowerIQ-" + str(secrets.token_hex(nbytes=8))
        organizations = Organization(name=org_radom_name, timestamp='2021-01-01 00:00:00', data='{}')
        db.session.add(organizations)
        db.session.commit()
        self.organization_id = organizations.id
        
        user = User(organization_id=self.organization_id, name="User Fake", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=self.user_id, timestamp='2021-07-27 15:17:00', data='{}', email='email@wilcompute.com')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id
        #create original batch
        inventory_batch = Inventory(organization_id=self.organization_id,
                                    created_by=self.user_id,
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
        inventory_lot_1 = Inventory(organization_id=self.organization_id,
                                    created_by=self.user_id,
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
        inventory_lot_2 = Inventory(organization_id=self.organization_id,
                                    created_by=self.user_id,
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

        #create lot reporting 1
        inventory_lot_1 = Inventory(organization_id=self.organization_id,
                                    created_by=self.user_id,
                                    variety='AK47',
                                    name='dryyyyy', 
                                    data={'variety_id': 51, 'from_inventory_id': 1},
                                    timestamp='2022-01-11 10:46:32.315',
                                    stats={'g-dry': {'dry': 0}}, 
                                    type='lot', 
                                    attributes={'room': 'Grow Bay 1'})
        db.session.add(inventory_lot_1)
        db.session.commit()

        #create lot reporting 2
        inventory_lot_1 = Inventory(organization_id=self.organization_id,
                                    created_by=self.user_id,
                                    variety='AK47',
                                    name='dry3', 
                                    data={'variety_id': 51, 'from_inventory_id': 2},
                                    timestamp='2022-01-11 10:46:32.315',
                                    stats={'g-dry': {'dry': 10}}, 
                                    type='lot', 
                                    attributes={'room': 'Grow Bay 1'})
        db.session.add(inventory_lot_1)
        db.session.commit()

    def test_lots_report(self):
        response = Lot.lots_report(self, 1, {})
        print(response)

    def test_lots_report_filter_id(self):
        response = Lot.lots_report(self, 1, {'ID': 3})
        self.assertEqual(response[0].get('ID'), 3)

    def test_lots_report_filter_variety(self):
        response = Lot.lots_report(self, 1, {'variety': 'Afghan Kush'})
        self.assertEqual(response[0].get('Variety'), 'Afghan Kush')

    def test_lots_report_filter_archived(self):
        response = Lot.lots_report(self, 1, {'quantity' != 0})
        self.assertEqual(response[0].get('Quantity'), 1980)
