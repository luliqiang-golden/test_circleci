'''Creates users in db based on given csv file'''
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411

import sys
import os
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import get_tables, DATABASE
from class_errors import DatabaseError
from activities.user_create import CreateUser
from utils import get_user_role_id

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/create user.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["user_name"] = row.index("name")
            column_index["email"] = row.index("email")
            column_index["role"] = row.index("role")
            column_index["job_title"] = row.index("job_title")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            create_user_post_obj = {
                'organization_id': 1,
                'created_by': 1,
                'name': "user_create",
                'user_name': row[column_index["user_name"]],
                'email':  row[column_index["email"]],
                'role_id': get_user_role_id(row[column_index["role"]]),
                'job_title': row[column_index["job_title"]],
                'enabled': True,
            }
            try:
                create_user_result = CreateUser.do_activity(create_user_post_obj, {})
                print('User ID: ', create_user_result["user_id"])
            except:
                print('error at create user on createuser__import')
                raise 
cursor.close()
DATABASE.dedicated_connection().commit()
