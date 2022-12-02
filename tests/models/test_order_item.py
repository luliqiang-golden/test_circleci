import json
import secrets
from tests import TestCase

from models.crm_accounts import CRMAccounts
from models.order_item import OrderItem
from models.inventory import Inventory
from models.shipments import Shipments
from models.orders import Orders
from models.user import User
from models.organization import Organization

from models.skus import Skus
from app import db

class TestOrderItems(TestCase):
    organization_id = 1
    user_id=1
    def setUp(self):
        org_radom_name = "GrowerIQ-" + str(secrets.token_hex(nbytes=8))
        organizations = Organization(name=org_radom_name, timestamp='2021-01-01 00:00:00', data='{}')
        db.session.add(organizations)
        db.session.commit()
        self.organization_id = organizations.id
        
        user = User(organization_id=self.organization_id, name="User Fake", auth0_id='auth0|5ab26f288bd5067ff5787c89', enabled=True, created_by=self.user_id, timestamp='2021-07-27 15:17:00', data='{}', email='email@wilcompute.com')
        db.session.add(user)
        db.session.commit()
        self.user_id = user.id
        
        super(TestOrderItems, self).setUp()
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
        
        #create sku 1
        sku_1 = Skus(organization_id=self.organization_id,
                        created_by=self.user_id,
                        name='SKU=afkush:Dry:Whs:pac:10g', 
                        variety='Afghan Kush', 
                        cannabis_class='dried cannabis', 
                        target_qty=10, 
                        data={'type': 'packaged'},
                        attributes={'status': 'enabled', 'reserved': 0},
                        target_qty_unit='dry',
                        sales_class='wholesale',
                        price=15,
                        current_inventory=5)
        db.session.add(sku_1)
        db.session.commit()
        sku_1_id = sku_1.id
        sku_1_name = sku_1.name
        
        #create sku 2
        sku_2 = Skus(organization_id=self.organization_id,
                        created_by=self.user_id,
                        name='SKU=afkush:Dry:Whs:pac:15g', 
                        variety='Afghan Kush', 
                        cannabis_class='dried cannabis', 
                        target_qty=15, 
                        data={'type': 'packaged'},
                        attributes={'status': 'enabled', 'reserved': 0},
                        target_qty_unit='dry',
                        sales_class='wholesale',
                        price=20,
                        current_inventory=5)
        db.session.add(sku_2)
        db.session.commit()
        sku_2_id = sku_2.id
        sku_2_name = sku_2.name
        
        #create lot item 1
        for i in range(5):
            inventory_lot_item_1 = Inventory(organization_id=self.organization_id,
                                                created_by=self.user_id,
                                                variety='Afghan Kush',
                                                name=f'Afghan Kush-2-22 {i}', 
                                                data={'sku_id': sku_1_id, 'sku_name': sku_1_name, 'from_inventory_id': inventory_lot_1_id},
                                                stats={'g-dry': {'dry': 10.0}}, 
                                                type='lot item', 
                                                attributes={'room': 'Grow Bay 1'})
            db.session.add(inventory_lot_item_1)
            db.session.commit()
        
        #create lot item 2
        for i in range(5):
            inventory_lot_item_2 = Inventory(organization_id=self.organization_id,
                                                created_by=self.user_id,
                                                variety='Afghan Kush',
                                                name=f'Afghan Kush-2-22 {i}', 
                                                data={'sku_id': sku_2_id, 'sku_name': sku_2_name, 'from_inventory_id': inventory_lot_2_id},
                                                stats={'g-dry': {'dry': 15.0}},
                                                type='lot item',
                                                attributes={'room': 'Grow Bay 1'})
            db.session.add(inventory_lot_item_2)
            db.session.commit()
            
        #create lot item 3
        for i in range(5):
            inventory_lot_item_3 = Inventory(organization_id=self.organization_id,
                                                created_by=self.user_id,
                                                variety='Afghan Kush',
                                                name=f'Afghan Kush-2-22 {i}', 
                                                data={'sku_id': sku_2_id, 'sku_name': sku_2_name, 'from_inventory_id': inventory_lot_1_id},
                                                stats={'g-dry': {'dry': 15.0}},
                                                type='lot item',
                                                attributes={'room': 'Grow Bay 1'})
            db.session.add(inventory_lot_item_3)
            db.session.commit()
        
        #create CRM Account
        crm_account = CRMAccounts(
            created_by = self.user_id,
            data = {'fax': '123123123', 'email': 'distributor@canada.com', 'telephone': '123123123', 'residing_address': {'city': 'Montréal', 'country': 'ca', 'address1': '715 Av. Papineau', 'address2': '123', 'province': 'Québec', 'postalCode': 'H2L'}, 'shipping_address': [{'city': 'Montréal', 'country': 'ca', 'address1': '715 Av. Papineau', 'address2': '123', 'province': 'Québec', 'postalCode': 'H2L'}]},
            name = 'distributorCanada',
            organization_id = self.organization_id,
            timestamp = '2022-01-11 10:43:27.081 -0300',
            attributes = {'status': 'approved', 'expiration_date': '2045-06-06T03:00:00.000Z'},
            account_type = 'distributor'
        )
        db.session.add(crm_account)
        db.session.commit()
        crm_account_id = crm_account.id
        
        #create Order
        order = Orders(
            crm_account_id = crm_account_id,
            created_by = self.user_id,
            organization_id = self.organization_id,
            description = None,
            order_type = 'wholesale',
            order_received_date = '2022-01-13T03:00:00.000Z',
            order_placed_by = 'test',
            timestamp = '2022-01-13 16:29:35.653 -0300',
            data = {'tax_name': 'fallback', 'crm_account_name': 'distributorCanada'},
            shipping_address = {'city': 'Montréal', 'country': 'ca', 'address1': '715 Av. Papineau', 'address2': '123', 'province': 'Québec', 'postalCode': 'H2L'},
            ordered_stats = {'g-dry': {'dry': 25.0}},
            shipped_stats = {},
            status = 'awaiting_approval',
            shipping_status = 'pending',
            due_date = '2022-01-13T03:00:00.000Z',
            sub_total = 90.00,
            provincial_tax = 6.00,
            excise_tax = 0.00,
            discount_percent = 0.00,
            discount = 0.00,
            shipping_value = 0.00,
            total = 96.00,
            include_tax = True
        )
        db.session.add(order)
        db.session.commit()
        order_id = order.id
        
        #create Order item 1
        order_item_1 = OrderItem(
            sku_id = sku_1_id,
            sku_name = sku_1_name,
            order_id = order_id,
            data = {},
            created_by = self.user_id,
            shipment_id = None,
            organization_id = self.organization_id,
            ordered_stats = {'g-dry': {'dry': 10.0}},
            variety = 'Afghan Kush',
            timestamp = '2022-01-13 16:32:45.722 -0300',
            shipped_stats = {},
            status = 'awaiting_approval',
            quantity = 2,
            filled = None,
            price = 30.00,
            excise_tax = 0.00,
            provincial_tax = 3.00,
            attributes = {},
            discount = 0.00,
            shipping_value = 0.00,
        )
        db.session.add(order_item_1)
        db.session.commit()
        
        #create Order item 2
        order_item_2 = OrderItem(
            sku_id = sku_2_id,
            sku_name = sku_2_name,
            order_id = order_id,
            data = {},
            created_by = self.user_id,
            shipment_id = None,
            organization_id = self.organization_id,
            ordered_stats = {'g-dry': {'dry': 15.0}},
            variety = 'Afghan Kush',
            timestamp = '2022-01-13 16:32:45.722 -0300',
            shipped_stats = {},
            status = 'awaiting_approval',
            quantity = 3,
            filled = None,
            price = 60.00,
            excise_tax = 0.00,
            provincial_tax = 6.00,
            attributes = {},
            discount = 0.00,
            shipping_value = 0.00
        )
        db.session.add(order_item_2)
        db.session.commit()
        
        #create Shipment
        shipment = Shipments(
            tracking_number = None,
            shipped_date = None,
            delivered_date = None,
            created_by = self.user_id,
            organization_id = self.organization_id,
            timestamp = '2022-01-13 20:58:53.730 -0300',
            shipping_address = {'city': 'Montréal', 'country': 'ca', 'address1': '715 Av. Papineau', 'address2': '123', 'province': 'Québec', 'postalCode': 'H2L'},
            crm_account_id = crm_account_id,
            status = 'pending',
            data = {},
            attributes = {},
        )
        db.session.add(shipment)
        db.session.commit()

    def test_validate_lots_quantity(self):
        
        sku_id = 1
        
        lots = [
                {
                'id': 2,
                'quantity_selected': 5
                }
            ]
        
        response = OrderItem.validate_lots_quantity(lots, sku_id)
        
        lot_item_grouped_by_lot_id = response[1]
        
        for key in lot_item_grouped_by_lot_id:
            for lot_item in lot_item_grouped_by_lot_id[key]:
                self.assertEquals(lot_item.data['sku_id'], sku_id)
