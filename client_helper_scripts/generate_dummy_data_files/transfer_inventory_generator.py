#Varieties generator
import argparse
import os
import random
import pandas as pd
from datetime import date
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411
from sqlalchemy import create_engine

def generate_transfer_inventory(organization_id):
    
    DB_HOST = os.getenv('DB_HOST')
    DB = os.getenv('DB')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:5432/{DB}', echo = False)
    
    possible_end_types = {
        'seeds': ['seeds', 'plants', 'g-wet', 'dry', 'cured', 'crude', 'distilled'],
        'plants': ['plants', 'g-wet', 'dry', 'cured', 'crude', 'distilled'],
        'g-wet': ['g-wet','dry', 'cured', 'crude', 'distilled'],
        'dry': ['dry', 'cured', 'crude', 'distilled'],
        'cured': ['cured', 'crude', 'distilled'],
        'crude': ['crude', 'distilled'],
        'distilled': ['distilled'],
        'biomass':  ['biomass'],
        'terpene':  ['terpene'],
        'sift':  ['sift'],
        'hash': ['hash']
    }
    
    variety_name = []
    start_type = []
    end_type = []
    received_inventory_id = []
    transfer_qty = []
    room = []
    
    
    received_inventories = pd.read_sql_query(f"""SELECT * FROM inventories WHERE organization_id = {organization_id} and type = 'received inventory'""", con=engine)
    
    rooms = pd.read_sql_query(f"""SELECT name FROM rooms 
                                WHERE organization_id = {organization_id}""", con=engine)['name']

    
    i = 0
    while i < random.randint(20, len(received_inventories.index)-1):
        
        index = random.randint(0, len(received_inventories.index)-1)
        
        start_unit = ''
        initial_quantity = 0
        for key_1, value_1 in received_inventories['stats'][index].items():
                if isinstance(value_1, dict):
                    for key_2, value_2 in value_1.items():
                        start_unit = key_2
                        initial_quantity = int(value_2)
                else:
                    start_unit = key_1
                    initial_quantity = int(value_1)
        
        
        variety_name.append(received_inventories['variety'][index])
        start_type.append(start_unit)
        end_type.append(possible_end_types[start_unit][random.randint(0, len(possible_end_types[start_unit])-1)])
        received_inventory_id.append(received_inventories['id'][index])
        transfer_qty.append(int(initial_quantity * random.randint(5, 30)/100))
        room.append(rooms[random.randint(0, len(rooms)-1)])
        
        i=i+1

    
    transfer_batch_data = {
        
        'variety': variety_name,
        'custom name': '',
        'scale name': '',
        'start type': start_type,
        'end type': end_type,
        'room': room,
        'received inventory id': received_inventory_id,
        'transfer qty': transfer_qty,
        'approved': 'Maintenance',
        'prepared': 'Maintenance',
        'reviewed': 'Maintenance',
        'date': date.today().strftime("%d-%m-%Y"),
        'organization_id': organization_id
    }
    
    
    df = pd.DataFrame(transfer_batch_data)

    df.to_csv('../template_client_helper_scripts/transfer to batch.csv', index=False, encoding='utf-8', sep=',')
    
    
    
if __name__ == '__main__':
    
    parser=argparse.ArgumentParser()

    parser.add_argument('-org_id',
                        help='Pass, as argument, '
                        'org_id you wish to generate varieties for'
                        '[python varieties_generator.py -org_id]',
                        required=True, 
                        type=int)
    
    args = parser.parse_args()
    
    generate_transfer_inventory(args.org_id)