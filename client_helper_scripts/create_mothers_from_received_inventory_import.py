'''Creates mother from reveived inventory based on given csv file'''
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411

import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import select_from_db, get_tables, DATABASE
from class_errors import DatabaseError
from activities.create_mother import CreateMother
from activities.update_room import UpdateRoom
from activities.transfer_inventory import TransferInventory
from activities.create_signature import CreateSignature
from utils import (generate_timestamp, update_timestamp, get_received_inventory_adjustment_activity_id,
                  get_inventory_adjustment_activity_id, get_variety_taxonomy_option_id, get_user_id_by_name)

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/create mothers from received inventory.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["mothers_count"] = row.index("number of mothers being created")
            column_index["variety"] = row.index("variety")
            column_index["room"] = row.index("room")
            column_index["from_inventory_id"] = row.index("received inventory id")
            column_index["approved_by"] = row.index("approved")
            column_index["prepared_by"] = row.index("prepared")
            column_index["reviewed_by"] = row.index("reviewed")
            column_index["date"] = row.index("date")
            column_index["organization_id"] = row.index("organization_id")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            for i in range(int(row[column_index["mothers_count"]])):
                # Create Mothers
                create_mother_result = {}
                create_mother_post_obj = {
                    'organization_id': row[column_index["organization_id"]],
                    'created_by': 1,
                    'name': "create_mother",
                    'to_status': 'not_added_to_batch',
                    'variety': row[column_index["variety"]],
                    'variety_id': get_variety_taxonomy_option_id(row[column_index["variety"]], row[column_index["organization_id"]])
                }
                try:
                    create_mother_result = CreateMother.do_activity(create_mother_post_obj, {})
                    print('Mother ID: ', create_mother_result["inventory_id"])
                except:
                    print('error at create mother on create_mothers_from_received_inventory_import')
                    raise

                # Backdating
                update_timestamp('inventories', create_mother_result["inventory_id"], generate_timestamp(row[column_index["date"]]))
                update_timestamp('activities', create_mother_result["activity_id"], generate_timestamp(row[column_index["date"]]))

                # Update room
                update_room_post_obj = {
                    'organization_id': row[column_index["organization_id"]],
                    'created_by': 1,
                    'name': "update_room",
                    'inventory_id': create_mother_result['inventory_id'],
                    'to_room': row[column_index["room"]]
                }
                try:
                    update_room_result = UpdateRoom.do_activity(update_room_post_obj, {})
                    print('Update room activity ID: ', update_room_result['activity_id'])
                except:
                    print('error at update room on create_mothers_from_received_inventory_import')
                    raise
                
                # Backdating
                update_timestamp('activities', update_room_result["activity_id"], generate_timestamp(row[column_index["date"]]))

                # Transfer inventory
                transfer_inv_result = {}
                transfer_inventory_post_obj = {
                    'organization_id': row[column_index["organization_id"]],
                    'created_by': 1,
                    'name': "transfer_inventory",
                    'to_inventory_id': create_mother_result["inventory_id"],
                    'from_inventory_id': row[column_index["from_inventory_id"]],
                    'to_qty_unit': 'plants',
                    'from_qty_unit': 'plants',
                    'to_qty': 1,
                    'from_qty': 1,
                    'approved_by': row[column_index["approved_by"]],
                    'prepared_by': row[column_index["prepared_by"]],
                    'reviewed_by': row[column_index["reviewed_by"]],
                    'variety': get_variety_taxonomy_option_id(row[column_index["variety"]], row[column_index["organization_id"]])
                }
                try:
                    transfer_inv_result = TransferInventory.do_activity(transfer_inventory_post_obj, {})
                    print('Transfer Inventory Activity Id: ', transfer_inv_result["activity_id"])
                except:
                    print('error at Transfer Inventory on create_mothers_from_received_inventory_import')
                    raise

                # Backdating
                update_timestamp('activities', transfer_inv_result["activity_id"], generate_timestamp(row[column_index["date"]]))

                # Get received_inventory type inventory_adjustment activity and backdate it.
                received_inventory_adjustment_activity_id = get_received_inventory_adjustment_activity_id(row[column_index["from_inventory_id"]], 'plants')
                update_timestamp('activities', received_inventory_adjustment_activity_id, generate_timestamp(row[column_index["date"]]))

                # Get inventory_adjustment activity and backdate it.
                inventory_adjustment_activity_id = get_inventory_adjustment_activity_id(create_mother_result["inventory_id"])
                update_timestamp('activities', inventory_adjustment_activity_id, generate_timestamp(row[column_index["date"]]))

                # Create signatures
                prepared_sig_post_obj = reviewed_sig_post_obj = approved_sig_post_obj = {
                    'organization_id': row[column_index["organization_id"]],
                    'created_by': 1,
                    'name': "create_signature",
                    'activity_id': transfer_inv_result['activity_id'],
                    'timestamp': datetime.today().isoformat(),
                }

                prepared_sig_post_obj.update({
                    'field': 'prepared by',
                    'signed_by': get_user_id_by_name(row[column_index["prepared_by"]])
                })

                reviewed_sig_post_obj.update({
                    'field': 'reviewed by',
                    'signed_by': get_user_id_by_name(row[column_index["reviewed_by"]])
                })

                approved_sig_post_obj.update({
                    'field': 'approved by',
                    'signed_by': get_user_id_by_name(row[column_index["approved_by"]])
                })
                try:
                    prepared_sig_post_obj_result = CreateSignature.do_activity(prepared_sig_post_obj, {})
                    # Backdating
                    update_timestamp('activities', prepared_sig_post_obj_result["activity_id"], generate_timestamp(row[column_index["date"]]))
                    update_timestamp('signatures', prepared_sig_post_obj_result["signature_id"], generate_timestamp(row[column_index["date"]]))

                    reviewed_sig_post_obj_result = CreateSignature.do_activity(reviewed_sig_post_obj, {})
                    # Backdating
                    update_timestamp('activities', reviewed_sig_post_obj_result["activity_id"], generate_timestamp(row[column_index["date"]]))
                    update_timestamp('signatures', reviewed_sig_post_obj_result["signature_id"], generate_timestamp(row[column_index["date"]]))

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
