'''Create lot items based on csv file'''
import sys
import os
import csv
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import get_tables, DATABASE, select_from_db
from activities.create_lot_item import CreateLotItem
from activities.transfer_inventory import TransferInventory
from utils import (update_timestamp, get_sku)

cursor = DATABASE.dedicated_connection().cursor()

print('compiling data....')
with open('./template_client_helper_scripts/create lot item import.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["lot id"] = row.index("lot id")
            column_index["sku name"] = row.index("sku name")
            column_index["quantity"] = row.index("quantity")
            column_index["approved by"] = row.index("approved by")
            column_index["backdate date"] = row.index("backdate date")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            for i in range(int(row[column_index['quantity']])):

                def get_lot(inventory_id):
                    params = {"inventory_id": inventory_id}
                    query = '''
                        SELECT i.*, (
                                CASE 
                                    WHEN i.stats->'plants' > '0.0' THEN 'plants'
                                    WHEN i.stats->'seeds' > '0.0' THEN 'seeds'
                                    WHEN i.stats->'g-wet' > '0.0' THEN 'g-wet'
                                    WHEN i.stats->'g-dry'->'dry' > '0.0' THEN 'g-dry'
                                    WHEN i.stats->'g-dry'->'cured' > '0.0' THEN 'cured'
                                    WHEN i.stats->'g-oil'->'crude' > '0.0' THEN 'crude'
                                    WHEN i.stats->'g-oil'->'distilled' > '0.0' THEN 'distilled'
                                END
                            ) as inventory_unit,
                            (
                                CASE 
                                    WHEN i.stats->'plants' > '0.0' THEN i.stats->'plants'
                                    WHEN i.stats->'seeds' > '0.0' THEN i.stats->'seeds'
                                    WHEN i.stats->'g-wet' > '0.0' THEN i.stats->'g-wet'
                                    WHEN i.stats->'g-dry'->'dry' > '0.0' THEN i.stats->'g-dry'->'dry'
                                    WHEN i.stats->'g-dry'->'cured' > '0.0' THEN i.stats->'g-dry'->'cured'
                                    WHEN i.stats->'g-oil'->'crude' > '0.0' THEN i.stats->'g-oil'
                                    WHEN i.stats->'g-oil'->'distilled' > '0.0' THEN i.stats->'g-oil'->'distilled'
                                END
                            ) as inventory_qty
                        FROM inventories i 
                        WHERE i.id = %(inventory_id)s
                        AND i.type = 'lot'
                    '''
                    result = select_from_db(query, params)[0] if select_from_db(query, params) != [] else print('Inventory ID not found: {0}'.format(inventory_id))
                    return result


                def get_inventory_adjustment(lot_id, lot_item_id) -> object:
                    params = {"lot_id": lot_id, "lot_item_id": lot_item_id}
                    query = '''
                        SELECT id FROM activities
                        WHERE name = 'inventory_adjustment'
                        AND data ->> 'activity_name' = 'transfer_inventory'
                        AND cast(data ->> 'inventory_id' as numeric) IN (
                                SELECT id FROM inventories
                                WHERE id IN (%(lot_id)s, %(lot_item_id)s)
                                AND type IN ('lot', 'lot item')
                            )
                        ORDER BY id DESC
                        LIMIT 2
                    '''
                    result = select_from_db(query, params) if select_from_db(query, params) != [] else print('[Inventory Adjustment]: Lot: {0} - Lot Item: {1}'.format(lot_id, lot_item_id))
                    return result

                try:
                    ''' IMPORTANT '''
                    # It's necessary to comment the firing_webhooks method (Shopify integration) into create_lot_item activity

                    sku_rows = get_sku(row[column_index['sku name']])
                    lot_rows = get_lot(row[column_index['lot id']])
                    date = datetime.strptime(row[column_index['backdate date']], '%Y-%m-%d') + timedelta(
                                    hours=datetime.today().hour,
                                    minutes=datetime.today().minute,
                                    seconds=datetime.today().second
                                )

                    if (row[column_index['sku name']]):
                        if (lot_rows['inventory_qty'] >= sku_rows['target_qty'] and lot_rows['inventory_unit'] == sku_rows['target_qty_unit']):
                            create_lot_items_payload = {
                                'organization_id': 1,
                                'created_by': 1,
                                'approved_by': row[column_index['approved by']],
                                'from_inventory_id': row[column_index["lot id"]],
                                'name': 'create_lot_item',
                                'sku_id': sku_rows['id'],
                                'sku_name': row[column_index['sku name']],
                                'variety': sku_rows['variety']
                            }
                            create_lot_items_result = CreateLotItem.do_activity(create_lot_items_payload, {})
                            print('Activity ID: {0} - Lot Item ID: {1}'.format(create_lot_items_result['activity_id'], create_lot_items_result['inventory_id']))

                            transfer_inventory_payload = {
                                'organization_id': 1,
                                'created_by': 1,
                                'name': 'transfer_inventory',
                                'to_inventory_id': create_lot_items_payload['inventory_id'],
                                'from_inventory_id': row[column_index['lot id']],
                                'to_qty_unit': lot_rows['inventory_unit'],
                                'from_qty_unit': lot_rows['inventory_unit'],
                                'to_qty': sku_rows['target_qty'],
                                'from_qty': sku_rows['target_qty']
                            }
                            transfer_inventory_result = TransferInventory.do_activity(transfer_inventory_payload, {})
                            print('Activity ID: {0}'.format(transfer_inventory_result['activity_id']))

                            if (row[column_index['backdate date']]):
                                update_timestamp('inventories', create_lot_items_result['inventory_id'], date)
                                update_timestamp('activities', create_lot_items_result['activity_id'], date)
                                update_timestamp('activities', transfer_inventory_result['activity_id'], date)

                                for inventory_adjustment_activity_id in get_inventory_adjustment(lot_rows['id'], create_lot_items_result['inventory_id']):
                                    update_timestamp('activities', int(inventory_adjustment_activity_id['id']), date)
                        else:
                            print('[Error]: Lot ID: {0} contains: {1} - {2} and SKU expects {3} - {4}'.format(lot_rows['id'], lot_rows['inventory_qty'], lot_rows['inventory_unit'], sku_rows['target_qty'], sku_rows['target_qty_unit']))    
                    else:
                        print('Error when generating Lot Item')

                except:
                    DATABASE.dedicated_connection().rollback()
                    print('error at creating Lot Items on create_lot_items_import')
                    raise
    line_count += 1
cursor.close()
DATABASE.dedicated_connection().commit()