import json
import secrets
from models.taxonomies import Taxonomies
from models.taxonomy_options import TaxonomyOptions

from tests.requests import AuthenticatedTestCase
from flask import request, jsonify
from models.inventory import Inventory
from models.skus import Skus
from app import db
from models.user import User
from models.organization import Organization

class TestLotItems(AuthenticatedTestCase):
    
    organization_id = 1
    user_id=1
    taxonomy_id=1
    taxonomy_option_id=1
    taxonomy_option_name=''
    def setUp(self):
        super(TestLotItems, self).setUp()
        
        org_radom_name = "GrowerIQ-" + str(secrets.token_hex(nbytes=8))
        organizations = Organization(name=org_radom_name, timestamp='2021-01-01 00:00:00', data='{}')
        db.session.add(organizations)
        db.session.commit()
        self.organization_id = organizations.id
        
        user = User(organization_id=self.organization_id, name="User Fake", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=self.user_id, timestamp='2021-07-27 15:17:00', data='{}', email='email@wilcompute.com')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id
        
        taxonomy = Taxonomies(organization_id = self.organization_id,
                                created_by = self.user_id,
                                name = 'varieties',
                                data = {},
                                )
        db.session.add(taxonomy)
        db.session.commit()
        self.taxonomy_id = taxonomy.id
        
        taxonomy_option = TaxonomyOptions(
            organization_id = self.organization_id,
            created_by = self.user_id,
            name = 'Blue Dream',
            data = """{"strain": ["Hybrid"], "stage_info": {"drying": {"days_in_stage": 10}, "seedling": {"days_in_stage": 10}, "flowering": {"days_in_stage": 10}, "vegetation": {"days_in_stage": 10}, "propagation": {"days_in_stage": 10}}, "description": ""}""",
            taxonomy_id = taxonomy.id
        )        
        db.session.add(taxonomy_option)
        db.session.commit()
        self.taxonomy_option_id = taxonomy_option.id
        self.taxonomy_option_name = taxonomy_option.name
        

        lot = Inventory(organization_id=self.organization_id,
                                    created_by=self.user_id,
                                    variety=self.taxonomy_option_name,
                                    name='dry', 
                                    data={'variety_id': self.taxonomy_option_id, 'from_inventory_id': 121},
                                    timestamp='2022-01-11 10:46:32.315',
                                    stats={'g-dry': {'dry': 40000.0}}, 
                                    type='lot', 
                                    attributes={'room': 'Grow Bay 1'})
        db.session.add(lot)
        db.session.commit()
         
        sku = Skus(organization_id=self.organization_id,
                        created_by=self.user_id,
                        name='SKU=afkush:Dry:Whs:pac:10g', 
                        variety=self.taxonomy_option_name, 
                        cannabis_class='dried cannabis', 
                        target_qty=10, 
                        data={"type": "packaged"},
                        attributes={"status": "enabled", "reserved": 0},
                        target_qty_unit='dry',
                        sales_class='wholesale',
                        price=15,
                        current_inventory=1)
        db.session.add(sku)
        db.session.commit()


    def test_lot_items_post_with_five_lot_item_quantity(self):
        args = {
            "name":"create_lot_item",
            "variety":self.taxonomy_option_name ,
            "approved_by":"email@wilcompute.com",
            "sku_id":1,
            "sku_name":"Blue Dream 1g", 
            "unit":"dry", 
            "lot_item_quantity":5, 
            "to_room":"propagation"
        }
        response_data = jsonify(
                {
                "data":{
                    "activities": [1,2,3,4,5],
                    "lot_items":[2,3,4,5,6]
                },
                "message": "success"
            }
        )
        response = self.client.post('/v1/organizations/' + str(self.organization_id) + '/lots/1/lot-items', json=args)
        result = json.loads(response.data)
        assert response.status_code == 200
        assert response.data == response_data.data


    def test_lot_items_post_with_single_lot_item_quantity(self):
        args = {
            "name":"create_lot_item",
            "variety":self.taxonomy_option_name ,
            "approved_by":"email@wilcompute.com",
            "sku_id":1,
            "sku_name":"213 1g", 
            "unit":"dry", 
            "lot_item_quantity":1, 
            "to_room":"propagation"
        }
        response_data = jsonify(
                {
                "data":{
                    "activities": [1],
                    "lot_items":[2]
                },
                "message": "success"
            }
        )
        response = self.client.post('/v1/organizations/' + str(self.organization_id) + '/lots/1/lot-items', json=args)
        result = json.loads(response.data)
        assert response.status_code == 200
        assert response.data == response_data.data

    def test_lot_items_post_with_wrong_user(self):
        args = {
            "name":"create_lot_item",
            "variety":self.taxonomy_option_name,
            "approved_by":"email@wilcompute.com",
            "sku_id":1,
            "sku_name":"213 1g", 
            "unit":"dry", 
            "lot_item_quantity":1, 
            "to_room":"propagation"
        }
        try:
            self.client.post('/v1/organizations/' + str(self.organization_id) + '/lots/1/lot-items', json=args)
        except Exception as e:
            self.assertEqual(e.status_code, 400)
            self.assertEqual(e.error['message'], f"User does not exists for {args.get('approved_by')} in organization #1")

    def test_lot_items_post_with_wrong_sku_id(self):
        args = {
            "name":"create_lot_item",
            "variety":self.taxonomy_option_name,
            "approved_by":"email@wilcompute.com",
            "sku_id":100,
            "sku_name":"213 1g", 
            "unit":"dry", 
            "lot_item_quantity":1, 
            "to_room":"propagation"
        }
        try:
            self.client.post('/v1/organizations/' + str(self.organization_id) + '/lots/1/lot-items', json=args)
        except Exception as e:
            self.assertEqual(e.status_code, 400)
            self.assertEqual(
                e.error['message'], 
                f"Not enough quantity available to create {args.get('lot_item_quantity')} number of lot_items from sku #{args.get('sku_id')}"
            )

    def test_lot_item_post_with_wrong_lot_id(self):
        args = {
            "name":"create_lot_item",
            "variety":self.taxonomy_option_name,
            "approved_by":"email@wilcompute.com",
            "sku_id":1,
            "sku_name":"213 1g", 
            "unit":"dry", 
            "lot_item_quantity":1, 
            "to_room":"propagation"
        }
        try:
            self.client.post('/v1/organizations/' + str(self.organization_id) + '/lots/100/lot-items', json=args)
        except Exception as e:
            self.assertEqual(e.status_code, 400)
            self.assertEqual(
                e.error['message'], 
                "No record found for inventory #100"
            )


        
