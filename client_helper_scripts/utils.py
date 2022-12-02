'''General utility functions for client_helper_scripts'''
import os
import sys
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
from psycopg2 import sql

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from class_errors import DatabaseError
from db_functions import execute_query_into_db, select_from_db, get_tables, NO_DATA_COLUMNS_TABLES, TABLE_COLUMNS, DATABASE


def generate_timestamp(date):
    '''Generates timestamp based on given date'''
    datetime_obj = datetime.strptime(date, '%d-%m-%Y')
    return datetime_obj + timedelta(hours=datetime.today().hour, minutes=datetime.today().minute, seconds=datetime.today().second)


def update_timestamp(table, id, timestamp, column=None):
    '''Updates timestamp based on given table name, id and timestamp'''
    time = timestamp
    params = {"timestamp": time, "id": id}
    col = 'timestamp' if column is None else column

    try:
        query = "UPDATE {0} SET {1} =%(timestamp)s WHERE id=%(id)s".format(table, col)
        result = execute_query_into_db(query, params)
    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_resource_error",
                "message": error.args[0]
            }, 500)
    return print("Backdate success. Affected rows: ", result['affected_rows'])


def get_received_inventory_adjustment_activity_id(inventory_id, start_type):
    '''returns inventory_adjustment activity_id for received_inventory type activity, by given inventory_id'''
    params = {"inv_id": inventory_id, "start_type": start_type}
    query = '''
        SELECT id FROM activities
        WHERE
        name = 'inventory_adjustment'
        AND
        CAST(data->>'inventory_id' AS INTEGER) = %(inv_id)s
        AND
        data->>'activity_name' = 'transfer_inventory'   
    '''
    return select_from_db(query, params)[0]['id']


def get_inventory_adjustment_activity_id(inventory_id, activity_name=None):
    '''returns inventory_adjustment activity_id  from given inventory_id'''
    params = {"inv_id": inventory_id}
    act_name = 'transfer_inventory' if activity_name is None else activity_name
    query = '''
        SELECT id FROM activities
        WHERE
        name = 'inventory_adjustment'
        AND
        CAST(data->>'inventory_id' AS INTEGER) = %(inv_id)s
        AND
        data->>'activity_name' = '{0}'
    '''.format(act_name)
    return select_from_db(query, params)[0]['id']


def get_variety_taxonomy_option_id(v_name, organization_id):
    '''Returns variety id by given variety name'''
    params = {"variety_name": v_name,
              "organization_id": organization_id}
    query = '''SELECT id FROM taxonomy_options WHERE name = %(variety_name)s and organization_id = %(organization_id)s'''
    return select_from_db(query, params)[0]['id']


def get_user_id_by_name(name):
    '''Returns user id by given user name'''
    params = {"user_name": name}
    get_user_query = '''SELECT id FROM users WHERE name = %(user_name)s'''
    return select_from_db(get_user_query, params)[0]['id']


def get_user_role_id(role):
    '''Returns role_id based on given role name'''
    params = {"role_name": role}
    user_role_id_query = '''SELECT id FROM roles WHERE name = %(role_name)s '''
    return select_from_db(user_role_id_query, params)[0]['id']


def get_variety_taxonomy_id(organization_id):
    '''Returns variety id'''
    params = {"organization_id": organization_id}
    variety_taxonomy_id_query = '''SELECT id FROM taxonomies WHERE name = 'varieties' and organization_id = %(organization_id)s''' 
    return select_from_db(variety_taxonomy_id_query, params)[0]['id']


def check_variety_exists(variety_name, organization_id):
    '''Checks if variety exists'''
    params = {'name': variety_name, 'organization_id': organization_id}
    check_variety_query = '''SELECT name from taxonomy_options WHERE name =%(name)s and organization_id = %(organization_id)s'''
    res = select_from_db(check_variety_query, params)
    if res:
        return True
    return False


def get_crm_account_id(account_name, organization_id):           
    '''Returns crm_account_id based on given account name'''
    params = {"crm_name": account_name,
              "organization_id": organization_id}
    crm_id_query = '''SELECT id from crm_accounts WHERE name = %(crm_name)s and organization_id = %(organization_id)s'''
    crm_id_result = select_from_db(crm_id_query, params)

    if crm_id_result != []:
        return crm_id_result[0]['id']
    else:
        print('CRM Account Name does not match: {0}'.format(account_name))


