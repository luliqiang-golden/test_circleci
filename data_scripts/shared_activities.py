# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

import argparse
from db_functions import DATABASE
from utilities import select_from_db, update_timestamp
from constants import USER_ID
from datetime import datetime
from utilities import get_random_user, get_random_date_before_today
from activities.create_mother import CreateMother
from activities.update_room import UpdateRoom
from activities.propagate_cuttings import PropagateCuttings
from activities.transfer_inventory import TransferInventory
from activities.create_signature import CreateSignature



def update_room(org_id, inventory_id, room, timestamp):
    updateRoomDate = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "update_room",
        "inventory_id": inventory_id,
        "to_room": room
    }

    try:
        result = UpdateRoom.do_activity(updateRoomDate, {})
        update_timestamp('activities', result['activity_id'], timestamp)
        return result
    except:
        print('error updating room on shared_activities')
        raise


def transfer_inventory(org_id, from_inventory_id, to_inventory_id, variety, timestamp, qty, qty_unit='plants', oil_density=0):
    prepared_by_user = get_random_user(org_id)
    reviewed_by_user = get_random_user(org_id)
    approved_by_user = get_random_user(org_id)

    transferInventoryData = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "transfer_inventory",
        "variety": variety,
        "from_inventory_id": from_inventory_id,
        "to_inventory_id": to_inventory_id,
        "to_qty": qty,
        "to_qty_unit": qty_unit,
        "from_qty": qty,
        "from_qty_unit": qty_unit,
        "prepared_by": prepared_by_user["email"],
        "reviewed_by": reviewed_by_user["email"],
        "approved_by": approved_by_user["email"]
    }

    if (oil_density > 0):
        transferInventoryData['oil_density'] = oil_density

    try:
        result = TransferInventory.do_activity(transferInventoryData, {})
        update_timestamp('activities', result['activity_id'], timestamp)
        create_signature(
            org_id, result['activity_id'], "prepared_by", prepared_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "reviewed_by", reviewed_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "approved_by", approved_by_user["id"], timestamp)
        return result
    except:
        print('error transfering inventory on shared_activities')
        raise


def propagate_cuttings(org_id, from_inventory_id, to_inventory_id, timestamp, qty):
    prepared_by_user = get_random_user(org_id)
    reviewed_by_user = get_random_user(org_id)
    approved_by_user = get_random_user(org_id)

    propagateCuttingsData = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "propagate_cuttings",
        "from_inventory_id": from_inventory_id,
        "to_inventory_id": to_inventory_id,
        "to_qty": qty,
        "to_qty_unit": "plants",
        "source_count": qty,
        "prepared_by": prepared_by_user["email"],
        "reviewed_by": reviewed_by_user["email"],
        "approved_by": approved_by_user["email"]
    }

    try:
        result = PropagateCuttings.do_activity(propagateCuttingsData, {})
        update_timestamp('activities', result['activity_id'], timestamp)
        create_signature(
            org_id, result['activity_id'], "prepared_by", prepared_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "reviewed_by", reviewed_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "approved_by", approved_by_user["id"], timestamp)
        return result
    except:
        print('error propagting cutting on shared_activities')
        raise


def create_signature(org_id, activity_id, field, signed_by, timestamp):
    signature_data = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "create_signature",
        "signed_by": USER_ID,
        "field": field,
        "timestamp": timestamp,
        "activity_id": activity_id
    }

    try:
        result = CreateSignature.do_activity(signature_data, {})
        # update_timestamp('activities', result['activity_id'], timestamp)
        return result
    except:
        print('error signature on shared_activities')
        raise
