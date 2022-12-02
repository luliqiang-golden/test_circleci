'''Creates received_inventory based on given csv file'''
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411
import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import select_from_db, get_tables, DATABASE
from class_errors import DatabaseError
from activities.receive_inventory import ReceiveInventory
from activities.approve_received_inventory import ApproveReceivedInventory
from activities.record_transaction_allocation import RecordTransactionAllocation
from activities.record_transaction import RecordTransaction
from activities.update_transaction_total_amount import UpdateTransactionTotalAmount
from utils import generate_timestamp, update_timestamp, get_variety_taxonomy_option_id, get_crm_account_id

def get_transaction_id_from_po(purchase_order, crm_id, date, organization_id):
    params = {"po": purchase_order,
              "organization_id": organization_id}
    transaction_id_query = '''SELECT id from transactions WHERE purchase_order = %(po)s and organization_id = %(organization_id)s'''
    result = select_from_db(transaction_id_query, params)
    if not result:
        return record_transaction(purchase_order, crm_id, date, organization_id)['transaction_id']
    print('Exsiting transaction found: ', result[0]['id'])
    return result[0]['id']

def record_transaction(purchase_order, crm_id, date, organization_id):
    transaction_result = {}
    record_transaction_post_obj = {
        'organization_id': organization_id,
        'created_by': 1,
        'name': 'record_transaction',
        'crm_account_id': crm_id,
        'purchase_order': purchase_order
    }

    try:
        transaction_result = RecordTransaction.do_activity(record_transaction_post_obj, {})
        print('New transaction id: ', transaction_result["transaction_id"], transaction_result['activity_id'])
        update_timestamp('transactions', transaction_result["transaction_id"], generate_timestamp(date))    
        update_timestamp('activities', transaction_result['activity_id'], generate_timestamp(date))
        return transaction_result
    except:
        print('error at record transaction on receive_inventory_import')
        raise
     

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/receive inv import.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["variety_name"] = row.index("variety name")
            column_index["product_type"] = row.index("product type")
            column_index["package_type"] = row.index("package type")
            column_index["amount"] = row.index("amount")
            column_index["net_weight_received"] = row.index("net weight received")
            column_index["account"] = row.index("account")
            column_index["weighed_by"] = row.index("weighed by")
            column_index["checked_by"] = row.index("checked by")
            column_index["approved_by"] = row.index("approved by")
            column_index["source_lot_number"] = row.index("source lot number")
            column_index["po"] = row.index("purchase order")
            column_index["date"] = row.index("date")
            column_index["organization_id"] = row.index("organization_id")
            column_index["room"] = row.index("room")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            amount = float(row[column_index["amount"]])
            net_weight_received = float(row[column_index["net_weight_received"]])
            receive_inv_result = {}
            received_inv_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'amount': amount,
                'approved_by': row[column_index["approved_by"]],
                'checked_by': row[column_index["checked_by"]],
                'weighed_by': row[column_index["weighed_by"]],
                'damage_details': "",
                'damage_to_shipment': False,
                'delivery_details': "",
                'delivery_matches_po': True,
                'intended_use': "",
                'name': "receive_inventory",
                'net_weight_received': net_weight_received,
                'package_type': "unpackaged",
                'po': row[column_index["po"]],
                'qty_seeds': amount if row[column_index["product_type"]] == 'seeds' else '',
                'qty_weight': net_weight_received,
                'quarantined': "true",
                'seed_weight': (net_weight_received / amount) if 
                                    row[column_index["product_type"]] == 'seeds' and  amount != 0 else 0,
                'to_qty': amount,
                'to_qty_unit': row[column_index["product_type"]],
                'to_stage': "received-approved",
                'upload_id': 0,
                'variety': row[column_index["variety_name"]],
                'variety_id':  get_variety_taxonomy_option_id(row[column_index["variety_name"]], row[column_index["organization_id"]]),
                'vendor_id': get_crm_account_id(row[column_index["account"]], row[column_index["organization_id"]]),
                'vendor_lot_number': row[column_index["source_lot_number"]],
                'vendor_name': row[column_index["account"]],
                'room': row[column_index["room"]],
            }
            try:
                receive_inv_result = ReceiveInventory.do_activity(received_inv_post_obj, {})
                print('inventory_id: ', receive_inv_result["inventory_id"])
            except:
                print('error at receiving inventory on receive_inventory_import')
                raise

            params = {"quantity": amount, "inv_id": receive_inv_result["inventory_id"]}
            inv_adj_query = '''SELECT id from activities WHERE name = 'inventory_adjustment' 
                            and cast(data->>'quantity' as decimal) = %(quantity)s 
                            and cast(data->>'inventory_id' as numeric) = %(inv_id)s'''
            inv_adjustment_id = select_from_db(inv_adj_query, params)[0]['id']

            # Backdate
            update_timestamp('inventories', receive_inv_result["inventory_id"], generate_timestamp(row[column_index["date"]]))
            update_timestamp('activities', receive_inv_result["activity_id"], generate_timestamp(row[column_index["date"]]))
            update_timestamp('activities',inv_adjustment_id, generate_timestamp(row[column_index["date"]]))

            # Receive inventory approve
            receive_approved_result = {}
            received_approved_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'approved_by': row[column_index["approved_by"]],
                'inventory_id': receive_inv_result["inventory_id"],
                'name': "approve_received_inventory",
                'quarantined': False,
                'to_stage': "received-approved"
            }

            try:
                receive_approved_result = ApproveReceivedInventory.do_activity(received_approved_post_obj, {})
                print('Approval Activity Id: ', receive_approved_result["activity_id"])
            except:
                print('error at receiving inventory approval on receive_inventory_import')
                raise
            
            # Backdate
            update_timestamp('activities', receive_approved_result["activity_id"], generate_timestamp(row[column_index["date"]]))

            # Record Transaction allocation
            transaction_allocation_result = {}
            transaction_id = get_transaction_id_from_po(row[column_index["po"]], get_crm_account_id(row[column_index["account"]], row[column_index["organization_id"]]), row[column_index["date"]], row[column_index["organization_id"]])
            record_transaction_allocation_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'amount': amount,
                'description': "",
                'inventory_id': receive_inv_result["inventory_id"],
                'name': "record_transaction_allocation",
                'transaction_id': transaction_id ,
                'type': "debit"
            }

            try:
                transaction_allocation_result = RecordTransactionAllocation.do_activity(record_transaction_allocation_post_obj, {})
                print('Transaction Allocation Id: ', transaction_allocation_result['transaction_allocation_id'])
            except:
                print('error at transaction allocation post on receive_inventory_import')
                raise
            # Backdate
            update_timestamp('transaction_allocations', transaction_allocation_result["transaction_allocation_id"], generate_timestamp(row[column_index["date"]]))    
            update_timestamp('activities', transaction_allocation_result["activity_id"], generate_timestamp(row[column_index["date"]]))

            # Update transaction amount
            update_transaction_result = {}
            update_transaction_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'amount': amount, #$ amount is hardcoded to 0
                'name': "update_transaction_total_amount",
                'to_transaction_id': transaction_id,  
            }

            try:
                update_transaction_result = UpdateTransactionTotalAmount.do_activity(update_transaction_post_obj, {})
                print('Transaction Allocation Id: ', update_transaction_result['activity_id'])
            except:
                print('error at transaction update post on receive_inventory_import')
                raise
            # Backdate   
            update_timestamp('activities', update_transaction_result["activity_id"], generate_timestamp(row[column_index["date"]]))
            line_count += 1

cursor.close()
DATABASE.dedicated_connection().commit()
