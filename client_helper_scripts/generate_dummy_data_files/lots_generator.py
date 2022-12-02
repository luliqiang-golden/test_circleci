#Varieties generator
import argparse
import os
import random
import pandas as pd
from datetime import date
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411
from sqlalchemy import create_engine

def generate_lot(organization_id):
    
    DB_HOST = os.getenv('DB_HOST')
    DB = os.getenv('DB')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:5432/{DB}', echo = False)
   
    variety_name = []
    received_inventory_id = []
    transfer_qty = []
    transfer_unit = []
    room = []
    
    
    received_inventories = pd.read_sql_query(f"""SELECT * FROM inventories WHERE organization_id = {organization_id} and type = 'received inventory'""", con=engine)
    
    rooms = pd.read_sql_query(f"""SELECT name FROM rooms 
                                WHERE organization_id = {organization_id}""", con=engine)['name']

    
    i = 0
    while i < random.randint(20, len(received_inventories.index)-1):
        
        index = random.randint(0, len(received_inventories.index)-1)
        
        unit = ''
        initial_quantity = 0
        for key_1, value_1 in received_inventories['stats'][index].items():
                if isinstance(value_1, dict):
                    for key_2, value_2 in value_1.items():
                        unit = key_2
                        initial_quantity = int(value_2)
                else:
                    unit = key_1
                    initial_quantity = int(value_1)
        
        if(initial_quantity > 0):
            
            variety_name.append(received_inventories['variety'][index])
            transfer_unit.append(unit)
            received_inventory_id.append(received_inventories['id'][index])
            transfer_qty.append(int(initial_quantity * random.randint(5, 30)/100))
            room.append(rooms[random.randint(0, len(rooms)-1)])
        
        i=i+1

    
    lot_data = {
        
        'variety': variety_name,
        'room': room,
        'received inventory id': received_inventory_id,
        'transfer qty': transfer_qty,
        'transfer unit': transfer_unit,
        'approved_by': 'Maintenance',
        'checked_by': 'Maintenance',
        'weighed_by': 'Maintenance',
        'date': date.today().strftime("%d-%m-%Y"),
        'organization_id': organization_id
    }
    
    
    df = pd.DataFrame(lot_data)

    df.to_csv('../template_client_helper_scripts/create lot import.csv', index=False, encoding='utf-8', sep=',')
    
    
    
if __name__ == '__main__':
    
    parser=argparse.ArgumentParser()

    parser.add_argument('-org_id',
                        help='Pass, as argument, '
                        'org_id you wish to generate varieties for'
                        '[python varieties_generator.py -org_id]',
                        required=True, 
                        type=int)
    
    args = parser.parse_args()
    
    generate_lot(args.org_id)