def get_shipping_address(account_name, shipping_address):
    '''Returns shipping address based on given account name'''
    params = {"crm_name": account_name}
    shipping_address_query = '''
        SELECT jsonb_array_elements(data -> 'shipping_address') as shipping_address
        FROM crm_accounts
        WHERE name = %(crm_name)s'''
    shipping_addresses = select_from_db(shipping_address_query, params)

    for address in shipping_addresses:
        string_formatted = "{0}, {1} {2} {3} {4}".format(
            address['shipping_address']['address1'],
            address['shipping_address']['city'],
            address['shipping_address']['province'],
            address['shipping_address']['postalCode'],
            address['shipping_address']['country']
        )

        if shipping_address == string_formatted:
            if address['shipping_address']['address2'] is not None:
                return address['shipping_address']
            else:
                return {
                    "city": address['shipping_address']['city'],
                    "country": address['shipping_address']['country'],
                    "address1": address['shipping_address']['address1'],
                    "address2": "",
                    "province": address['shipping_address']['province'],
                    "postalCode": address['shipping_address']['postalCode']
                }
        else:
            print('shipping address does not match the address entered: {0} != {1}'.format(shipping_address, string_formatted))


def check_order_type(order_type):
    '''Checks if the order type entered is valid '''
    order_type_formatted = order_type.lower()
    params = {"order_type": order_type_formatted}
    order_type_query = '''
        SELECT distinct(sales_class)
        FROM skus
        WHERE sales_class = %(order_type)s'''
    order_type_result = select_from_db(order_type_query, params)[0]

    if order_type_formatted == order_type_result['sales_class']:
        return order_type_result['sales_class']
    else:
        print('the order type was not found in the database')


def get_sku(sku_name):
    '''Returns sku row based on given sku name'''
    params = {"sku_name": sku_name}
    sku_query = '''SELECT * from skus WHERE name = %(sku_name)s'''
    return select_from_db(sku_query, params)[0]


def get_unit_price(sku_id):
    '''Check price received with sku price through id'''
    params = {"sku_id": sku_id}
    sku_query = '''SELECT price from skus WHERE id = %(sku_id)s'''
    price_result = select_from_db(sku_query, params)[0]['price']
    return round(float(price_result),2)


def get_inventory_range(sku_name, quantity) -> object:
    '''Returns inventories rows based on given id range'''
    params = {"sku_name": sku_name, "quantity": quantity}
    inventory_range_query = '''
        SELECT * FROM inventories
        WHERE type = 'lot item'
        AND id BETWEEN (select min(id) from inventories) 
        AND (select max(id) from inventories)
        AND data ->> 'sku_name' = %(sku_name)s
        AND data ->> 'order_item_id' isnull
        ORDER BY id ASC
        LIMIT %(quantity)s
    '''
    inventory_range_result = select_from_db(inventory_range_query, params)
    if inventory_range_result == []:
        print('No lot item found')
    return inventory_range_result

def get_inventory_count(sku_name) -> int:
    '''Returns quantity available in stock rows based on given sku_name'''
    params = {"sku_name": sku_name}
    inventory_count_query = '''
        SELECT COUNT(*) as quantity FROM inventories
        WHERE type = 'lot item'
        AND data ->> 'sku_name' = %(sku_name)s
        AND data ->> 'order_item_id' isnull
    '''
    inventory_count_result = select_from_db(inventory_count_query, params)
    if inventory_count_result == []:
        print('No lot item found')
    return inventory_count_result[0]['quantity']

def get_filled_inventory_count(sku_name) -> int:
    '''Returns quantity filled in lot items rows based on given sku_name'''
    params = {"sku_name": sku_name}
    inventory_count_query = '''
        SELECT COUNT(*) as quantity FROM inventories
        WHERE type = 'lot item'
        AND data ->> 'sku_name' = %(sku_name)s
        AND data ->> 'order_item_id' notnull
    '''
    inventory_count_result = select_from_db(inventory_count_query, params)
    if inventory_count_result == []:
        print('No lot item found')
    return inventory_count_result[0]['quantity']

def get_shipment_id(order_id):
    '''Returns shipment_id based on given order_id'''
    params = {"order_id": order_id}
    shipment_id_query = '''
        SELECT s.id FROM shipments s
        INNER JOIN order_items oi ON oi.shipment_id = s.id
        INNER JOIN orders o ON o.id = oi.order_id
        WHERE s.status = 'pending'
        AND o.shipping_status = 'pending'
        AND o.status = 'approved'
        AND o.id = %(order_id)s
    '''
    shipment_id_result = select_from_db(shipment_id_query, params)
    if shipment_id_result != []:
        return select_from_db(shipment_id_query, params)[0]['id']


def get_order(order_id):
    
    '''Returns all orders columns based on given order_id'''
    params = {"order_id": order_id}
    order_id_query = '''
        SELECT * FROM orders WHERE id = %(order_id)s
    '''
    return select_from_db(order_id_query, params)[0]
