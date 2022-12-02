'''Transfers received inventory to batch based on given csv file'''
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411
import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import select_from_db, get_tables, DATABASE
from class_errors import DatabaseError
from activities.create_batch import CreateBatch
from activities.batch_plan_update import BatchPlanUpdate
from activities.update_room import UpdateRoom
from activities.update_stage import UpdateStage
from activities.transfer_inventory import TransferInventory
from activities.create_signature import CreateSignature
from utils import (generate_timestamp, update_timestamp, get_received_inventory_adjustment_activity_id, 
                    get_inventory_adjustment_activity_id, get_variety_taxonomy_option_id, get_user_id_by_name)


#This function needs a proper revemp. Currently this can only work with start type = seeds/plants and end type = dry/cured
def get_batch_plan_timeline(start_type, end_type):
    ''''''
    head = {'name': 'planning', "planned_length": None}
    tail = {'name': 'qa', "planned_length": None}
    batchPlan = {
        'germinating': {'name': 'germinating', "planned_length": None},
        'propagation': {'name': 'propagation', "planned_length": None},
        'vegetation':  {'name': 'vegetation', "planned_length": None},
        'flowering': {'name': 'flowering', "planned_length": None},
        'harvesting': {'name': 'harvesting', "planned_length": None},
        'drying': {'name': 'drying', "planned_length": None},
        'curing': {'name': 'curing', "planned_length": None},
        'extracting_crude_oil': {'name': 'extracting_crude_oil', "planned_length": None},
        'distilling': {'name': 'distilling', "planned_length": None},
    }
    
    if(start_type == end_type and start_type != 'plants'):
        return [head, tail]
    
    timeline = {}
    
    timeline['seeds_to_seeds'] = [head, tail]
    timeline['seeds_to_plants'] = [head, batchPlan['germinating'], batchPlan['propagation'], batchPlan['vegetation'], tail]
    timeline['seeds_to_g-wet'] = [head, batchPlan['germinating'], batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], tail]
    timeline['seeds_to_dry'] = [head, batchPlan['germinating'], batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], batchPlan['drying'], tail]
    timeline['seeds_to_cured'] = [head, batchPlan['germinating'], batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], batchPlan['drying'], batchPlan['curing'], tail]
    timeline['seeds_to_crude'] = [head, batchPlan['germinating'], batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], batchPlan['extracting_crude_oil'], tail]
    timeline['seeds_to_distilled'] = [head, batchPlan['germinating'], batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], batchPlan['extracting_crude_oil'], batchPlan['distilling'], tail]
    
    timeline['plants_to_plants'] = [head, batchPlan['propagation'], batchPlan['vegetation'], tail]
    timeline['plants_to_g-wet'] = [head, batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], tail]
    timeline['plants_to_dry'] = [head, batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], batchPlan['drying'], tail]
    timeline['plants_to_cured'] = [head, batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], batchPlan['drying'], batchPlan['curing'], tail]
    timeline['plants_to_crude'] = [head, batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], batchPlan['extracting_crude_oil'], tail]
    timeline['plants_to_distilled'] = [head, batchPlan['propagation'], batchPlan['vegetation'], batchPlan['flowering'], batchPlan['harvesting'], batchPlan['extracting_crude_oil'], batchPlan['distilling'], tail]
    
    timeline['g-wet_to_g-wet'] = [head, tail]
    timeline['g-wet_to_dry'] = [head, batchPlan['drying'], tail]
    timeline['g-wet_to_cured'] = [head, batchPlan['drying'], batchPlan['curing'], tail]
    timeline['g-wet_to_crude'] = [head, batchPlan['extracting_crude_oil'], tail]
    timeline['g-wet_to_distilled'] = [head, batchPlan['extracting_crude_oil'], batchPlan['distilling'], tail]
    
    timeline['dry_to_dry'] = [head, tail]
    timeline['dry_to_cured'] = [head, batchPlan['curing'], tail]
    timeline['dry_to_crude'] = [head, batchPlan['extracting_crude_oil'], tail]
    timeline['dry_to_distilled'] = [head, batchPlan['extracting_crude_oil'], batchPlan['distilling'], tail]
    
    timeline['cured_to_cured'] = [head, tail]
    timeline['cured_to_crude'] = [head, batchPlan['extracting_crude_oil'], tail]
    timeline['cured_to_distilled'] = [head, batchPlan['extracting_crude_oil'], batchPlan['distilling'], tail]
    
    timeline['crude_to_crude'] = [head, tail]
    timeline['crude_to_distilled'] = [head, batchPlan['distilling'], tail]
    
    timeline['distilled_to_distilled'] = [head, tail]
    
    return timeline[start_type + '_to_' + end_type]

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/transfer to batch.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["variety"] = row.index("variety")
            column_index["custom_name"] = row.index("custom name")
            column_index["scale_name"] = row.index("scale name")
            column_index["start_type"] = row.index("start type")
            column_index["end_type"] = row.index("end type")
            column_index["to_room"] = row.index("room")
            column_index["from_inventory_id"] = row.index("received inventory id")
            column_index["from_qty"] = row.index("transfer qty")
            column_index["approved_by"] = row.index("approved")
            column_index["prepared_by"] = row.index("prepared")
            column_index["reviewed_by"] = row.index("reviewed")
            column_index["date"] = row.index("date")
            column_index["organization_id"] = row.index("organization_id")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            # Create batch
            create_batch_result = {}
            create_batch_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "create_batch",
                'custom_name': row[column_index["custom_name"]] if len(row[column_index["scale_name"]] ) != 0 else None,
                'scale_name':  row[column_index["scale_name"]] if len(row[column_index["scale_name"]] ) != 0 else None,
                'variety': row[column_index["variety"]],
                'variety_id': get_variety_taxonomy_option_id(row[column_index["variety"]], row[column_index["organization_id"]]),
            }

            try:
                create_batch_result = CreateBatch.do_activity(create_batch_post_obj, {})
                print('inventory_id: ', create_batch_result["inventory_id"])
            except:
                print('error at create batch on transfer_to_batch_import')
                raise 
            # Backdating
            update_timestamp('inventories', create_batch_result["inventory_id"], generate_timestamp(row[column_index["date"]]))
            update_timestamp('activities', create_batch_result["activity_id"], generate_timestamp(row[column_index["date"]]))

            # Batch Plan update
            plan_update_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "batch_plan_update",
                'inventory_id': create_batch_result["inventory_id"],
                'plan': {
                    'end_type': row[column_index["end_type"]],
                    'start_date': datetime.today().isoformat(),
                    'start_type': row[column_index["start_type"]],
                    'timeline': get_batch_plan_timeline(start_type=row[column_index["start_type"]], end_type=row[column_index["end_type"]])
                }
            }

            try:
                plan_update_result = BatchPlanUpdate.do_activity(plan_update_post_obj, {})
                print('Batch Plan Update Activity Id: ', plan_update_result["activity_id"])
            except:
                print('error at batch plan update on transfer_to_batch_import')
                raise
            # Backdating
            update_timestamp('activities', plan_update_result["activity_id"], generate_timestamp(row[column_index["date"]]))

            # Update Room
            update_room_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "update_room",
                'inventory_id': create_batch_result["inventory_id"],
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

            # Update Stage
            update_stage_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "update_stage",
                'inventory_id': create_batch_result["inventory_id"],
                'to_stage': 'planning'   
            }
            try:
                update_stage_result = UpdateStage.do_activity(update_stage_post_obj, {})
                print('Update Stage Activity Id: ', update_stage_result["activity_id"])
            except:
                print('error at Update Stage on transfer_to_batch_import')
                raise
            # Backdating
            update_timestamp('activities', update_stage_result["activity_id"], generate_timestamp(row[column_index["date"]]))

            # Transfer Inventory
            transfer_inv_result = {}
            transfer_inventory_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "transfer_inventory",
                'to_inventory_id': create_batch_result["inventory_id"],
                'from_inventory_id': row[column_index["from_inventory_id"]],
                'to_qty_unit': row[column_index["start_type"]],
                'from_qty_unit': row[column_index["start_type"]],
                'to_qty': row[column_index["from_qty"]],
                'from_qty': row[column_index["from_qty"]],
                'approved_by': row[column_index["approved_by"]],
                'prepared_by': row[column_index["prepared_by"]],
                'reviewed_by': row[column_index["reviewed_by"]],
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
            received_inventory_adjustment_activity_id = get_received_inventory_adjustment_activity_id(row[column_index["from_inventory_id"]], row[column_index["start_type"]])
            update_timestamp('activities', received_inventory_adjustment_activity_id, generate_timestamp(row[column_index["date"]]))

            # Get batch inventory adjustment activity id and backdate it
            batch_inventory_adjustment_activity_id = get_inventory_adjustment_activity_id(create_batch_result["inventory_id"])
            update_timestamp('activities', batch_inventory_adjustment_activity_id, generate_timestamp(row[column_index["date"]]))

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
