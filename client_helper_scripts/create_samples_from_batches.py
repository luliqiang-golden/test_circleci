'''Create lot items based on csv file'''
import sys
import os
import csv
from datetime import datetime, timedelta


sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import get_tables, DATABASE, select_from_db
from activities.batch_create_sample import BatchCreateSample
from activities.create_signature import CreateSignature
from activities.transfer_inventory import TransferInventory
from utils import generate_timestamp, get_inventory_adjustment_activity_id, get_received_inventory_adjustment_activity_id, get_user_id_by_name, update_timestamp, get_variety_taxonomy_option_id

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/create samples import.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        print(row)
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["from_inventory_id"] = row.index("from_inventory_id")
            column_index["sampled_by"] = row.index("sampled_by")
            column_index["approved_by"] = row.index("approved_by")
            column_index["quantity"] = row.index("quantity")
            column_index["product_type"] = row.index("product_type")
            column_index["date"] = row.index("date")
            column_index["variety"] = row.index("variety")
            column_index["organization_id"] = row.index("organization_id")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            
            try:
                create_sample_data = {
                    "organization_id": row[column_index['organization_id']],
                    "created_by": 1,
                    "name": "batch_create_sample",
                    "from_inventory_id": row[column_index['from_inventory_id']],
                    "sampled_by": row[column_index['sampled_by']],
                    "variety": row[column_index['variety']],
                    "approved_by": row[column_index['approved_by']],
                    "to_test_status": "batch-create-sample",
                    "batch_in_qa": False,
                    "to_qty": row[column_index['quantity']],
                    "to_qty_unit": row[column_index['product_type']],
                    "from_qty": row[column_index['quantity']],
                    "from_qty_unit": row[column_index['product_type']],
                    "related_inventory_id": row[column_index['from_inventory_id']],
                }
                
                result_sample = BatchCreateSample.do_activity(create_sample_data, {})
                update_timestamp('activities', result_sample['activity_id'], generate_timestamp(row[column_index["date"]]))
                    
                    
            except:
                print('error creating sample on create_sample')
                raise
    line_count += 1
cursor.close()
DATABASE.dedicated_connection().commit()