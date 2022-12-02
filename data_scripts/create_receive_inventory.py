# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
import psycopg2
import psycopg2.extras
from random import randint

from db_functions import DATABASE
from utilities import get_ramdom_vendor, get_random_user, get_random_date_before_today, update_timestamp
from constants import USER_ID

from activities.receive_inventory import ReceiveInventory
from activities.approve_received_inventory import ApproveReceivedInventory


def create_receive_inventories(org_id, varieties):
    try:
        # approved
        end_day = len(varieties)*25
        MINUSDAYS = 10
        start_day = end_day-MINUSDAYS
        stats = ['seeds', 'g-wet', 'dry', 'cured', 'crude', 'distilled']
        count = 0
        # stats unit is not plants       
        # for variety in varieties:
        #     if count == 2:
        #         stats.pop(0)
        #         count = 0
        #     if len(stats) == 0:
        #         stats = ['seeds', 'g-wet', 'dry', 'cured', 'crude', 'distilled']
        #     stat = stats[0]
        #     count += 1
        #     date = get_random_date_before_today(start_day, end_day)
        #     inventory_id = create_receive_inventory(org_id, variety, date, stat)
        #     approve_received_inventory(org_id, inventory_id, date)
        #     start_day = end_day - MINUSDAYS
        #     end_day = start_day  
        # stats unit is plants       
        for variety in varieties:
            date = get_random_date_before_today(start_day, end_day)
            inventory_id = create_receive_inventory(org_id, variety, date, 'plants')
            approve_received_inventory(org_id, inventory_id, date)
            start_day = end_day - MINUSDAYS
            end_day = start_day
        # unappoved
        for index in range(1,3):
            date = get_random_date_before_today(start_day, end_day)
            variety = varieties[randint(0, len(varieties)-1)]
            inventory_id = create_receive_inventory(org_id, variety, date, 'plants')
            start_day = end_day - MINUSDAYS
            end_day = start_day        

    except:
        print('error at approving received inventory on create_receive_inventory')
        raise


def create_receive_inventory(org_id, variety, timestamp, stat):
    vendor = get_ramdom_vendor(org_id)
    qty = randint(1000, 2000)  
    pieces = qty
    net_weight = qty * 40
    unit = stat
    intended_use = "propagate mother / batches"

    receiveInventoryData = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": "receive_inventory",
      "po": "PO"+str(randint(1000,10000)),
      "vendor_name": vendor["name"],
      "vendor_id": vendor["id"],
      "variety": variety,
      "intended_use": intended_use,
      "net_weight_received": net_weight,
      "vendor_lot_number": "JG"+str(randint(1000,10000)),
      "number_of_pieces": pieces,
      "delivery_matches_po": True,
      "weighed_by": get_random_user(org_id)["email"],
      "checked_by": get_random_user(org_id)["email"],
      "to_stage": "received-unapproved",
      "quarantined": "false",
      "to_qty": qty,
      "to_qty_unit": unit,
      "package_type": "unpackaged",
    }
    try:
        result = ReceiveInventory.do_activity(receiveInventoryData, {})
        update_timestamp('inventories', result['inventory_id'], timestamp)
        update_timestamp('activities', result['activity_id'], timestamp)
        return result["inventory_id"]
    except:
        print('error at receiving inventory on create_receive_inventory')
        raise 
    


def approve_received_inventory(org_id, inventory_id, timestamp):
    approveReceivedInventoryData = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": "approve_received_inventory",
      "inventory_id": inventory_id,
      "to_stage": "received-approved",
      "quarantined": False,
      "approved_by": get_random_user(org_id)["email"],
    }

    try:
        result = ApproveReceivedInventory.do_activity(approveReceivedInventoryData, {})
        update_timestamp('activities', result['activity_id'], timestamp)
        return result
    except:
        print('error at approving received inventory on create_receive_inventory')
        raise 


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")  

    if (organization_id):
        DATABASE.dedicated_connection().begin()
        try:
            create_receive_inventories(organization_id)
            DATABASE.dedicated_connection().commit()
        except:
            DATABASE.dedicated_connection().rollback()
