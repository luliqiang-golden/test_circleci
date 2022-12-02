# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
import psycopg2
import psycopg2.extras
from random import randint
from db_functions import DATABASE, DatabaseError
from utilities import *
from random import sample
from create_crm_account import get_crm_accounts_by_organization
from create_transaction import *
from activities.receive_consumable_lot import ReceiveConsumableLot
from activities.record_transaction import RecordTransaction
from activities.record_transaction_allocation import RecordTransactionAllocation
from activities.update_transaction_total_amount import UpdateTransactionTotalAmount
from activities.consumable_lot_destroy_items import ConsumableLotDestroyItems
from activities.consumable_lot_use_items import ConsumableLotUseItems
from activities.consumable_lot_return_items import ConsumableLotReturnItems
from activities.consumable_lot_update_status import UpdateStatus
from constants import USER_ID
from class_errors import DatabaseError


def get_consumable_lot_data(organization_id):

    return [
        {
            "initial_qty": 110,
            "intended_use": "Cultivation",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12345,
            "amount": 2000,
        },
        {
           "initial_qty": 8000,
            "intended_use": "For Batch 2",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12346,
            "amount": 100,
        },
           {
           "initial_qty": 150,
            "intended_use": "Cultivation",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12347,
            "amount": 1000,
        },
        {
           "initial_qty": 100,
            "intended_use": "Harvesting",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12348,
            "amount": 750,
        },
           {
           "initial_qty": 100000,
            "intended_use": "Cultivation",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12349,
            "amount": 700,
        },
           {
           "initial_qty": 190000,
            "intended_use": "Utility",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12350,
            "amount": 50,
        },
           {
           "initial_qty": 350,
            "intended_use": "Cultivation",
            "damage_to_shipment": True,
            "delivery_matches_po": True,
            "delivery_details": "Different order number",
            "damage_details": "Slightly broken",
            "po": 12351,
            "amount": 70,
        },
           {
           "initial_qty": 115,
            "intended_use": "Utility",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12352,
            "amount": 230,
        },
        {
           "initial_qty": 500,
            "intended_use": "Cultivation",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12456,
            "amount": 300,
        },
        {
           "initial_qty": 600,
            "intended_use": "Cultivation",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12498,
            "amount": 320,
        },
        {
           "initial_qty": 250,
            "intended_use": "Cultivation",
            "damage_to_shipment": False,
            "delivery_matches_po": False,
            "delivery_details": None,
            "damage_details": None,
            "po": 12500,
            "amount": 320,
        },
    ]

def get_consumable_class_from_id(class_id, consumables): 
    for consumable in consumables:
        if consumable.get('id') == class_id:
            return consumable

