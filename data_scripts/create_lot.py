# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

import argparse
from db_functions import DATABASE
from constants import USER_ID
from datetime import datetime, timedelta
from random import randint, sample
from utilities import get_random_user, get_random_date_before_today, select_from_db, update_timestamp
from shared_activities import update_room, transfer_inventory, propagate_cuttings, create_signature
from activities.create_mother import CreateMother
import psycopg2
import psycopg2.extras
from psycopg2 import sql

from activities.create_lot import CreateLot
from activities.create_lot_item import CreateLotItem



def create_lots(org_id):    
    try:
        lot_data = get_lot_data(org_id)

        for data in lot_data:
            create_lot(org_id,  data["qa_start_date"],  data["variety"], data["batch_id"], data["total_weight"], data["production_type"])

    except:
        print('error creating lots on create_lot ')
        raise

def get_sku_name(org_id, variety, target_qty_unit):
    escaped_values = {}
    escaped_values["organization_id"] = org_id
    escaped_values["variety"] = variety
    escaped_values['target_qty_unit'] = target_qty_unit

    query = '''
        SELECT name from skus WHERE organization_id = %(organization_id)s AND variety = %(variety)s AND target_qty_unit = %(target_qty_unit)s
    '''
    
    return select_from_db(query,escaped_values)



def get_lot_data(org_id):
    params = {'organization_id': org_id}
    query = '''        
        select *, id as batch_id, variety,
		case
			when stats#>>'{g-oil,distilled}'>'0' then cast(stats#>>'{g-oil,distilled}' as float)
			when stats#>>'{g-dry,dry}'>'0' then cast(stats#>>'{g-dry,dry}' as float)
		end total_weight,
		case
			when stats#>>'{g-oil,distilled}'>'0' then 'distilled'
			when stats#>>'{g-dry,dry}'>'0' then 'dry'
		end production_type,
        timestamp as qa_start_date
        from inventories
        where organization_id = %(organization_id)s and type = 'batch' and 
        attributes->>'stage'='qa' and data#>>'{plan,end_type}' in ('dry', 'distilled') and 
        (stats#>>'{g-dry,dry}'>'0.0' or stats#>>'{g-oil,distilled}'>'0.0')
    '''
    
    return select_from_db(query, params)


def create_lot(org_id, qa_start_date, variety, batch_id, total_weight, production_type):
    
    # MOVE TO LOT
    qa_end_date = qa_start_date + timedelta(days=15)
    lot_start_date = qa_end_date

    lot_data = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": 'create_lot',
        "variety": variety,
        "from_inventory_id": batch_id,
    }

    result_lot = CreateLot.do_activity(lot_data, {})
    update_timestamp('inventories', result_lot["inventory_id"], qa_end_date)
    update_timestamp('activities', result_lot["activity_id"], qa_end_date)
    transfer_inventory(org_id, batch_id, result_lot["inventory_id"], variety, qa_end_date, total_weight, qty_unit=production_type)
    print("lot id {} created, from id {}".format(result_lot["inventory_id"], batch_id))

    lot_item_qty = 0

    # CREATE LOT ITEMS
    for i in range(1, 6):
        sku_qty = randint(1,30)
        lot_item_qty += sku_qty
        approved_by_user = get_random_user(org_id)

        sku_name = get_sku_name(org_id, variety, production_type)

        lot_item_data = {
            "organization_id": org_id,
            "created_by": USER_ID,
            "name": "create_lot_item",
            "from_inventory_id": result_lot["inventory_id"],
            "variety": variety,
            "approved_by": approved_by_user["email"],
            "sku_name": sku_name[0]['name'],
        }

        if lot_item_qty < total_weight:
            result_lot_item = CreateLotItem.do_activity(lot_item_data, {})
            update_timestamp('inventories', result_lot_item["inventory_id"], qa_end_date)
            update_timestamp('activities', result_lot_item["activity_id"], qa_end_date)
            create_signature(
                org_id, result_lot_item['activity_id'], "approved_by", approved_by_user["id"], qa_end_date)
            transfer_inventory(org_id, result_lot["inventory_id"], result_lot_item["inventory_id"], variety, qa_end_date, sku_qty, production_type, 2)
            print("lot item id {} created, from id {} - stats: {}, qty: {}".format(result_lot_item["inventory_id"], result_lot["inventory_id"], production_type, sku_qty))
        


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")  

    if (organization_id):
        DATABASE.dedicated_connection().begin()
        try:        
            create_lots(organization_id)
            DATABASE.dedicated_connection().commit()
        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
            print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
            DATABASE.dedicated_connection().rollback()
