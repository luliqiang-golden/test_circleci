# Import libraries from parent folder

import os
import sys
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))) +
    '/python_scripts')
import psycopg2.extras
import psycopg2
import argparse
from run_data_scripts import run_data_scripts
from clear_org_data import clear_org_data
from db_functions import DATABASE


def generate_data(organization_id):
    """ Generates data for organization"""

    clear_org_data({
        "clear_org": "Y",
        "org_id": organization_id
    })

    run_data_scripts({
        "create_org": "N",
        "org_id": organization_id,
        "create_org_settings": "Y",
        "create_roles": "N",
        "create_rules": "N",
        "create_user": "N",
        "create_greenhouse_rooms": "Y",
        "create_mother_room": "Y",
        "create_propagation_room": "Y",
        "create_drying_room": "Y",
        "create_warehouse_rooms": "Y",
        "create_taxonomies": "Y",
        "create_crm_accounts": "Y",
        "create_shipments": "Y",
        "create_orders": "Y",
        "create_samples": "Y",
        "create_capas": "Y",
        "create_destruction": "Y",
        "create_consumables": "Y",
        "create_consumable_lot": "Y",
        "create_departments": "Y",
        "create_sops": "Y"
    })


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")
    if (organization_id):
        DATABASE.dedicated_connection().begin()
        try:
            generate_data(organization_id)
            DATABASE.dedicated_connection().commit()
        except(psycopg2.Error, psycopg2.Warning,
               psycopg2.ProgrammingError) as error:
            print('Error running data script: {!r}, errno is {}'.format(error, error.args[0]))
            DATABASE.dedicated_connection().rollback()
