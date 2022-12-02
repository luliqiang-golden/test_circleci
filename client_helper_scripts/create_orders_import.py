'''Creates Orders based on csv file'''
import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import get_tables, DATABASE
from activities.create_order import CreateOrder
from utils import (check_order_type, get_crm_account_id, get_shipping_address, update_timestamp)

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/create_orders_template.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["crm account name"] = row.index("crm account name")
            column_index["shipping address"] = row.index("shipping address")
            column_index["order placed by"] = row.index("order placed by")
            column_index["order placed date"] = row.index("order placed date")
            column_index["order type"] = row.index("order type")
            column_index["order due date"] = row.index("order due date")
            column_index["backdate date"] = row.index("backdate date")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            order_due_date = datetime.strptime(row[column_index["order due date"]], '%Y-%m-%d').isoformat() if row[column_index["order due date"]] != '' else ''
            create_order_payload = {
                'organization_id': 1,
                'created_by': 1,
                'name': "create_order",
                'crm_account_name': row[column_index["crm account name"]],
                'crm_account_id': get_crm_account_id(row[column_index["crm account name"]]),
                'shipping_address': get_shipping_address(row[column_index["crm account name"]], row[column_index["shipping address"]]),
                'order_placed_by': row[column_index["order placed by"]],
                'order_received_date': datetime.strptime(row[column_index["order placed date"]], '%Y-%m-%d').isoformat(),
                'order_type': check_order_type(row[column_index["order type"]]),
                'due_date': order_due_date,
                'shipping_status': 'pending',
                'status': 'awaiting_approval',
            }
            try:
                # It's necessary to comment the firing_webhooks method (Shopify integration) into create_orders activity
                create_order_result = CreateOrder.do_activity(create_order_payload, {})

                if (row[column_index["backdate date"]]):
                    date = datetime.strptime(row[column_index["backdate date"]], '%Y-%m-%d') + timedelta(
                        hours=datetime.today().hour,
                        minutes=datetime.today().minute,
                        seconds=datetime.today().second
                    )
                    update_timestamp('orders', create_order_result["order_id"], date)
                    update_timestamp('activities', create_order_result["activity_id"], date)

                print('Create Order Activity ID: ', create_order_result["activity_id"], 'Order ID: ', create_order_result["order_id"])
            except:
                print('error at create order on create_orders_import')
                raise
            line_count += 1
cursor.close()
DATABASE.dedicated_connection().commit()
