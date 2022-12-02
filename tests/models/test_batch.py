import secrets
from decimal import Decimal
from app import db
from tests import TestCase
from models.inventory.batch import Batch
from models.inventory import Inventory
from models.activity import Activity
from models.user import User
from models.organization import Organization

class TestBatch(TestCase):
    organization_id = 1
    user_id=1
    def setUp(self):
        super(TestBatch, self).setUp()
        
        org_radom_name = "GrowerIQ-" + str(secrets.token_hex(nbytes=8))
        organizations = Organization(name=org_radom_name, timestamp='2021-01-01 00:00:00', data='{}')
        db.session.add(organizations)
        db.session.commit()
        self.organization_id = organizations.id
        
        user = User(organization_id=self.organization_id, name="User Fake", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='email@wilcompute.com')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id
        
        
    def test_creates_ungerminated_seeds_destruction_inventory(self):
        batch = Batch(organization_id=self.organization_id, name='candies', variety='Harlequin', created_by=self.user_id, stats={ 'seeds': 300 }, type='batch', timestamp='2021-07-27 15:17:00', attributes={'room': 'Quarantine Room', 'stage': 'planning', 'test_status': '', 'seeds_weight': 3000, 'seed_weight': 10})
        db.session.add(batch)
        db.session.commit()
        
        params = { 'quantity': 100, 'approved_by': 'email@wilcompute.com', 'recorded_by': 'email@wilcompute.com' , 'scale_name':"scale", 'timestamp':"2021-07-27 15:17:00"}
        response = batch.germinate_seed(self.user_id, self.organization_id, params)
        
        self.assertEqual(Inventory.query.count(), 2)
        destruction_inventory = Inventory.query.filter(Inventory.type == 'destruction inventory').first()
        self.assertEqual(destruction_inventory.data, {'collected_from': 'Quarantine Room', 'from_inventory_id': batch.id, 'reason_for_destruction': 'Ungerminated seeds'})
        self.assertEqual(destruction_inventory.stats, {'g-wet': Decimal('2000.0')})
        self.assertEqual(destruction_inventory.attributes, {'status': 'undestroyed'})
        self.assertEqual(destruction_inventory.variety, 'Harlequin')
        activities_with_parent_id = Activity.query.filter(Activity.parent_id == response['germinate_seeds_activity_id']).count()
        self.assertEqual(activities_with_parent_id, 5)
        activities_from_destruction = Activity.query.filter(Activity.parent_id == response['queue_for_destruction_activity_id']).count()
        self.assertEqual(activities_from_destruction, 4)
        germinate_seeds_total = Activity.query.count()
        self.assertEqual(germinate_seeds_total, 10)

    def test_germinate_seeds_without_destruction(self):
        batch = Batch(organization_id=self.organization_id, name='candies', variety='Harlequin', created_by=self.user_id, stats={ 'seeds': 300 }, type='batch', timestamp='2021-07-27 15:17:00', attributes={'room': 'Quarantine Room', 'stage': 'planning', 'test_status': '', 'seeds_weight': 3000, 'seed_weight': 10})
        db.session.add(batch)
        db.session.commit()
        params = { 'quantity': 300, 'approved_by': 'email@wilcompute.com', 'recorded_by': 'email@wilcompute.com' , 'scale_name':"scale", 'timestamp': "2021-07-27 15:17:00",}
        response = batch.germinate_seed(self.user_id, self.organization_id, params)
        self.assertEqual(Inventory.query.count(), 1)
        germinate_seeds_without_destruction = -1
        self.assertEqual(response["queue_for_destruction_activity_id"], germinate_seeds_without_destruction)
        activities_with_parent_id = Activity.query.filter(Activity.parent_id == response['germinate_seeds_activity_id']).count()
        self.assertEqual(activities_with_parent_id, 4)
        germinate_seeds_total = Activity.query.count()
        self.assertEqual(germinate_seeds_total, 5)


    def test_germinate_seeds_without_seeds(self):
        batch = Batch(organization_id=self.organization_id, name='candies', variety='Harlequin', created_by=self.user_id, stats={ 'seeds': 300 }, type='batch', timestamp='2021-07-27 15:17:00', attributes={'room': 'Quarantine Room', 'stage': 'planning', 'test_status': '', 'seeds_weight': 3000, 'seed_weight': 10})
        db.session.add(batch)
        db.session.commit()
        params = { 'quantity': 0, 'approved_by': 'email@wilcompute.com', 'recorded_by': 'email@wilcompute.com' , 'scale_name':"scale", 'timestamp': "2021-07-27 15:17:00",}
        response = batch.germinate_seed(self.user_id, self.organization_id, params)
        self.assertEqual(Inventory.query.count(), 2)
        germinate_without_seeds = -1
        self.assertEqual(response["germinate_seeds_activity_id"], germinate_without_seeds)
        
    def test_germinate_seeds_less_than_zero(self):
        batch = Batch(organization_id=self.organization_id, name='candies', variety='Harlequin', created_by=self.user_id, stats={ 'seeds': 300 }, type='batch', timestamp='2021-07-27 15:17:00', attributes={'room': 'Quarantine Room', 'stage': 'planning', 'test_status': '', 'seeds_weight': 3000, 'seed_weight': 10})
        db.session.add(batch)
        db.session.commit()
        
        params = { 'quantity': -1, 'approved_by': 'email@wilcompute.com', 'recorded_by': 'email@wilcompute.com' , 'scale_name':"scale", "timestamp": "2021-07-27 15:17:00",}
        result = batch.germinate_seed(self.user_id, self.organization_id, params)
        self.assertEqual(batch.stats.get('seeds'), 300)
        self.assertEqual(result['queue_for_destruction_activity_id'], -1)
        self.assertEqual(result['germinate_seeds_activity_id'], -1)
