#Varieties generator
import argparse
import os
import random
import pandas as pd
from datetime import date
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411
from sqlalchemy import create_engine

def generate_mothers(organization_id):
    
    DB_HOST = os.getenv('DB_HOST')
    DB = os.getenv('DB')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:5432/{DB}', echo = False)
    
    
    number_of_mothers = []
    variety_name = []
    received_inventory_id = []
    room = []
    
    
    received_inventories = pd.read_sql_query(f"""SELECT * FROM inventories 
                                             WHERE organization_id = {organization_id} AND 
                                                   type = 'received inventory' AND
                                                   stats->'plants' IS NOT NULL AND CAST(stats->>'plants' AS numeric) > 0""", con=engine)
    
    rooms = pd.read_sql_query(f"""SELECT name FROM rooms 
                                WHERE organization_id = {organization_id}""", con=engine)['name']
    
    i = 0
    while i < random.randint(5, 30):
        
        index = random.randint(0, len(received_inventories.index)-1)
        
        number_of_mothers.append(random.randint(0, 5))
        variety_name.append(received_inventories['variety'][index])
        room.append(rooms[random.randint(0, len(rooms)-1)])
        received_inventory_id.append(received_inventories['id'][index])
        
        i=i+1

    
    mothers_data = {
        
        'number of mothers being created': number_of_mothers,
        'variety': variety_name,
        'room': room,
        'received inventory id': received_inventory_id,
        'approved': 'Maintenance',
        'prepared': 'Maintenance',
        'reviewed': 'Maintenance',
        'date': date.today().strftime("%d-%m-%Y"),
        'organization_id': organization_id
    
    }
    
    
    df = pd.DataFrame(mothers_data)

    df.to_csv('../template_client_helper_scripts/create mothers from received inventory.csv', index=False, encoding='utf-8', sep=',')
    
    
    
if __name__ == '__main__':
    
    parser=argparse.ArgumentParser()

    parser.add_argument('-org_id',
                        help='Pass, as argument, '
                        'org_id you wish to generate varieties for'
                        '[python varieties_generator.py -org_id]',
                        required=True, 
                        type=int)
    
    args = parser.parse_args()
    
    generate_mothers(args.org_id)