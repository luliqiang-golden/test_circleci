import json
from tests.requests import AuthenticatedTestCase

from models.crm_accounts import CRMAccounts
from models.order_item import OrderItem
from models.inventory import Inventory
from models.shipments import Shipments
from models.orders import Orders
from models.skus import Skus
from app import db

class TestOrderItems(AuthenticatedTestCase):

    def setUp(self):
        super(TestOrderItems, self).setUp()
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

        #create lot 3
        inventory_lot_3 = Inventory(organization_id='1',
                                    created_by=1,
                                    variety='Afghan Kush',
                                    name='dry3', 
                                    data={'variety_id': 51, 'from_inventory_id': [inventory_lot_1_id, inventory_lot_2_id]},
                                    timestamp='2022-01-15 10:46:32.315 -0300',
                                    stats={'g-dry': {'dry': 1980.0}}, 
                                    type='lot', 
                                    attributes={'room': 'Grow Bay 1'})
        db.session.add(inventory_lot_3)
        db.session.commit()
        inventory_lot_3_id = inventory_lot_3.id

        #create sku 1
        sku_1 = Skus(organization_id='1',
                        created_by=1,
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
        sku_2 = Skus(organization_id='1',
                        created_by=1,
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
            inventory_lot_item_1 = Inventory(organization_id='1',
                                                created_by=1,
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
            inventory_lot_item_2 = Inventory(organization_id='1',
                                                created_by=1,
                                                variety='Afghan Kush',
                                                name=f'Afghan Kush-2-22 {i}', 
                                                data={'sku_id': sku_2_id, 'sku_name': sku_2_name, 'from_inventory_id': inventory_lot_2_id},
                                                stats={'g-dry': {'dry': 15.0}},
                                                type='lot item',
                                                attributes={'room': 'Grow Bay 1'})
            db.session.add(inventory_lot_item_2)
            db.session.commit()
        
        #create CRM Account
        crm_account = CRMAccounts(
            created_by = 1,
            data = {'fax': '123123123', 'email': 'distributor@canada.com', 'telephone': '123123123', 'residing_address': {'city': 'Montréal', 'country': 'ca', 'address1': '715 Av. Papineau', 'address2': '123', 'province': 'Québec', 'postalCode': 'H2L'}, 'shipping_address': [{'city': 'Montréal', 'country': 'ca', 'address1': '715 Av. Papineau', 'address2': '123', 'province': 'Québec', 'postalCode': 'H2L'}]},
            name = 'distributorCanada',
            organization_id = 1,
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
            created_by = 1,
            organization_id = 1,
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
            created_by = 1,
            shipment_id = None,
            organization_id = 1,
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
            created_by = 1,
            shipment_id = None,
            organization_id = 1,
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
            created_by = 1,
            organization_id = 1,
            timestamp = '2022-01-13 20:58:53.730 -0300',
            shipping_address = {'city': 'Montréal', 'country': 'ca', 'address1': '715 Av. Papineau', 'address2': '123', 'province': 'Québec', 'postalCode': 'H2L'},
            crm_account_id = crm_account_id,
            status = 'pending',
            data = {},
            attributes = {},
        )
        db.session.add(shipment)
        db.session.commit()

    def test_order_item_invalid_shipment_id(self):
        try:
            params = {
                'shipment_id': 9999,
                'sku_id': 1,
                'lots': [
                    {
                    'id': 2,
                    'quantity_selected': 2
                    }
                ],
                'created_by': 1
            }
            
            self.client.post('/v1/organizations/1/order-items/1/fill', json=params)
            
        except(Exception) as exception:
            self.assertEquals(exception.status_code, 400)
            self.assertEquals(exception.error['message']['shipment_id'][0], 'Error while inserting data - shipment_id not found.')
    
    def test_order_item_missing_created_by(self):
    
        try:
            params = {
                'shipment_id': 1,
                'sku_id': 1,
                'lots': [
                    {
                    'id': 2,
                    'quantity_selected': 2
                    }
                ]
            }

            self.client.post('/v1/organizations/1/order-items/1/fill', json=params)

        except(Exception) as exception:
            self.assertEquals(exception.status_code, 400)
            self.assertEquals(exception.error['message']['created_by'][0], 'Missing data for required field.')

    def test_order_item_invalid_sku_id_without_shipment_id(self):
        
        try:
            params = {
                'sku_id': 9999,
                'lots': [
                    {
                    'id': 2,
                    'quantity_selected': 2
                    },
                    {
                    'id': 3,
                    'quantity_selected': 3
                    }
                ],
                'created_by': 1
            }
            
            self.client.post('/v1/organizations/1/order-items/1/fill', json=params)
        
        except(Exception) as exception:
            self.assertEquals(exception.status_code, 400)
            self.assertEquals(exception.error['message']['sku_id'][0], 'Error while inserting data - sku_id not found.')
    
    def test_order_item_total_quantity_requested_different_from_needed_quantity(self):
        
        params = {
            'sku_id': 1,
            'lots': [
                {
                'id': 2,
                'quantity_selected': 1
                }
            ],
            'created_by': 1
        }
        
        response = self.client.post('/v1/organizations/1/order-items/1/fill', json=params)
        
        response_body = json.loads(response.data)

        self.assertEquals(response.status_code, 400)
        self.assertEquals(response_body['message'], 'Error while inserting data - Total quantity requested is different from order item quantity')
        
    def test_order_item_lot_item_quantity_unavailable(self):
        
        try:
            params = {
                'sku_id': 1,
                'lots': [
                    {
                    'id': 2,
                    'quantity_selected': 10
                    }
                ],
                'created_by': 1
            }
            
            self.client.post('/v1/organizations/1/order-items/1/fill', json=params)
        
        except(Exception) as exception:
            self.assertEquals(exception.status_code, 400)
            self.assertEquals(exception.error['message']['_schema'][0], 'Invalid quantity selected for lot 2.')
            
    def test_order_item_fill_without_shipment(self):
        
        params = {
            'sku_id': 1,
            'lots': [
                {
                'id': 2,
                'quantity_selected': 2
                }
            ],
            'created_by': 1
        }
        
        response = self.client.post('/v1/organizations/1/order-items/1/fill', json=params)
        
        response_body = json.loads(response.data)

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response_body['shipment_id'], 2)
        self.assertEquals(response_body['quantity_filled'], 2)
        
    def test_order_item_fill_with_shipment(self):
        
        params = {
            'shipment_id': 1,
            'sku_id': 1,
            'lots': [
                {
                'id': 2,
                'quantity_selected': 2
                }
            ],
            'created_by': 1
        }
        
        response = self.client.post('/v1/organizations/1/order-items/1/fill', json=params)
        
        response_body = json.loads(response.data)

        self.assertEquals(response.status_code, 201)
        self.assertEquals(response_body['shipment_id'], 1)
        self.assertEquals(response_body['quantity_filled'], 2)
        
    