def create_consumable_lots(organization_id):
        consumables = get_consumables_by_organization(organization_id)

        consumable_lot_data = get_consumable_lot_data(organization_id)

        for i, consumable in enumerate(consumable_lot_data):

            crm_account = get_ramdom_vendor(organization_id)
            user = get_random_user(organization_id)

            consumable_lot_id = create_consumable_lot(
                consumable_class_id=consumables[i]['id'],
                initial_qty=consumable["initial_qty"],
                unit=consumables[i]['unit'],
                organization_id=organization_id,
                expiration_date=get_random_date_after_today(1,30),
                vendor_name=crm_account['name'],
                checked_by=user['name'],
                intended_use=consumable["intended_use"],
                damage_to_shipment=consumable["damage_to_shipment"],
                damage_details=consumable["damage_details"],
                delivery_matches_po=consumable["delivery_matches_po"],
                delivery_details=consumable["delivery_details"],
                po=consumable["po"],
                amount=consumable["amount"]
            )

            transaction_id = create_transaction_for_consumable_lot(
                organization_id=organization_id,
                vendor_id=crm_account['id'],
                purchase_order=consumable["po"],
            )

            create_transaction_allocation(
                organization_id=organization_id,
                transaction_id=transaction_id,
                amount=consumable["amount"],
                consumable_lot_id=consumable_lot_id )

            update_transaction(
                organization_id=organization_id,
                to_transaction_id=transaction_id,
                amount=consumable["amount"],
            )

        consumable_lots = get_consumable_lots_by_organization(organization_id)
        actions_on_consumable_lot = sample(consumable_lots, 11)

        try:
            allocation = get_allocation_associated_with_consumable_lot(organization_id, actions_on_consumable_lot[0]['id'])
        except:
            print('Error in getting transaction allocation related to the consumable lot')

        if 'amount' in allocation:
            returnable_amount = randint(1, allocation['amount']/2)

        try:
            consumable = get_consumable_type_from_consumable(organization_id, actions_on_consumable_lot[0]['class_id'])
        except:
            print('Error in getting consumable related to the consumable lot')

        #return this lot
        consumable_lot_return_items(
            organization_id=organization_id,
            transaction_id=allocation['transaction_id'],
            amount=returnable_amount,
            from_consumable_lot_id=actions_on_consumable_lot[0]['id'],
            description=("Returning the %s" % consumable['type']),
            from_qty=int(actions_on_consumable_lot[0]['current_qty']/2),
            returned_by=user['name'],
            from_qty_unit=actions_on_consumable_lot[0]['unit'])

        # create a dictionary of 4 unique varieties
        used_varieties = {}

        inventories = get_distinct_inventories(organization_id, 11)
        for inventory in inventories:
            used_varieties[inventory['variety']] = inventory['id']

        used_varieties_keys = list(used_varieties.values())

        ipmCount = 0
        i = 0
        # Tie lots to random inventories containing different varieties
        # Make sure there is at least 1 IPM lot and total consumable lots is < 6
        while ipmCount < 2 and i < 11:
   
            consumable_lot_approve_items(
                organization_id=organization_id,
                to_status="approved",
                consumable_lot_id=actions_on_consumable_lot[i]['id'],
                created_by=actions_on_consumable_lot[i]['created_by']
            )

            current_qty = actions_on_consumable_lot[i]['current_qty']
            from_qty = randint(5, int(current_qty/2) - 5)

            try:
                allocation = get_allocation_associated_with_consumable_lot(organization_id, actions_on_consumable_lot[i]['id'])
            except:
                print('Error in getting transaction allocation related to the consumable lot')

            if 'amount' in allocation:
                from_amount = round(float(allocation['amount']/from_qty), 2)

            consumable = get_consumable_class_from_id(actions_on_consumable_lot[i]['class_id'], consumables)

            # Send ipm lots to a different method
            if consumable.get('type').lower() != 'insects' and consumable.get('type').lower() != 'ipm':
                consumable_lot_use_items(
                    organization_id=organization_id,
                    consumable_type= consumable.get('type'),
                    subtype= consumable.get('subtype'),
                    prepared_by= 'Andrew Wilson',
                    sprayed_by='Mack "Attack" Martyn',
                    from_consumable_lot_id=actions_on_consumable_lot[i]['id'],
                    from_qty=from_qty,
                    from_amount=from_amount,
                    unit=actions_on_consumable_lot[i]['unit'],
                    inventoryId=str(used_varieties_keys[i-1]),
                    person_in_charge='Andrew Wilson'
                )
            else:
                consumable_lot_use_items_ipm(
                organization_id=organization_id,
                consumable_type= consumable.get('type'),
                subtype= consumable.get('subtype'),
                prepared_by= 'Andrew Wilson',
                added_by='Mack "Attack" Martyn',
                from_consumable_lot_id=actions_on_consumable_lot[i].get('id'),
                from_qty=from_qty,
                from_amount=from_amount,
                unit=consumable.get('unit'),
                inventoryId=str(used_varieties_keys[i-1]),
                room='Propagation Room',
                container_qty=consumable.get('container_qty'),
                container_unit=consumable.get('container_unit'),
                pest=consumable.get('pest'),
                )
                ipmCount += 1
            actions_on_consumable_lot[i]['current_qty'] = actions_on_consumable_lot[i]['current_qty'] - from_qty
            i += 1
            

        #destroy this lot
        current_qty = actions_on_consumable_lot[5]['current_qty']
        from_qty = randint(1, current_qty)

        consumable_lot_destroy_items(
            organization_id=organization_id,
            from_consumable_lot_id=actions_on_consumable_lot[5]['id'],
            from_qty=from_qty,
            destroyedBy=user['name'],
            unit=actions_on_consumable_lot[5]['unit'])


def create_consumable_lot(
        consumable_class_id,
        initial_qty,
        unit,
        organization_id,
        expiration_date,
        vendor_name,
        checked_by,
        intended_use,
        damage_to_shipment,
        po,
        delivery_details,
        damage_details,
        delivery_matches_po,
        amount
):

    consumable_lot = {
      "organization_id": organization_id,
      "created_by": USER_ID,
      "name": "receive_consumable_lot",
      "consumable_class_id": consumable_class_id,
      "initial_qty": initial_qty,
      "current_qty": initial_qty,
      "unit": unit,
      "expiration_date": expiration_date,
      "vendor_name": vendor_name,
      "checked_by": checked_by,
      "intended_use": intended_use,
      "damage_to_shipment": damage_to_shipment,
      "damage_details": damage_details,
      "delivery_matches_po": delivery_matches_po,
      "delivery_details": delivery_details,
      "po": po,
      "amount": amount
    }

    try:
        consumable_lot = ReceiveConsumableLot.do_activity(consumable_lot, {})
        return consumable_lot['consumable_lot_id']

    except:
        print('Error: cannot do activity create_consumable_lot')
        raise

