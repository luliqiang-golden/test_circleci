# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
import psycopg2
import psycopg2.extras
from random import randint
from db_functions import DATABASE, insert_into_db
from activities.create_consumable_class import CreateConsumableClass
from constants import USER_ID

def create_consumables(organization_id):

        create_consumable(
            organization_id=organization_id,
            type="Tyvek Suits",
            subtype="Cultivation",
            unit="item",
        )

        create_consumable(
            organization_id=organization_id,
            type="Soil",
            subtype="Cultivation",
            unit="g"
        )

        create_consumable(
            organization_id=organization_id,
            type="QA Labour",
            subtype="Cultivation",
            unit="item"
        )
        
        create_consumable(
            organization_id=organization_id,
            type="Cultivation Labour",
            subtype="Labour",
            unit="item"
        )

        create_consumable(
            organization_id=organization_id,
            type="Fertilizer",
            subtype="Cultivation",
            unit="g"
        )

        create_consumable(
            organization_id=organization_id,
            type="Gloves",
            subtype="Large",
            unit="item"
        )

        create_consumable(
            organization_id=organization_id,
            type="Pots",
            subtype="L1",
            unit="item"
        )

        create_consumable(
            organization_id=organization_id,
            type="Gloves",
            subtype="Small",
            unit="item"
        )

        create_consumable(
            organization_id=organization_id,
            type="Insects",
            subtype="Ladybugs",
            unit="container",
            containerUnit="insects",
            containerQty="70"
        )

        create_consumable(
            organization_id=organization_id,
            type="Insects",
            subtype="Wasps",
            unit="container",
            containerUnit="insects",
            containerQty="60"
        )

        create_consumable(
            organization_id=organization_id,
            type="Pesticide",
            subtype="Rodenticide",
            unit="g"
        )
    
    

def create_consumable(
        organization_id,
        type,
        subtype,
        unit,
        containerUnit = '',
        containerQty = 0,
):
    if (not containerUnit or containerQty == 0):
        consumable = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        "name": "create_consumable_class",
        "organization_id": organization_id,
        "type": type,
        "subtype": subtype,
        "unit": unit,
        }
    else:
        consumable = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        "name": "create_consumable_class",
        "organization_id": organization_id,
        "type": type,
        "subtype": subtype,
        "unit": unit,
        "containerUnit": containerUnit,
        "containerQty": containerQty,
        }

    consumable_class_result = CreateConsumableClass.do_activity(consumable, {})


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")  

    if (organization_id):
        # Begin DB transaction
        DATABASE.dedicated_connection().begin()

        try:
            create_consumables(organization_id)
            # Commit DB transaction
            DATABASE.dedicated_connection().commit()

        except:
            DATABASE.dedicated_connection().rollback()
