#Varieties generator
import argparse
import os
import random
import pandas as pd
from datetime import date
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411
from sqlalchemy import create_engine

def generate_received_inventory(organization_id):
    
    DB_HOST = os.getenv('DB_HOST')
    DB = os.getenv('DB')
    DB_USERNAME = os.getenv('DB_USERNAME')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    engine = create_engine(f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:5432/{DB}', echo = False)
    
    varieties = pd.read_sql_query(f"""SELECT name FROM taxonomy_options 
                                WHERE taxonomy_id = (SELECT id FROM taxonomies WHERE name = 'varieties' AND organization_id = {organization_id})""", con=engine)['name']

    rooms = pd.read_sql_query(f"""SELECT name FROM rooms 
                                WHERE organization_id = {organization_id}""", con=engine)['name']

    inventories_types = ['packaged', 'unpackaged']
    product_types = ['seeds', 'plants', 'g-wet', 'dry', 'cured', 'crude', 'distilled', 'terpene', 'sift', 'biomass', 'hash']

    variety_name = []

    product_type = []

    package_type = []

    amount = []

    net_weight_received = []
    
    room = []


    for variety in varieties:
        for inv_type in inventories_types:
            for prod_type in product_types:
                
                variety_name.append(variety)
                package_type.append(inv_type)
                product_type.append(prod_type)
                amount.append(random.randint(100, 10000))
                net_weight_received.append(random.randint(100, 10000))
                room.append(rooms[random.randint(0, len(rooms)-1)])


    received_inventory_data = {
        'variety name': variety_name,
        'product type': product_type,
        'package type': package_type,
        'amount': amount,
        'net weight received': net_weight_received,
        'account': 'Supplier',
        'weighed by': 'maintenance@groweriq.ca',
        'checked by': 'maintenance@groweriq.ca',
        'approved by': 'maintenance@groweriq.ca',
        'room': room,
        'source lot number': 0,
        'purchase order': 0,
        'date': date.today().strftime("%d-%m-%Y"),
        'organization_id': organization_id
    }

    df = pd.DataFrame(received_inventory_data)

    df.to_csv('../template_client_helper_scripts/receive inv import.csv', index=False, encoding='utf-8', sep=',')
    
if __name__ == '__main__':
    
    parser=argparse.ArgumentParser()

    parser.add_argument('-org_id',
                        help='Pass, as argument, '
                        'org_id you wish to generate varieties for'
                        '[python varieties_generator.py -org_id]',
                        required=True, 
                        type=int)
    
    args = parser.parse_args()
    
    generate_received_inventory(args.org_id)