'''Creates lot from reveived inventory based on given csv file'''
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411

import sys
import os
import csv
from datetime import datetime, timedelta


sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import get_tables, DATABASE
from utils import (get_variety_taxonomy_option_id)
from activities.create_lot import CreateLot
from activities.create_signature import CreateSignature
from activities.transfer_inventory import TransferInventory
from activities.update_room import UpdateRoom
from utils import generate_timestamp, get_inventory_adjustment_activity_id, get_received_inventory_adjustment_activity_id, get_user_id_by_name, update_timestamp


cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/create lot import.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["variety"] = row.index("variety")
            column_index["to_room"] = row.index("room")
            column_index["from_inventory_id"] = row.index("received inventory id")
            column_index["to_qty"] = row.index("transfer qty")
            column_index["to_qty_unit"] = row.index("transfer unit")
            column_index["approved_by"] = row.index("approved_by")
            column_index["checked_by"] = row.index("checked_by")
            column_index["weighed_by"] = row.index("weighed_by")
            column_index["date"] = row.index("date")
            column_index["organization_id"] = row.index("organization_id")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            # Create lot
            create_lot_result = {}
            create_lot_post_obj = {
                
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "create_lot",
                'variety': row[column_index["variety"]],
                'variety_id': get_variety_taxonomy_option_id(row[column_index["variety"]], row[column_index["organization_id"]]),
                'weighed_by': row[column_index["weighed_by"]],
                'checked_by': row[column_index["checked_by"]],
                'approved_by': row[column_index["approved_by"]],
                'to_room': row[column_index["to_room"]],
                'from_inventory_id': row[column_index["from_inventory_id"]],
                'inventory_type': 'received_inventory',
                'to_qty': row[column_index["to_qty"]],
                'to_qty_unit': row[column_index["to_qty_unit"]],
                'from_qty': row[column_index["to_qty"]],
                'from_qty_unit': row[column_index["to_qty_unit"]]
                
            }
            try:
                create_lot_result = CreateLot.do_activity(create_lot_post_obj, {})
                print('Lot ID: ', create_lot_result["inventory_id"])
            except:
                print('error at create lot on create_lot')
                raise
        
            update_timestamp('inventories', create_lot_result["inventory_id"], generate_timestamp(row[column_index["date"]]))
            update_timestamp('activities', create_lot_result["activity_id"], generate_timestamp(row[column_index["date"]]))
            
            # Update Room
            update_room_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "update_room",
                'inventory_id': create_lot_result["inventory_id"],
                'to_room': row[column_index["to_room"]],
            }
            try:
                update_room_result = UpdateRoom.do_activity(update_room_post_obj, {})
                print('Update Room Activity Id: ', update_room_result["activity_id"])
            except:
                print('error at Update Room on transfer_to_batch_import')
                raise
            # Backdating
            update_timestamp('activities', update_room_result["activity_id"], generate_timestamp(row[column_index["date"]]))
            
            
            # Transfer Inventory
            transfer_inv_result = {}
            transfer_inventory_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "transfer_inventory",
                'to_inventory_id': create_lot_result["inventory_id"],
                'from_inventory_id': row[column_index["from_inventory_id"]],
                'to_qty_unit': row[column_index["to_qty_unit"]],
                'from_qty_unit': row[column_index["to_qty_unit"]],
                'to_qty': row[column_index["to_qty"]],
                'from_qty': row[column_index["to_qty"]],
                'approved_by': row[column_index["approved_by"]],
                'checked_by': row[column_index["checked_by"]],
                'weighed_by': row[column_index["weighed_by"]],
                'variety': get_variety_taxonomy_option_id(row[column_index["variety"]], row[column_index["organization_id"]])
            }
            try:
                transfer_inv_result = TransferInventory.do_activity(transfer_inventory_post_obj, {})
                print('Approval Activity Id: ', transfer_inv_result["activity_id"])
            except:
                print('error at Transfer Inventory on transfer_to_batch_import')
                raise
            # Backdating
            update_timestamp('activities', transfer_inv_result["activity_id"], generate_timestamp(row[column_index["date"]]))

            # Get received inventory adjustment activity id and backdate it
            received_inventory_adjustment_activity_id = get_received_inventory_adjustment_activity_id(row[column_index["from_inventory_id"]], row[column_index["to_qty_unit"]])
            update_timestamp('activities', received_inventory_adjustment_activity_id, generate_timestamp(row[column_index["date"]]))

            # Get batch inventory adjustment activity id and backdate it
            batch_inventory_adjustment_activity_id = get_inventory_adjustment_activity_id(create_lot_result["inventory_id"])
            update_timestamp('activities', batch_inventory_adjustment_activity_id, generate_timestamp(row[column_index["date"]]))

            # Create signatures
            checked_sig_post_obj = weighed_sig_post_obj = approved_sig_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "create_signature",
                'activity_id': transfer_inv_result['activity_id'],
                'timestamp': datetime.today().isoformat(),
            }

            checked_sig_post_obj.update({
                'field': 'checked by',
                'signed_by': get_user_id_by_name(row[column_index["checked_by"]])
            })

            column_index.update({
                'field': 'weighed by',
                'signed_by': get_user_id_by_name(row[column_index["weighed_by"]])
            })

            approved_sig_post_obj.update({
                'field': 'approved by',
                'signed_by': get_user_id_by_name(row[column_index["approved_by"]])
            })
            try:
                checked_sig_post_obj_result = CreateSignature.do_activity(checked_sig_post_obj, {})
                # Backdating
                update_timestamp('activities', checked_sig_post_obj_result["activity_id"], generate_timestamp(row[column_index["date"]]))
                update_timestamp('signatures', checked_sig_post_obj_result["signature_id"], generate_timestamp(row[column_index["date"]]))

                weighed_sig_post_obj_result = CreateSignature.do_activity(weighed_sig_post_obj, {})
                # Backdating
                update_timestamp('activities', weighed_sig_post_obj_result["activity_id"], generate_timestamp(row[column_index["date"]]))
                update_timestamp('signatures', weighed_sig_post_obj_result["signature_id"], generate_timestamp(row[column_index["date"]]))

                approved_sig_post_obj_result = CreateSignature.do_activity(approved_sig_post_obj, {})
                # Backdating
                update_timestamp('activities', approved_sig_post_obj_result["activity_id"], generate_timestamp(row[column_index["date"]]))
                update_timestamp('signatures', approved_sig_post_obj_result["signature_id"], generate_timestamp(row[column_index["date"]]))
                
                print('Signatures are created')
            except:
                print('error at create signatures on transfer_to_batch_import')
                raise 

            line_count += 1
cursor.close()
DATABASE.dedicated_connection().commit()