def consumable_lot_destroy_items(
    organization_id,
    from_consumable_lot_id,
    from_qty,
    destroyedBy,
    unit,
    ):

    consumable_lot_destroy_items = {
      'name': 'consumable_lot_destroy_items',
      'from_consumable_lot_id': from_consumable_lot_id,
      'from_qty': from_qty,
      'destroyed_by': destroyedBy,
      'from_qty_unit': unit,
      'organization_id': organization_id,
      'created_by': USER_ID
    }

    try:
        destroy_consumable_lot = ConsumableLotDestroyItems.do_activity(consumable_lot_destroy_items, {})
    except:
        print('Error: cannot do activity destroy_consumable_lot')
        raise

def consumable_lot_approve_items(
    organization_id,
    to_status,
    consumable_lot_id,
    created_by
    ):

    consumable_lot_approve_items = {
      'name': 'consumable_lot_update_status',
      'organization_id': organization_id,
      'to_status': to_status,
      'consumable_lot_id': consumable_lot_id,
      'created_by': created_by
    }

    try:
        approve_consumable_lot = UpdateStatus.do_activity(consumable_lot_approve_items, {})
    except:
        print('Error: cannot do activity consumable_lot_update_status')
        raise


def consumable_lot_use_items(
    organization_id,
    consumable_type,
    subtype,
    prepared_by,
    sprayed_by,
    from_consumable_lot_id,
    from_qty,
    from_amount,
    inventoryId,
    unit,
    person_in_charge
    ):

    consumable_lot_use_items = {
      'name': 'consumable_lot_use_items',
      'organization_id': organization_id,
      'created_by': USER_ID,
      'type': consumable_type,
      'subtype': subtype,
      'prepared_by': prepared_by,
      'sprayed_by': sprayed_by,
      'from_consumable_lot_id': from_consumable_lot_id,
      'from_qty': from_qty,
      'from_amount': from_amount,
      'from_qty_unit': unit,
      'linked_inventory_id': inventoryId,
      'person_in_charge': person_in_charge
    }

    try:
        use_consumable_lot = ConsumableLotUseItems.do_activity(consumable_lot_use_items, {})
    except:
        print('Error: cannot do activity use_consumable_lot')
        raise

def consumable_lot_use_items_ipm(
    organization_id,
    consumable_type,
    subtype,
    prepared_by,
    added_by,
    from_consumable_lot_id,
    from_qty,
    from_amount,
    inventoryId,
    unit,
    room,
    container_qty,
    container_unit,
    pest,
    ):

    consumable_lot_use_items_ipm = {
      'name': 'consumable_lot_use_items',
      'organization_id': organization_id,
      'created_by': USER_ID,
      'type': consumable_type,
      'subtype': subtype,
      'prepared_by': prepared_by,
      'added_by': added_by,
      'from_consumable_lot_id': from_consumable_lot_id,
      'from_qty': from_qty,
      'from_amount': from_amount,
      'from_qty_unit': unit,
      'linked_inventory_id': inventoryId,
      'room': room,
      'container_qty': container_qty,
      'container_unit': container_unit,
      'pest': pest,
    }

    try:
        use_consumable_lot = ConsumableLotUseItems.do_activity(consumable_lot_use_items_ipm, {})
    except:
        print('Error: cannot do activity use_consumable_lot')
        raise

def consumable_lot_return_items(
    organization_id,
    transaction_id,
    amount,
    description,
    from_consumable_lot_id,
    from_qty,
    returned_by,
    from_qty_unit,
    ):

    consumable_lot_return_items = {
      'name': 'consumable_lot_return_items',
      'from_consumable_lot_id': from_consumable_lot_id,
      'from_qty': from_qty,
      'returned_by': returned_by,
      'from_qty_unit': from_qty_unit,
      'organization_id': organization_id,
      'created_by': USER_ID
    }

    try:
        return_consumable_lot = ConsumableLotReturnItems.do_activity(consumable_lot_return_items, {})
    except:
        print('Error: cannot do activity consumable_lot_return_items')
        raise

    transaction_allocation = {
      'name': 'record_transaction_allocation',
      'type': 'credit',
      'created_by': USER_ID,
      'organization_id': organization_id,
      'transaction_id': transaction_id,
      'amount': amount,
      'consumable_lot_id': from_consumable_lot_id,
    }

    try:
        record_transaction_allocation = RecordTransactionAllocation.do_activity(transaction_allocation, {})
    except:
        print('Error: cannot do activity record_transaction_allocation')
        raise

    update_transaction = {
    'name': 'update_transaction_total_amount',
    'from_transaction_id': transaction_id,
    'amount': amount,
    'organization_id': organization_id,
    'created_by': USER_ID
    }

    try:
        update_transaction_amount = UpdateTransactionTotalAmount.do_activity(update_transaction, {})
    except:
        print('Error: cannot do activity update_transaction_total_amount')
        raise


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")  

    if (organization_id):
        # Begin DB transaction
        DATABASE.dedicated_connection().begin()

        create_consumable_lots(organization_id)

        # Commit DB transaction
        DATABASE.dedicated_connection().commit()
