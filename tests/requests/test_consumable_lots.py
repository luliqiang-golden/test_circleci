from decimal import Decimal
from models.transaction_allocations import TransactionAllocations
from models.consumable_classes import ConsumableClasses
from tests.requests import AuthenticatedTestCase
from models.transactions import Transactions
from models.crm_accounts import CRMAccounts
from models.activity import Activity
from app import db
import json

class TestConsumableLots(AuthenticatedTestCase):
    
    def setUp(self):
        super(TestConsumableLots, self).setUp()
        
        consumable_class = ConsumableClasses (
            organization_id = 1,
            created_by = 1,
            type = 'gloves',
            subtype = 'large',
            unit = 'each',
            data = {},
            status = 'enabled'
        )
        
        db.session.add(consumable_class)
        db.session.commit()
        
        
        
        consumable_class_2 = ConsumableClasses (
            organization_id = 1,
            created_by = 1,
            type = 'gloves',
            subtype = 'medium',
            unit = 'each',
            data = {},
            status = 'enabled'
        )
        
        db.session.add(consumable_class_2)
        db.session.commit()
        
        
        crm_account = CRMAccounts (
            created_by = 1,
            data = {"fax": "", "email": "supplier@wilcompute.com", "telephone": "12345612345", "residing_address": {"city": "Toronto", "country": "Canada", "address1": "40 Executive Ct", "address2": None, "province": "ON", "postalCode": "123 ABC"}, "shipping_address": [{"city": "Toronto", "country": "Canada", "address1": "40 Executive Ct", "address2": None, "province": "ON", "postalCode": "123 ABC"}]},
            name = 'supplier',
            organization_id = 1,
            attributes = {"status": "approved", "expiration_date": "2200-12-18"},
            account_type = 'supplier'
        )
        
        db.session.add(crm_account)
        db.session.commit()


    def test_create_consumable_lot_first_unit_should_work(self):
        
        args = {
            "upload_id": None,
            "po": "111",
            "vendor_lot_number": "123",
            "vendor_name": "supplier",
            "vendor_id": "1",
            "initial_qty": 100,
            "expiration_date": None,
            "intended_use": None,
            "damage_to_shipment": False,
            "delivery_matches_po": True,
            "checked_by": "current@wilcompute.com",
            "approved_by": "current@wilcompute.com",
            "amount": 50,
            "delivery_details": None,
            "damage_details": None,
            "unit": "each",
            "supply_type": "gloves",
            "subtype": "large",
            "created_by": 1
        }

        response = self.client.post('/v1/organizations/1/consumable_lots', json=args)

        response_body = json.loads(response.data)

        activities = Activity.query.order_by(Activity.timestamp.asc()).all()
        transactions = Transactions.query.all()
        transaction_allocations = TransactionAllocations.query.all()

        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_body.get('id'), 1)
        self.assertEqual(response_body.get('vendor_lot_number'), '123')
        self.assertEqual(response_body.get('status'), 'awaiting_approval')
        self.assertEqual(response_body.get('class_id'), 1)
        
        self.assertEqual(len(activities), 3)
        self.assertEqual(activities[0].name, 'receive_consumable_lot')
        self.assertEqual(activities[1].name, 'record_transaction')
        self.assertEqual(activities[2].name, 'record_transaction_allocation')
        self.assertEqual(activities[0].data, {"po": "111", "unit": "each", "amount": 50.0, "upload_id": None, "vendor_id": "1", "vendor_lot_number": "123", "checked_by": "current@wilcompute.com", "approved_by": "current@wilcompute.com", "initial_qty": 100, "vendor_name": "supplier", "intended_use": None, "damage_details": None, "expiration_date": None, "delivery_details": None, "consumable_lot_id": 1, "damage_to_shipment": False, "consumable_class_id": 1, "delivery_matches_po": True})
        self.assertEqual(activities[1].data, {"description": None, "total_amount": Decimal('50.0'), "crm_account_id": '1', "purchase_order": "111", "transaction_id": 1})
        self.assertEqual(activities[2].data, {"type": "debit", "amount": 50.0, "description": None, "transaction_id": 1, "consumable_lot_id": 1, "transaction_allocation_id": 1})
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].total_amount, 50)
        self.assertEqual(transactions[0].crm_account_id, 1)
        self.assertEqual(transactions[0].purchase_order, '111')
        
        self.assertEqual(len(transaction_allocations), 1)
        self.assertEqual(transaction_allocations[0].amount, 50)
        self.assertEqual(transaction_allocations[0].transaction_id, 1)
        self.assertEqual(transaction_allocations[0].data, {"consumable_lot_id": 1})
        self.assertEqual(transaction_allocations[0].type, 'debit')
        
    
    def test_create_consumable_lot_second_unit_same_po_should_work(self):
        
        args_1 = {
            "upload_id": None,
            "po": "111",
            "vendor_lot_number": "123",
            "vendor_name": "supplier",
            "vendor_id": "1",
            "initial_qty": 100,
            "expiration_date": None,
            "intended_use": None,
            "damage_to_shipment": False,
            "delivery_matches_po": True,
            "checked_by": "current@wilcompute.com",
            "approved_by": "current@wilcompute.com",
            "amount": 50,
            "delivery_details": None,
            "damage_details": None,
            "unit": "each",
            "supply_type": "gloves",
            "subtype": "large",
            "created_by": 1
        }
        
        args_2 = {
            "upload_id": None,
            "po": "111",
            "vendor_lot_number": "123",
            "vendor_name": "supplier",
            "vendor_id": "1",
            "initial_qty": 100,
            "expiration_date": None,
            "intended_use": None,
            "damage_to_shipment": False,
            "delivery_matches_po": True,
            "checked_by": "current@wilcompute.com",
            "approved_by": "current@wilcompute.com",
            "amount": 50,
            "delivery_details": None,
            "damage_details": None,
            "unit": "each",
            "supply_type": "gloves",
            "subtype": "medium",
            "created_by": 1
        }

        self.client.post('/v1/organizations/1/consumable_lots', json=args_1)
        response_2 = self.client.post('/v1/organizations/1/consumable_lots', json=args_2)

        response_body = json.loads(response_2.data)
        
        activities = Activity.query.order_by(Activity.timestamp.asc()).all()
        transactions = Transactions.query.all()
        transaction_allocations = TransactionAllocations.query.all()

        self.assertEqual(response_2.headers['Content-Type'], 'application/json')
        self.assertEqual(response_2.status_code, 200)
        self.assertEqual(response_body.get('id'), 2)
        self.assertEqual(response_body.get('vendor_lot_number'), '123')
        self.assertEqual(response_body.get('status'), 'awaiting_approval')
        self.assertEqual(response_body.get('class_id'), 2)
        
        self.assertEqual(len(activities), 6)
        self.assertEqual(activities[3].name, 'receive_consumable_lot')
        self.assertEqual(activities[4].name, 'update_transaction_total_amount')
        self.assertEqual(activities[5].name, 'record_transaction_allocation')
        self.assertEqual(activities[3].data, {"po": "111", "unit": "each", "amount": 50.0, "upload_id": None, "vendor_id": "1", "vendor_lot_number": "123", "checked_by": "current@wilcompute.com", "approved_by": "current@wilcompute.com", "initial_qty": 100.0, "vendor_name": "supplier", "intended_use": None, "damage_details": None, "expiration_date": None, "delivery_details": None, "consumable_lot_id": 2, "damage_to_shipment": False, "consumable_class_id": 2, "delivery_matches_po": True})
        self.assertEqual(activities[4].data, {"amount": 50.0, "transaction_id": 1})
        self.assertEqual(activities[5].data, {"type": "debit", "amount": 50.0, "description": None, "transaction_id": 1, "consumable_lot_id": 2, "transaction_allocation_id": 2})
        
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].total_amount, 100)
        self.assertEqual(transactions[0].crm_account_id, 1)
        self.assertEqual(transactions[0].purchase_order, '111')
        
        self.assertEqual(len(transaction_allocations), 2)
        self.assertEqual(transaction_allocations[1].amount, 50)
        self.assertEqual(transaction_allocations[1].transaction_id, 1)
        self.assertEqual(transaction_allocations[1].data, {"consumable_lot_id": 2})
        self.assertEqual(transaction_allocations[1].type, 'debit')
    
        
    def test_create_consumable_lot_should_fail_invalid_checked_by(self):
        
        try:
            args = {
                "upload_id": None,
                "po": "111",
                "vendor_lot_number": "123",
                "vendor_name": "supplier",
                "vendor_id": "1",
                "initial_qty": 100,
                "expiration_date": None,
                "intended_use": None,
                "damage_to_shipment": False,
                "delivery_matches_po": True,
                "checked_by": "curren@wilcompute.com",
                "approved_by": "current@wilcompute.com",
                "amount": 50,
                "delivery_details": None,
                "damage_details": None,
                "unit": "each",
                "supply_type": "gloves",
                "subtype": "large",
                "created_by": 1
            }

            self.client.post('/v1/organizations/1/consumable_lots', json=args)

        except(Exception) as exception:
            self.assertEqual(exception.status_code, 400)
            self.assertEqual(exception.error['message'], 'Error while inserting data - curren@wilcompute.com not found for organization 1.')
            
            
    def test_create_consumable_lot_should_fail_invalid_approved_by(self):
        
        try:
            args = {
                "upload_id": None,
                "po": "111",
                "vendor_lot_number": "123",
                "vendor_name": "supplier",
                "vendor_id": "1",
                "initial_qty": 100,
                "expiration_date": None,
                "intended_use": None,
                "damage_to_shipment": False,
                "delivery_matches_po": True,
                "checked_by": "current@wilcompute.com",
                "approved_by": "curren@wilcompute.com",
                "amount": 50,
                "delivery_details": None,
                "damage_details": None,
                "unit": "each",
                "supply_type": "gloves",
                "subtype": "large",
                "created_by": 1
            }

            self.client.post('/v1/organizations/1/consumable_lots', json=args)

        except(Exception) as exception:
            self.assertEqual(exception.status_code, 400)
            self.assertEqual(exception.error['message'], 'Error while inserting data - curren@wilcompute.com not found for organization 1.')
            
    
    def test_create_consumable_lot_should_fail_invalid_vendor(self):
        
        try:
            args = {
                "upload_id": None,
                "po": "111",
                "vendor_lot_number": "123",
                "vendor_name": "supplier",
                "vendor_id": "9784651",
                "initial_qty": 100,
                "expiration_date": None,
                "intended_use": None,
                "damage_to_shipment": False,
                "delivery_matches_po": True,
                "checked_by": "current@wilcompute.com",
                "approved_by": "current@wilcompute.com",
                "amount": 50,
                "delivery_details": None,
                "damage_details": None,
                "unit": "each",
                "supply_type": "gloves",
                "subtype": "large",
                "created_by": 1
            }

            self.client.post('/v1/organizations/1/consumable_lots', json=args)

        except(Exception) as exception:
            self.assertEqual(exception.status_code, 400)
            self.assertEqual(exception.error['message'], 'Error while inserting data - vendor id: 9784651 named: supplier not found for organization 1.')
            
    
    def test_create_consumable_lot_should_fail_invalid_supply(self):
        
        try:
            args = {
                "upload_id": None,
                "po": "111",
                "vendor_lot_number": "123",
                "vendor_name": "supplier",
                "vendor_id": "1",
                "initial_qty": 100,
                "expiration_date": None,
                "intended_use": None,
                "damage_to_shipment": False,
                "delivery_matches_po": True,
                "checked_by": "current@wilcompute.com",
                "approved_by": "current@wilcompute.com",
                "amount": 50,
                "delivery_details": None,
                "damage_details": None,
                "unit": "each",
                "supply_type": "glove",
                "subtype": "large",
                "created_by": 1
            }

            self.client.post('/v1/organizations/1/consumable_lots', json=args)

        except(Exception) as exception:
            self.assertEqual(exception.status_code, 400)
            self.assertEqual(exception.error['message'], 'Error while inserting data - glove - large not found for organization 1.')
            
            