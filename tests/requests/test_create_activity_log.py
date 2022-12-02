import json
from decimal import Decimal
from models.activities_history import ActivitiesHistory
from models.activity import Activity
from tests import TestCase
from tests.requests import AuthenticatedTestCase
from flask import jsonify
from app import db

class TestCreateActivityLog(AuthenticatedTestCase):

    def setUp(self):
        TestCase.tearDown(self)
        super(TestCreateActivityLog, self).setUp()

        activity = Activity(
            organization_id = '1',
            created_by = 1,
            timestamp  = '2022-06-15 16:12:47.473 -0300',
            name  = 'create_activity_log',
            data = {
                "description": "Description Test",
                "detail": "Title test",
                "inventory_id": "35864",
                "timestamp": "2022-02-02 00:52:32",
            },
            parent_id = None,
            edited = False,
            deleted = False
        )

        db.session.add(activity)
        db.session.commit()


    def test_post_create_activity_log(self):
        
        payload = {
            "description": "Description Test",
            "detail": "Title test",
            "inventory_id": "35864",
            "uploads": [{
                "category": "COA",
                "content_type": "application/pdf",
                "description": "A COA document for the material",
                "name": "Pass COA v2.pdf",
                "id": "1990"
            }]
        }
        
        response = self.client.post(f'/v1/organizations/1/activity/create_activity_log', json=payload)
        
        response_body = json.loads(response.data)
        
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_body.get('data').get('description'), 'Description Test')
        self.assertEqual(response_body.get('data').get('detail'), 'Title test')
        self.assertEqual(response_body.get('data').get('inventory_id'), 35864)
        self.assertEqual(response_body.get('data').get('uploads')[0].get('id'), 1990)


    def test_put_create_activity_log(self):
        
        payload = {
            "description": "Description Test",
            "detail": "Title test",
            "inventory_id": "35864",
            "uploads": [{
                "category": "COA",
                "content_type": "application/pdf",
                "description": "A COA document for the material",
                "name": "Pass COA v2.pdf",
                "id": "1990"
            }]
        }
        
        response = self.client.post(f'/v1/organizations/1/activity/create_activity_log', json=payload)
        
        response = json.loads(response.data)
        
        activity_id = response.get('id')
        
            
        payload = {
            "description": "Description Test Update",
            "detail": "Title test Update",
            "inventory_id": "35864",
            "timestamp": "2022-02-02 00:52:32+00:00",
            "uploads": [{
                "category": "COA",
                "content_type": "application/pdf",
                "description": "A COA document for the material Update",
                "name": "Pass COA v2.pdf",
                "id": "1990"
            }],
            "reason_for_modification": 'test'
        }
        
        response = self.client.put(f'/v1/organizations/1/activity/create_activity_log/{activity_id}', json=payload)
        
        response_body = json.loads(response.data)
        
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('data').get('description'), 'Description Test Update')
        self.assertEqual(response_body.get('data').get('detail'), 'Title test Update')
        self.assertEqual(response_body.get('data').get('inventory_id'), 35864)
        self.assertEqual(response_body.get('timestamp'), '2022-02-02 00:52:32+00:00')
        self.assertEqual(response_body.get('data').get('uploads')[0].get('description'), 'A COA document for the material Update')


    def test_delete_create_activity_log(self):
        
        payload = {
            "description": "Description Test",
            "detail": "Title test",
            "inventory_id": "35864",
            "uploads": [{
                "category": "COA",
                "content_type": "application/pdf",
                "description": "A COA document for the material",
                "name": "Pass COA v2.pdf",
                "id": "1990"
            }]
        }
        
        response = self.client.post(f'/v1/organizations/1/activity/create_activity_log', json=payload)
        
        response = json.loads(response.data)
        
        activity_id = response.get('id')
        
            
        payload = {
            "reason_for_modification": 'test'
        }
        
        response = self.client.delete(f'/v1/organizations/1/activity/create_activity_log/{activity_id}', json=payload)
        
        response_body = json.loads(response.data)
        
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body, {})
