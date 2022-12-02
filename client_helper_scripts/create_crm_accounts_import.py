'''Creates CRM accounts in db based on given csv file'''

import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import get_tables, DATABASE
from class_errors import DatabaseError
from activities.create_crm_account import CreateCRMAccount

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/create crm accounts.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["name"] = row.index("name")
            column_index["type"] = row.index("type")
            column_index["email"] = row.index("email")
            column_index["address1"] = row.index("address1")
            column_index["address2"] = row.index("address2")
            column_index["city"] = row.index("city")
            column_index["province"] = row.index("province")
            column_index["postal_code"] = row.index("postal code")
            column_index["country"] = row.index("country")
            column_index["telephone"] = row.index("telephone")
            column_index["organization_id"] = row.index("organization_id")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            create_crm_post_obj = {
                'organization_id': row[column_index["organization_id"]],
                'created_by': 1,
                'name': "create_crm_account",
                'account_name': row[column_index["name"]],
                'account_type': row[column_index["type"]],
                'email':  row[column_index["email"]],
                'expiration_date': (datetime.today() + timedelta(days=365)).isoformat(),
                'fax': '',
                'residing_address': {
                    'address1': row[column_index["address1"]],
                    'address2': row[column_index["address2"]],
                    'city': row[column_index["city"]],
                    'province': row[column_index["province"]],
                    'postalCode': row[column_index["postal_code"]],
                    'country': row[column_index["country"]],
                    },
                'shipping_address': [{
                    'address1': row[column_index["address1"]],
                    'address2': row[column_index["address2"]],
                    'city': row[column_index["city"]],
                    'province': row[column_index["province"]],
                    'postalCode': row[column_index["postal_code"]],
                    'country': row[column_index["country"]],
                    }],
                'status': 'awaiting_approval',
                'telephone': row[column_index["telephone"]]
            }
            try:
                create_crm_result = CreateCRMAccount.do_activity(create_crm_post_obj, {})
                print('User ID: ', create_crm_result["crm_account_id"])
            except:
                print('error at create crm account on create_crm_accounts_import')
                raise 
            line_count += 1
cursor.close()
DATABASE.dedicated_connection().commit()
