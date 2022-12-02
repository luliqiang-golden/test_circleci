import argparse
import os
import subprocess

import varieties_generator
import accounts_generator
import received_inventory_generator
import transfer_inventory_generator
import mothers_from_received_inventory_generator
import lots_generator

if __name__ == '__main__':
    
    parser=argparse.ArgumentParser()

    parser.add_argument('-org_id',
                        help='Pass, as argument, '
                        'org_id you wish to generate varieties for'
                        '[python varieties_generator.py -org_id]',
                        required=True, 
                        type=int)
    
    args = parser.parse_args()
    
    original_path = os.getcwd()
    
    varieties_generator.generate_varieties(args.org_id)
    os.chdir(os.path.dirname(original_path))
    subprocess.call("python varieties_import.py", shell=True)
    os.chdir(original_path)
    
    accounts_generator.generate_accounts(args.org_id)
    os.chdir(os.path.dirname(original_path))
    subprocess.call("python create_crm_accounts_import.py", shell=True)
    os.chdir(original_path)
    
    received_inventory_generator.generate_received_inventory(args.org_id)
    os.chdir(os.path.dirname(original_path))
    subprocess.call("python receive_inventory_import.py", shell=True)
    os.chdir(original_path)
    
    transfer_inventory_generator.generate_transfer_inventory(args.org_id)
    os.chdir(os.path.dirname(original_path))
    subprocess.call("python transfer_to_batch_import.py", shell=True)
    os.chdir(original_path)
    
    mothers_from_received_inventory_generator.generate_mothers(args.org_id)
    os.chdir(os.path.dirname(original_path))
    subprocess.call("python create_mothers_from_received_inventory_import.py", shell=True)
    os.chdir(original_path)
    
    lots_generator.generate_lot(args.org_id)
    os.chdir(os.path.dirname(original_path))
    subprocess.call("python create_lot_import.py", shell=True)
    os.chdir(original_path)