# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
import psycopg2
import psycopg2.extras
from db_functions import DATABASE
from utilities import select_from_db
from resource_functions import get_collection
from activities.order_add_item import OrderAddItem


from constants import USER_ID
from class_errors import DatabaseError


def get_skus_by_organization(organization_id):
    escaped_values = {}
    escaped_values["organization_id"] = organization_id
    
    query = '''
        SELECT s.id, s.name, s.variety, s.target_qty, s.target_qty_unit,
            (SELECT  COUNT(*) from inventories AS i WHERE i.organization_id = %(organization_id)s AND i.type = 'lot item' AND i.data->>'sku_name'=s.name) AS stock
        FROM skus AS s WHERE s.organization_id = %(organization_id)s
    '''
    
    return select_from_db(query,escaped_values)



def create_order_item(
    organization_id,
    order_id,
    sku,
    quantity
):
    try:
        order_item = {
            "organization_id": organization_id,
            "created_by": USER_ID,
            'name': 'order_add_item',
            'order_id': order_id,
            'sku_id': sku["id"],
            'sku_name': sku["name"],
            'shipment_id': '',
            'variety': sku["variety"],
            'to_qty': sku["target_qty"],
            'to_qty_unit': sku["target_qty_unit"],
            'quantity': quantity,
        }
        OrderAddItem.do_activity(order_item, {})
    except:
        print('error at creating order item on create_order_item')
        raise



