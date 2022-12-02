import json
from decimal import Decimal
from models.role import Role
from models.role_permission import RolePermission
from models.user import User
from models.user_role import UserRole
from models.permission import Permission
from tests import TestCase
from tests.requests import AuthenticatedTestCase
from flask import jsonify
from app import db

class TestRolePermission(AuthenticatedTestCase):
    
    number_of_permissions = 0
    
    def setUp(self):
        TestCase.tearDown(self)
        super(TestRolePermission, self).setUp()
        
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
        
        role_permission = [RolePermission(role_id=1, permission_id =1),
                           RolePermission(role_id=1, permission_id =2),
                           RolePermission(role_id=1, permission_id =3),
                           RolePermission(role_id=1, permission_id =4),
                           RolePermission(role_id=1, permission_id =5),
                           RolePermission(role_id=1, permission_id =6),
                           RolePermission(role_id=1, permission_id =7),
                           RolePermission(role_id=1, permission_id =8),
                           RolePermission(role_id=1, permission_id =9),
                           RolePermission(role_id=1, permission_id =10),
                           RolePermission(role_id=1, permission_id =11),
                           RolePermission(role_id=1, permission_id =12),
                           RolePermission(role_id=1, permission_id =13),
                           RolePermission(role_id=1, permission_id =14),
                           RolePermission(role_id=1, permission_id =15),
                           RolePermission(role_id=1, permission_id =16),
                           RolePermission(role_id=1, permission_id =17),
                           RolePermission(role_id=1, permission_id =18)]

        db.session.bulk_save_objects(role_permission)
        db.session.commit()
        
        role_permission = [RolePermission(role_id=2, permission_id =1),
                           RolePermission(role_id=2, permission_id =2),
                           RolePermission(role_id=2, permission_id =3)]

        db.session.bulk_save_objects(role_permission)
        db.session.commit()
        
        role_permission = [RolePermission(role_id=3, permission_id =1)]

        db.session.bulk_save_objects(role_permission)
        db.session.commit()
        
        user = User(organization_id=1, name="Test User", auth0_id=None, enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='test_user@wilcompute.com')

        db.session.add(user)
        db.session.commit()
        
        user = User(organization_id=1, name="Test User 2", auth0_id=None, enabled=True, created_by=1, timestamp='2021-07-27 15:17:00', data='{}', email='test_user_2@wilcompute.com')

        db.session.add(user)
        db.session.commit()
        
        user_role = [UserRole(user_id = 1, role_id = 1),
                     UserRole(user_id = 2, role_id = 2),
                     UserRole(user_id = 3, role_id = 1)]

        db.session.bulk_save_objects(user_role)
        db.session.commit()
        
        self.number_of_permissions = (len(Permission.query.all()))



    def test_get_all_roles_permission_from_organization(self):

        response = self.client.get('/v1/organizations/1/role_permission')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 2)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(len(response_body[1]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[0]['permissions'][3]['has_access'], False)
        self.assertEqual(response_body[1]['permissions'][3]['has_access'], True)
        self.assertEqual(response_body[0]['role_id'], 2)
        self.assertEqual(response_body[1]['role_id'], 1)
        self.assertEqual(response_body[0]['role_name'], 'QA')
        self.assertEqual(response_body[1]['role_name'], 'Admin')
        self.assertEqual(response_body[0]['sections_qty'], 3)
        self.assertEqual(response_body[1]['sections_qty'], 7)
        self.assertEqual(response_body[0]['users_qty'], 1)
        self.assertEqual(response_body[1]['users_qty'], 2)

    def test_get_roles_permission_by_id(self):

        response = self.client.get('/v1/organizations/2/role_permission/3')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[0]['permissions'][3]['has_access'], False)
        self.assertEqual(response_body[0]['permissions'][0]['has_access'], True)
        self.assertEqual(response_body[0]['role_id'], 3)
        self.assertEqual(response_body[0]['role_name'], 'Cultivator')
        self.assertEqual(response_body[0]['sections_qty'], 1)
        self.assertEqual(response_body[0]['users_qty'], 0)



    def test_add_new_role_missing_parent(self):
        
        args = {
            "name": "role test",
            "permission_ids": [2,3,4,5,6,7,8,9,10,11,12]
        }

        response = self.client.post('/v1/organizations/1/role_permission', json=args)

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[0]['permissions'][0]['has_access'], True)
        self.assertEqual(response_body[0]['permissions'][1]['has_access'], True)
        self.assertEqual(response_body[0]['permissions'][12]['has_access'], False)
        self.assertEqual(response_body[0]['role_id'], 4)
        self.assertEqual(response_body[0]['role_name'], 'role test')
        self.assertEqual(response_body[0]['sections_qty'], 7)

    def test_add_new_role_missing_one_child(self):
        
        args = {
            "name": "role test",
            "permission_ids": [2,3,4,5,6,7,9,10,11,12]
        }

        response = self.client.post('/v1/organizations/1/role_permission', json=args)

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[0]['permissions'][0]['has_access'], True)
        self.assertEqual(response_body[0]['permissions'][7]['has_access'], False)
        self.assertEqual(response_body[0]['role_id'], 4)
        self.assertEqual(response_body[0]['role_name'], 'role test')
        self.assertEqual(response_body[0]['sections_qty'], 7)

    def test_add_new_role_name_with_whitespaces(self):
        
        args = {
            "name": "               role test                                       ",
            "permission_ids": [2,3,4,5,6,7,9,10,11,12]
        }

        response = self.client.post('/v1/organizations/1/role_permission', json=args)

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[0]['permissions'][0]['has_access'], True)
        self.assertEqual(response_body[0]['permissions'][7]['has_access'], False)
        self.assertEqual(response_body[0]['role_id'], 4)
        self.assertEqual(response_body[0]['role_name'], 'role test')
        self.assertEqual(response_body[0]['sections_qty'], 7)


    def test_update_role_name(self):
        
        args = {
            "name": "updated QA"
        }

        response = self.client.put('/v1/organizations/1/role_permission/2', json=args)

        response_body = json.loads(response.data)
        
        print(response_body)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[0]['permissions'][0]['has_access'], True)
        self.assertEqual(response_body[0]['permissions'][3]['has_access'], False)
        self.assertEqual(response_body[0]['role_id'], 2)
        self.assertEqual(response_body[0]['role_name'], 'updated QA')
        self.assertEqual(response_body[0]['sections_qty'], 3)

    def test_update_role_permissions(self):
        
        args = {
            "permission_ids": [10]
        }

        response = self.client.put('/v1/organizations/1/role_permission/2', json=args)

        response_body = json.loads(response.data)
        
        print(response_body)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[0]['permissions'][9]['has_access'], True)
        self.assertEqual(response_body[0]['role_id'], 2)
        self.assertEqual(response_body[0]['role_name'], 'QA')
        self.assertEqual(response_body[0]['sections_qty'], 1)

    def test_update_role_name_and_permissions(self):
        
        args = {
            "name": "updated QA",
            "permission_ids": [10,11]
        }

        response = self.client.put('/v1/organizations/1/role_permission/2', json=args)

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[0]['permissions'][9]['has_access'], True)
        self.assertEqual(response_body[0]['permissions'][10]['has_access'], True)
        self.assertEqual(response_body[0]['permissions'][0]['has_access'], False)
        self.assertEqual(response_body[0]['role_id'], 2)
        self.assertEqual(response_body[0]['role_name'], 'updated QA')
        self.assertEqual(response_body[0]['sections_qty'], 1)


    def test_batch_update(self):
        
        args = [
            {
                "role_id": 1,
                "name": "Super Admin"
            },
            {
                "role_id": 2,
                "name": "updated QA",
                "permission_ids": [10,11]
            }
        ]

        response = self.client.put('/v1/organizations/1/role_permission/batch', json=args)

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 2)
        self.assertEqual(len(response_body[1]['permissions']), self.number_of_permissions)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[1]['permissions'][9]['has_access'], True)
        self.assertEqual(response_body[1]['permissions'][10]['has_access'], True)
        self.assertEqual(response_body[0]['permissions'][0]['has_access'], True)
        self.assertEqual(response_body[0]['permissions'][1]['has_access'], True)
        self.assertEqual(response_body[1]['permissions'][0]['has_access'], False)
        self.assertEqual(response_body[1]['role_id'], 2)
        self.assertEqual(response_body[0]['role_id'], 1)
        self.assertEqual(response_body[1]['role_name'], 'updated QA')
        self.assertEqual(response_body[0]['role_name'], 'Super Admin')
        self.assertEqual(response_body[1]['sections_qty'], 1)
        self.assertEqual(response_body[0]['sections_qty'], 7)


    def test_delete_role_permission(self):

        self.client.delete('/v1/organizations/1/role_permission/2')
        
        response = self.client.get('/v1/organizations/1/role_permission')

        response_body = json.loads(response.data)

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response_body), 1)
        self.assertEqual(len(response_body[0]['permissions']), self.number_of_permissions)
        self.assertEqual(response_body[0]['role_id'], 1)
        self.assertEqual(response_body[0]['role_name'], 'Admin')
        self.assertEqual(response_body[0]['sections_qty'], 7)