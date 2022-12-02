# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
import psycopg2
import psycopg2.extras
import json
import datetime
import copy

from constants import USER_ID
from class_errors import DatabaseError
from datetime import datetime
from utilities import select_from_db, get_random_user
from shared_activities import create_signature

from activities.queue_for_destruction import QueueForDestruction
from activities.destroy_material import DestroyMaterial


def create_destructions(org_id):
    batches = get_batches_data(org_id)
    destruction_inventories = []

    for batch in batches:
        batch_id = batch['id']
        variety = batch['variety']
        room = batch['attributes']['room']
        type_of_waste = 'leaves'
        reason = 'Harverst trimmings'
        # create a sample using 5% of the total quantity in a batch
        from_qty = int(0.05 * float(batch['stats']['plants']))
        from_qty_unit = 'plants'
        destroyed_qty_unit = 'g-wet'
        timestamp = batch['timestamp']
        result = create_queue_for_destruction(
            org_id, batch_id, variety, room, type_of_waste, reason, from_qty, from_qty_unit, destroyed_qty_unit, timestamp)
        destruction_inventories.append(result)

    destruction_inventories.pop(0)
    destruction_inventories.pop(0)
    destroy_material(org_id, destruction_inventories)

def get_batches_data(organization_id):
    escaped_values = {}
    escaped_values["organization_id"] = organization_id

    query = '''
        SELECT *
        FROM inventories AS t
        WHERE t.organization_id=%(organization_id)s
        AND t.type = 'batch'
        AND t.stats->>'plants'>'2'
        LIMIT 4
    '''
    queryResult = select_from_db(query, escaped_values)

    if not queryResult:
        query = '''
        SELECT *
        FROM inventories AS t
        WHERE t.organization_id=%(organization_id)s
        AND t.type = 'batch'
        AND t.stats#>>'{g-oil,crude}'>'0'
        LIMIT 4
        '''
        queryResult = select_from_db(query, escaped_values)
        return queryResult
    elif len(queryResult) == 1:
        return [queryResult, queryResult]
    else:
        return queryResult



def create_queue_for_destruction(org_id, from_inventory_id, variety, room, wasteType, reason, from_qty, from_qty_unit, destroyed_qty_unit, timestamp):
    weighed_by_user = get_random_user(org_id)
    checked_by_user = get_random_user(org_id)

    queue_for_destruction_data = {
        "name": "queue_for_destruction",
        "organization_id": org_id,
        "created_by": USER_ID,
        "from_inventory_id": from_inventory_id,
        "to_qty": from_qty,
        "to_qty_unit": destroyed_qty_unit,
        "variety": variety,
        "type_of_waste": wasteType,
        "weighed_by": weighed_by_user["email"],
        "checked_by": checked_by_user["email"],
        "reason_for_destruction": reason,
        "collected_from": room,
        "from_qty": from_qty,
        "from_qty_unit": from_qty_unit
    }

    result = QueueForDestruction.do_activity(queue_for_destruction_data, {})
    create_signature(
        org_id, result['activity_id'], "weighed_by", weighed_by_user["id"], timestamp)
    create_signature(
        org_id, result['activity_id'], "checked_by", checked_by_user["id"], timestamp)
        

    print('batch id: {} has been sent to queue for destruction'.format(
        from_inventory_id))
    return {
        'inventory_id': result['inventory_id'],
        'from_qty': from_qty,
        'from_qty_unit': destroyed_qty_unit
    }


def destroy_material(org_id, inventories):

    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    complete_destruction = [{
        'name': 'complete_destruction',
        'from_inventory_id': inventory['inventory_id'],
        'from_qty': inventory['from_qty'],
        'from_qty_unit': inventory['from_qty_unit'],
        'to_status': 'destroyed',
    } for inventory in inventories]

    witness_1_user = get_random_user(org_id)
    witness_2_user = get_random_user(org_id)


    destroy_material_data = {
        "organization_id": org_id,
        "name": "destroy_material",
        "created_by": USER_ID,
        "destruction_timestamp": date,
        "method_of_destruction": "Kitty litter",
        "witness_1": witness_1_user["email"],
        "witness_1_role": "admin",
        "witness_2": witness_2_user["email"],
        "witness_2_role": "admin",
        'destroyed_date': date,
        "completed_queue_destruction_activities": complete_destruction
    }

    result = DestroyMaterial.do_activity(destroy_material_data, {})

    create_signature(
            org_id, result['activity_id'], "witness_1", witness_1_user["id"], date)
    create_signature(
            org_id, result['activity_id'], "witness_2", witness_2_user["id"], date)


    return result['activity_id']


if __name__ == "__main__":
    if (organization_id):
        DATABASE.dedicated_connection().begin()
    try:        
        create_lots(organization_id)
        DATABASE.dedicated_connection().commit()
    except(psycopg2.Error, psycopg2.Warning,
        psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        DATABASE.dedicated_connection().rollback()
