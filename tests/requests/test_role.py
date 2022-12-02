import json
from decimal import Decimal
from models.role import Role
from tests.requests import AuthenticatedTestCase
from flask import jsonify
from app import db

class TestRole(AuthenticatedTestCase):
    
    def setUp(self):
        super(TestRole, self).setUp()
        
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

    def test_get_all_roles_from_organization(self):

        response = self.client.get('/v1/organizations/1/role')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 2)
        self.assertEqual(response_body[0].get('name'), 'Admin')
        self.assertEqual(response_body[1].get('name'), 'QA')
        self.assertEqual(response_body[0].get('organization_id'), 1)
        self.assertEqual(response_body[1].get('organization_id'), 1)

    def test_get_role_by_id(self):

        response = self.client.get('/v1/organizations/2/role')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(response_body[0].get('name'), 'Cultivator')
        self.assertEqual(response_body[0].get('organization_id'), 2)

    