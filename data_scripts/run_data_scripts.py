import re
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
from psycopg2 import sql

from random import sample, shuffle, randint
from utilities import get_varieties, get_variety_strains
from create_batch_with_metrics import create_batch_with_metrics, get_batch_ids
from create_crm_account import create_accounts
from create_mother import create_mothers
from create_organization import create_org
from create_roles import create_roles
from create_room import create_room
from create_rules import create_rules
from create_sku import create_skus
from create_taxonomies import create_taxonomies
from create_taxonomy_option import create_taxonomy_option, create_taxonomy_options
from create_user import create_user
from create_order import create_orders
from create_shipment import create_shipments
from create_sample import create_samples
from create_destruction import create_destructions
from create_capa import create_capas
from create_receive_inventory import create_receive_inventories
from create_consumables import create_consumables
from create_consumable_lot import create_consumable_lots
from constants import STANDARDIZED_LAB_RESULT
from create_batch import create_batches, get_batches
from create_lot import create_lots
from create_recall import create_recalls
from create_departments import create_departments
from create_sops import create_sops
from create_org_settings import create_org_settings

# Import database connection from db_functions
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

from db_functions import DATABASE
import json


def run_data_scripts(opts=None):
    """ Function that runs all data scripts to generate data for a new or existing organization
    :type opts: dictionary
    :param opts: Contains options for running this script without interactive prompts

    :rtype: void
    """

    yes = re.compile("Y", re.IGNORECASE)
    no = re.compile("N", re.IGNORECASE)

    if opts is None:
        prompt = input("Do you want to create a org? (Y/N): ")
    else:
        prompt = opts['create_org']

    if yes.match(prompt):
        while True:
            prompt = input("Enter the org name: ")
            if prompt:
                break
        org_id = create_org(name=prompt)
        # demo_org_id = create_org(name="Demo")
    elif no.match(prompt):
        while True:
            if opts is None:
                prompt = input(
                    "Enter the org id you want to generate data for: ")
            else:
                prompt = opts['org_id']

            org_id = None
            try:
                org_id = int(prompt)
                break
            except ValueError:
                print("Error: You need to enter a number")

    if opts is None:
        prompt = input("Do you want to update org settings? (Y/N): ")
    else:
        prompt = opts['create_org_settings']

    if yes.match(prompt):
        create_org_settings(organization_id=org_id)
    elif no.match(prompt):
        print("Skipping org settings creation")

    if opts is None:
        prompt = input("Do you want to create roles? (Y/N): ")
    else:
        prompt = opts['create_roles']

    if yes.match(prompt):
        create_roles(organization_id=org_id)
    elif no.match(prompt):
        print("Skipping role creation")

    if opts is None:
        prompt = input("Do you want to create rules? (Y/N): ")
    else:
        prompt = opts['create_rules']

    if yes.match(prompt):
        create_rules(organization_id=org_id)
    elif no.match(prompt):
        print("Skipping rule creation")

    if opts is None:
        prompt = input("Do you want to create a default user? (Y/N): ")
    else:
        prompt = opts['create_user']

    if yes.match(prompt):
        create_user(
            organization_id=org_id,
            name="Admin User",
            email="admin@groweriq.ca"
        )
    elif no.match(prompt):
        print("Skipping user creation")

    # Create greenhouse rooms
    if opts is None:
        prompt = input("Do you want to create greenhouse rooms? (Y/N): ")
    else:
        prompt = opts['create_greenhouse_rooms']

    if yes.match(prompt):
        create_room(organization_id=org_id, name="Bay 1", zone="greenhouse")
        create_room(organization_id=org_id, name="Bay 2", zone="greenhouse")
        create_room(organization_id=org_id, name="Bay 3", zone="greenhouse")
        create_room(organization_id=org_id, name="Bay 4", zone="greenhouse")
        create_room(organization_id=org_id, name="Bay 5", zone="greenhouse")
        create_room(organization_id=org_id, name="Bay 6", zone="greenhouse")
    elif no.match(prompt):
        print("Skipping greenhouse room creation")

    # Create mother room
    if opts is None:
        prompt = input("Do you want to create a mother room? (Y/N): ")
    else:
        prompt = opts['create_mother_room']

    if yes.match(prompt):
        create_room(organization_id=org_id, name="Mother Room", zone="special")
    elif no.match(prompt):
        print("Skipping mother room creation")

    # Create propagation room
    if opts is None:
        prompt = input("Do you want to create a propagation room? (Y/N): ")
    else:
        prompt = opts['create_propagation_room']

    if yes.match(prompt):
        create_room(organization_id=org_id,
                    name="Propagation Room", zone="special")
    elif no.match(prompt):
        print("Skipping propagation room creation")

    # Create drying room
    if opts is None:
        prompt = input("Do you want to create a drying room? (Y/N): ")
    else:
        prompt = opts['create_drying_room']

    if yes.match(prompt):
        create_room(organization_id=org_id,
                    name="Drying Room", zone="special")
    elif no.match(prompt):
        print("Skipping drying room creation")

    # Create warehouse rooms
    if opts is None:
        prompt = input("Do you want to create warehouse rooms? (Y/N): ")
    else:
        prompt = opts['create_warehouse_rooms']

    if yes.match(prompt):
        create_room(organization_id=org_id, name="Vault 1", zone="warehouse")
        create_room(organization_id=org_id, name="Vault 2", zone="warehouse")
        create_room(organization_id=org_id, name="Vault 3", zone="warehouse")
        create_room(organization_id=org_id, name="Vault 4", zone="warehouse")
        create_room(organization_id=org_id, name="Vault 5", zone="warehouse")
        create_room(organization_id=org_id, name="Shipping/Receiving", zone="warehouse")
    elif no.match(prompt):
        print("Skipping warehouse room creation")

    varieties = get_varieties()

    variety_strains = get_variety_strains()

    if opts is None:
        prompt = input(
            "Do you want to create taxonomies and taxonomy options? (Y/N): ")
    else:
        prompt = opts['create_taxonomies']

    if yes.match(prompt):
        create_taxonomies(organization_id=org_id)
        create_taxonomy_options(org_id=org_id, variety_strains=variety_strains)

    elif no.match(prompt):
        print("Skipping taxonomy creation")

    # Shuffle batch varieties
    batch_varieties = varieties
    shuffle(batch_varieties)

    # Create crm accounts
    if opts is None:
        prompt = input(
            "Do you want to create crm accounts for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_crm_accounts']

    if yes.match(prompt):
        create_accounts(org_id)

    elif no.match(prompt):
        print("Skipping crm account creation")

     # Create receive inventories
    create_receive_inventories(org_id, batch_varieties)

    # Create mothers
    create_mothers(org_id)

    # Create skus
    create_skus(org_id, batch_varieties)

    # Create batches
    create_batches(org_id)

    # Create sample
    if opts is None:
        prompt = input(
            "Do you want to create samples for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_samples']

    if yes.match(prompt):
        create_samples(org_id)

    elif no.match(prompt):
        print("Skipping sample creation")

    # Create Lots and Lot items
    create_lots(org_id)

    # Create Orders
    if opts is None:
        prompt = input(
            "Do you want to create orders for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_orders']

    if yes.match(prompt):
        create_orders(org_id)

    elif no.match(prompt):
        print("Skipping order creation")

    # Create Shipment
    if opts is None:
        prompt = input(
            "Do you want to create shipments for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_shipments']

    if yes.match(prompt):
        create_shipments(org_id)

    elif no.match(prompt):
        print("Skipping shipment creation")

    # Create recalls
    create_recalls(org_id)

    # Create destruction
    if opts is None:
        prompt = input(
            "Do you want to create destruction process (queue for destruction and material destroyed) for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_destruction']

    if yes.match(prompt):
        create_destructions(org_id)

    elif no.match(prompt):
        print("Skipping destruction creation")

    # Create Capas
    if opts is None:
        prompt = input(
            "Do you want to create capas for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_capas']

    if yes.match(prompt):
        create_capas(org_id)
        # TODO: more descriptive confirmation like with create batches???
        print('Capas have been created')
    elif no.match(prompt):
        print("Skipping capa creation")

    # Create Consumables
    if opts is None:
        prompt = input(
            "Do you want to create consumables for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_consumables']

    if yes.match(prompt):
        create_consumables(org_id)
        print("Consumables have been created")

    elif no.match(prompt):
        print("Skipping consumables creation")

    # Create Consumable lot
    if opts is None:
        prompt = input(
            "Do you want to create consumable lots for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_consumable_lot']

    if yes.match(prompt):
        create_consumable_lots(org_id)
        print("Consumable lots have been created")

    elif no.match(prompt):
        print("Skipping consumable lot creation")

    # Create departments
    if opts is None:
        prompt = input(
            "Do you want to create departments for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_departments']

    if yes.match(prompt):
        create_departments(org_id)
        print("Departments have been created")

    elif no.match(prompt):
        print("Skipping departments creation")

    # Create SOPs
    if opts is None:
        prompt = input(
            "Do you want to create SOPs for the organization? (Y/N): "
        )
    else:
        prompt = opts['create_sops']

    if yes.match(prompt):
        create_sops(org_id)
        print("SOPS have been created")

    elif no.match(prompt):
        print("Skipping SOPs creation")


if __name__ == "__main__":
    DATABASE.dedicated_connection().begin()
    try:
        run_data_scripts()
        print('comit')
        DATABASE.dedicated_connection().commit()
    except(psycopg2.Error, psycopg2.Warning,
           psycopg2.ProgrammingError) as error:
        print('Error running data script: {!r}, errno is {}'.format(error, error.args[0]))
        DATABASE.dedicated_connection().rollback()
