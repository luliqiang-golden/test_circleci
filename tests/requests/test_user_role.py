import json
from decimal import Decimal
from models.role import Role
from models.user_role import UserRole
from models.user import User
from tests.requests import AuthenticatedTestCase
from flask import jsonify
from app import db

class TestUserRole(AuthenticatedTestCase):
    
    def setUp(self):
        super(TestUserRole, self).setUp()
        
        role = Role(organization_id='1',
            created_by=1,
            name='Admin',
            role_description = '')

        db.session.add(role)
        db.session.commit()
        
        role = Role(organization_id='1',
            created_by=1,
            name='QA',
            role_description = '')

        db.session.add(role)
        db.session.commit()
        
        role = Role(organization_id='2',
            created_by=1,
            name='Cultivator',
            role_description = '')

        db.session.add(role)
        db.session.commit()
        
        user = User(organization_id=1, name="Test User", auth0_id=None, enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='test_user@wilcompute.com')

        db.session.add(user)
        db.session.commit()
        
        user = User(organization_id=1, name="Test User 2", auth0_id=None, enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='test_user_2@wilcompute.com')

        db.session.add(user)
        db.session.commit()
        
        user = User(organization_id=1, name="Test User 3", auth0_id=None, enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='test_user_3@wilcompute.com')

        db.session.add(user)
        db.session.commit()
        
        user_role = [UserRole(user_id = 1, role_id = 1),
                     UserRole(user_id = 2, role_id = 2),
                     UserRole(user_id = 3, role_id = 2)]

        db.session.bulk_save_objects(user_role)
        db.session.commit()

    def test_get_all_user_roles_from_organization(self):

        response = self.client.get('/v1/organizations/1/user_role')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 3)
        self.assertEqual(response_body[0].get('user_name'), 'Current User')
        self.assertEqual(response_body[1].get('user_name'), 'Test User')
        self.assertEqual(response_body[0].get('role_name'), 'Admin')
        self.assertEqual(response_body[1].get('role_name'), 'QA')
        self.assertEqual(response_body[0].get('organization_id'), 1)
        self.assertEqual(response_body[1].get('organization_id'), 1)

    def test_get_user_role_by_user_id(self):

        response = self.client.get('/v1/organizations/1/user_role?user_id=1')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('user_name'), 'Current User')
        self.assertEqual(response_body.get('role_name'), 'Admin')
        self.assertEqual(response_body.get('organization_id'), 1)

    def test_get_user_role_by_role_id(self):

        response = self.client.get('/v1/organizations/1/user_role?role_id=2')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0].get('user_name'), 'Test User')
        self.assertEqual(response_body[0].get('role_name'), 'QA')
        self.assertEqual(response_body[0].get('organization_id'), 1)

    def test_add_user_role(self):

        args = {
            "user_id": 4,
            "role_id": 1
        }

        response = self.client.post('/v1/organizations/1/user_role', json=args)

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('user_name'), 'Test User 3')
        self.assertEqual(response_body.get('role_name'), 'Admin')
        self.assertEqual(response_body.get('organization_id'), 1)

    def test_update_user_role(self):
        
        args = {
            "user_id": 4,
            "role_id": 1
        }

        self.client.post('/v1/organizations/1/user_role', json=args)

        args = {
            "role_id": 2
        }

        response = self.client.put('/v1/organizations/1/user_role/4', json=args)

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('user_name'), 'Test User 3')
        self.assertEqual(response_body.get('role_name'), 'QA')
        self.assertEqual(response_body.get('organization_id'), 1)

    def test_delete_user_role(self):

        self.client.delete('/v1/organizations/1/user_role/2')

        response = self.client.get('/v1/organizations/1/user_role')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0].get('user_name'), 'Current User')
        self.assertEqual(response_body[0].get('role_name'), 'Admin')
        self.assertEqual(response_body[0].get('organization_id'), 1)