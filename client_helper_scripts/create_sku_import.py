'''Create SKU's based on csv file'''
import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import get_tables, DATABASE, select_from_db
from activities.create_sku import CreateSKU
from utils import (update_timestamp)

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/create_sku_template.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["sku name"] = row.index("sku name")
            column_index["variety"] = row.index("variety")
            column_index["price"] = row.index("price")
            column_index["target qty"] = row.index("target qty")
            column_index["target unit"] = row.index("target unit")
            column_index["type"] = row.index("type")
            column_index["sales class"] = row.index("sales class")
            column_index["cannabis class"] = row.index("cannabis class")
            column_index["backdate date"] = row.index("backdate date")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:

            def get_variety(variety):
                params = {"variety": variety}
                query = '''
                   SELECT name FROM taxonomy_options 
                    WHERE taxonomy_id = (select id from taxonomies where name = 'varieties')
                    AND name = %(variety)s
                '''
                result = select_from_db(query, params)[0]['name'] if select_from_db(query, params) != [] else print('Variety not found: {0}'.format(variety))
                return result

            def get_sku_name(sku_name):
                params = {"sku_name": sku_name}
                query = '''
                   SELECT name FROM skus WHERE name = %(sku_name)s
                '''
                result = select_from_db(query, params)[0]['name'] if select_from_db(query, params) != [] else print('error to create SKU: {0}'.format(sku_name))
                return result
 

            try:
                sales_class = str(row[column_index['sales class']]).lower()
                price = round(float(row[column_index['price']]),2)
                target_qty = float(row[column_index['target qty']])
                target_qty_unit = str(row[column_index['target unit']]).lower()
                type = row[column_index['type']] if row[column_index['type']] == 'packaged' or row[column_index['type']] == 'unpackaged' else print('{0} is not type of sku'.format(row[column_index['type']]))
                date = datetime.strptime(row[column_index['backdate date']], '%Y-%m-%d') + timedelta(
                                hours=datetime.today().hour,
                                minutes=datetime.today().minute,
                                seconds=datetime.today().second
                            )

                if (get_sku_name(row[column_index['sku name']]) is None and get_variety(row[column_index['variety']]) is not None):
                    create_sku_payload = {
                        'organization_id': 1,
                        'created_by': 1,
                        'name': 'create_sku',
                        'price': price,
                        'sales_class': sales_class,
                        'sku_name': row[column_index['sku name']],
                        'target_qty': target_qty,
                        'target_qty_unit': target_qty_unit,
                        'to_status': 'enabled',
                        'type': type,
                        'variety': get_variety(row[column_index['variety']])
                    }

                    if (row[column_index['cannabis class']]):
                        create_sku_payload['cannabis_class'] = str(row[column_index['cannabis class']]).lower()

                    create_sku_result = CreateSKU.do_activity(create_sku_payload, {})
                    print('Create SKU ID: {0} - Activity ID: {1}'.format(create_sku_result['sku_id'], create_sku_result['activity_id']))

                    if (row[column_index['backdate date']]):
                        update_timestamp('skus', create_sku_result['sku_id'], date)
                        update_timestamp('activities', create_sku_result['activity_id'], date)

            except:
                DATABASE.dedicated_connection().rollback()
                print('error at creating SKU on create_sku_import')
                raise
    line_count += 1
cursor.close()
DATABASE.dedicated_connection().commit()