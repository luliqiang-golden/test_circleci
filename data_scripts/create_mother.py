# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

import argparse
from db_functions import DATABASE
from constants import USER_ID
from datetime import datetime, timedelta
from random import sample
from utilities import get_random_user, get_random_date_before_today, select_from_db, update_timestamp
from shared_activities import update_room, transfer_inventory, propagate_cuttings
from activities.create_mother import CreateMother
import psycopg2
import psycopg2.extras
from psycopg2 import sql



def create_mothers(org_id):    
    try:
        mothers = []
        mother_data = get_mother_data(org_id)
        random_mothers_to_create_mother_to_mother = sample(mother_data, 3)

        for data in mother_data:
            mother_from_mother = data in random_mothers_to_create_mother_to_mother
            date = data['timestamp'] + timedelta(days=10)
            mother_id = create_mother(org_id, data["variety"], date, data["id"])
            if (mother_from_mother):
                print(mother_id, ' mother from mother')
                create_mother(org_id, data["variety"], date, mother_id, True)

            mothers.append({"mother_id": mother_id, "variety": data["variety"]})
            
        return mothers   
    except:
        print('error creating mothers on create_mother ')
        raise


def get_mother_data(org_id):
    params = {'organization_id': org_id}
    query = '''        
        SELECT id, (stats->>'plants') plants, variety , timestamp               
        FROM inventories
        WHERE organization_id = %(organization_id)s 
            AND type = 'received inventory' AND (stats->>'plants') > '1' 
            AND  attributes->>'stage' = 'received-approved'
    '''
    
    return select_from_db(query, params)


def create_mother(org_id, variety, timestamp, from_inventory_id, mother_from_mother = False):
    motherData ={
      "organization_id": org_id,
      "created_by": USER_ID,
      "timestamp": timestamp,
      "variety": variety,
      "name": "create_mother",
    }

    try:
        result = CreateMother.do_activity(motherData, {})
        update_timestamp('inventories', result["inventory_id"], timestamp)
        update_timestamp('activities', result["activity_id"], timestamp)
        update_room(org_id, result["inventory_id"], 'Mother Room',timestamp)
        if (mother_from_mother):
            propagate_cuttings(org_id, from_inventory_id, result["inventory_id"], timestamp, 1)
        else:
            transfer_inventory(org_id, from_inventory_id, result["inventory_id"], variety, timestamp, 1)
        return result["inventory_id"]
    except:
        print('error creating mother on create_mother ')
        raise 



if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")  

    if (organization_id):
        DATABASE.dedicated_connection().begin()
        try:        
            create_mothers(organization_id)
            DATABASE.dedicated_connection().commit()
        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
            print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
            DATABASE.dedicated_connection().rollback()
