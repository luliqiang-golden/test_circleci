'''Add multiple Orders as Shipped based on csv file'''
import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import get_tables, DATABASE, select_from_db
from activities.shipment_packaged import ShipmentPackaged
from activities.shipment_shipped import ShipmentShipped
from activities.shipment_update_shipped_date import ShipmentUpdateShippedDate
from utils import (get_order, get_shipment_id, update_timestamp)

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/mark_orders_as_shipped_template.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["order id"] = row.index("order id")
            column_index["shipped date"] = row.index("shipped date")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:

            def get_inventory_adjustment(shipment_id) -> object:
                params = {"shipment_id": shipment_id}
                query = '''
                    SELECT id FROM activities
                    WHERE name = 'inventory_adjustment'
                    AND data ->> 'activity_name' = 'shipment_shipped'
                    AND cast(data ->> 'inventory_id' as numeric) in (
                            SELECT i.id FROM order_items oi
                            INNER JOIN inventories i ON (i.data ->> 'order_item_id')::bigint = oi.id
                            AND i.type = 'lot item'
                            WHERE oi.shipment_id = %(shipment_id)s
	                    )
                '''
                result = select_from_db(query, params)
                if result == []:
                    print('No lot item found')
                return result

            try:
                ''' IMPORTANT '''
                # It's necessary to comment the firing_webhooks method (Shopify integration) into
                # shipment_packaged, shipment_shipped, shipment_update_shipped_date

                order_rows = get_order(row[column_index['order id']])
                shipment_id = get_shipment_id(row[column_index['order id']])
                shipped_date = datetime.strptime(row[column_index["shipped date"]], '%Y-%m-%d') + timedelta(
                                hours=datetime.today().hour,
                                minutes=datetime.today().minute,
                                seconds=datetime.today().second
                            )

                if (order_rows['shipping_status'] is not None and order_rows['shipping_status'] == 'pending' and order_rows['status'] == 'approved'):
                    shipment_packaged_payload = {
                        'organization_id': 1,
                        'created_by': 1,
                        'name': 'shipment_packaged',
                        'shipment_id': shipment_id,
                        'to_room': ''
                    }
                    shipment_packaged_result = ShipmentPackaged.do_activity(shipment_packaged_payload, {})
                    print('Shipment Packaged - Activity ID: ', shipment_packaged_result['activity_id'])

                    shipment_shipped_payload = {
                        'organization_id': 1,
                        'created_by': 1,
                        'name': 'shipment_shipped',
                        'shipment_id': shipment_id, 
                        'reduce_inventory': True
                    }
                    shipment_shipped_result = ShipmentShipped.do_activity(shipment_shipped_payload, {})
                    print('Shipment Shipped - Activity ID: ', shipment_shipped_result['activity_id'])

                    update_shipped_date_payload = {
                        'organization_id': 1,
                        'created_by': 1,
                        'name': 'shipment_update_shipped_date',
                        'shipment_id': shipment_id,
                        'to_shipped_date': datetime.strptime(row[column_index["shipped date"]], '%Y-%m-%d').isoformat()
                    }
                    update_shipped_date_result = ShipmentUpdateShippedDate.do_activity(update_shipped_date_payload, {})
                    print('Update Shipped - Activity ID: ', update_shipped_date_result['activity_id'])

                    if (row[column_index["shipped date"]]):
                        update_timestamp('activities', shipment_packaged_result["activity_id"], shipped_date)
                        update_timestamp('activities', shipment_shipped_result["activity_id"], shipped_date)
                        update_timestamp('activities', update_shipped_date_result["activity_id"], shipped_date)

                        for inventory_adjustment_activity_id in get_inventory_adjustment(shipment_id):
                            update_timestamp('activities', int(inventory_adjustment_activity_id['id']), shipped_date)
                else:
                    print('Order could not be Shipped')
            except:
                DATABASE.dedicated_connection().rollback()
                print('error at marking order as shipped on mark_orders_as_shipped_import')
                raise
    line_count += 1
cursor.close()
DATABASE.dedicated_connection().commit()