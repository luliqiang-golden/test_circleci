'''Add multiple Orders Items based on csv file'''
import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import get_tables, DATABASE, update_into_db, update_resource_attribute_into_db
from activities.order_add_item import OrderAddItem
from activities.order_update_status import OrderUpdateStatus
from activities.create_shipment import CreateShipment
from activities.order_item_add_shipment import OrderItemAddShipment
from activities.order_item_map_to_lot_item import OrderItemMapToLotItem
from utils import (get_filled_inventory_count, get_unit_price, get_inventory_count, 
get_inventory_range, get_order, get_shipment_id, get_sku, update_timestamp)

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/order_add_multiple_items_template.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["order id"] = row.index("order id")
            column_index["sku name"] = row.index("sku name")
            column_index["quantity"] = row.index("quantity")
            column_index["backdate date"] = row.index("backdate date")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            # Order Item
            sku_rows = get_sku(row[column_index["sku name"]])
            order_rows = get_order(row[column_index['order id']])
            quantity_available = get_inventory_count(row[column_index["sku name"]])
            reserved = get_filled_inventory_count(row[column_index["sku name"]])

            if (row[column_index['backdate date']]):
                date = datetime.strptime(row[column_index["backdate date"]], '%Y-%m-%d') + timedelta(
                                hours=datetime.today().hour,
                                minutes=datetime.today().minute,
                                seconds=datetime.today().second
                            )

            order_item_payload = {
                'organization_id': 1,
                'created_by': 1,
                'name': 'order_add_item',
                'order_id': row[column_index['order id']],
                'sku_name': row[column_index['sku name']],
                'sku_id': sku_rows['id'],
                'to_qty': 1,
                'to_qty_unit': sku_rows['target_qty_unit'],
                'variety': sku_rows['variety'],
                'quantity': int(row[column_index['quantity']]),
                'price': get_unit_price(sku_rows['id']),
                'shipment_id': '',
                'status': '',
                'include_tax': True,
            }

            # Order Stutus
            order_status_payload = {
                'organization_id': 1,
                'created_by': 1,
                'name': 'order_update_status',
                'order_id': row[column_index['order id']],
                'timestamp': datetime.today().isoformat(),
                'to_status': 'approved'
            }

            # New Shipment Payload
            new_shipment_payload = {
                'organization_id': 1,
                'created_by': 1,
                'name': 'create_shipment',
                'crm_account_id': order_rows['crm_account_id'],
                'status': 'pending',
                'shipping_address': order_rows['shipping_address']
            }

            def get_shipment(order_item_id):
                try:
                    if get_shipment_id(row[column_index['order id']]) is None:
                        result = CreateShipment.do_activity(new_shipment_payload, {})

                        if (row[column_index["backdate date"]]):
                            update_timestamp('shipments', result["shipment_id"], date)
                            update_timestamp('activities', result["activity_id"], date)

                        shipment_id = result['shipment_id']
                    else:
                        shipment_id = get_shipment_id(row[column_index['order id']])

                    # Get Shipment Payload
                    shipment_payload = {
                        'organization_id': 1,
                        'created_by': 1,
                        'name': 'order_item_add_shipment',
                        'shipment_id': shipment_id,
                        'order_item_id': order_item_id,
                        'quantity_filled': int(row[column_index['quantity']]),
                    }
                    result = OrderItemAddShipment.do_activity(shipment_payload, {})

                    if (row[column_index["backdate date"]]):
                        update_timestamp('activities', result["activity_id"], date)

                    return result
                except:
                    DATABASE.dedicated_connection().rollback()
                    print('Error in get_shipment')
                    raise

            def update_lot_item(inventory_id, order_item_id):              
                try:
                    # Update order item with lot item
                    update_order_item = {
                        'organization_id': 1,
                        'created_by': 1,
                        'name': 'order_item_map_to_lot_item',
                        'order_item_id': order_item_id,
                        'inventory_id': inventory_id,
                    }
                    print('Order Item {0} added to Lot Item {1}'.format(order_item_id, inventory_id))
                    result = OrderItemMapToLotItem.do_activity(update_order_item, {})

                    if (row[column_index["backdate date"]]):
                        update_timestamp('activities', result["activity_id"], date)
                    return result
                except:
                    DATABASE.dedicated_connection().rollback()
                    print('error at filling order item')
                    raise

            try:
                if (quantity_available >= int(row[column_index['quantity']]) and int(row[column_index['quantity']]) > 0):
                    ''' IMPORTANT '''
                    # It's necessary to comment the firing_webhooks method (Shopify integration) into create_orders,
                    # create_invoice, create_shipment, order_add_item, order_item_add_shipment, order_item_map_to_lot_item,
                    # order_update_status activities
                    order_item_result = OrderAddItem.do_activity(order_item_payload, {})

                    if (row[column_index["backdate date"]]):
                        update_timestamp('order_items', order_item_result["order_item_id"], date)
                        update_timestamp('activities', order_item_result["activity_id"], date)

                    print('Create Order Item Activity ID: ', order_item_result['activity_id'], 'Order Item ID: ', order_item_result['order_item_id'])

                    if order_rows['status'] == 'awaiting_approval' and not 'invoice_id' in order_rows['data']:
                        order_status_result = OrderUpdateStatus.do_activity(order_status_payload, {})

                        if (row[column_index["backdate date"]]):
                            update_timestamp('activities', order_status_result["activity_id"], date)

                        print('Update Status Activity ID: ', order_status_result['activity_id'])
                    elif order_item_payload['status'] == 'awaiting_approval' or order_item_payload['status'] == '' and 'invoice_id' in order_rows['data']:
                        order_status_result = update_into_db('order_items', order_item_result['order_item_id'], {'status': 'approved'})
                    else:
                        print('Error Updating Order Status')

                    get_shipment(order_item_result['order_item_id'])

                    for inventory in get_inventory_range(row[column_index['sku name']], row[column_index['quantity']]):
                        update_lot_item(inventory['id'], order_item_result['order_item_id'])
                else:
                    DATABASE.dedicated_connection().rollback()
                    print('The quantity in stock for sku {0} is {1} less than ordered {2}'.format( sku_rows['name'], quantity_available, row[column_index['quantity']]))
            except:
                DATABASE.dedicated_connection().rollback()
                print('error at create order on order_add_multiple_items_import')
                raise
            finally:
                available = get_inventory_count(row[column_index["sku name"]])
                reserved = get_filled_inventory_count(row[column_index["sku name"]])

                update_resource_attribute_into_db('skus', sku_rows['id'], 'reserved', reserved)
                update_into_db('skus', sku_rows['id'], {'current_inventory': available})

                print('UPDATED STOCK: name: {0}, available: {1}, reserved: {2}'.format(sku_rows['name'], available, reserved))
    line_count += 1
cursor.close()
DATABASE.dedicated_connection().commit()
