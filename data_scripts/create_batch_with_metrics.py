# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
from datetime import datetime, timedelta
from insert_metrics_for_batch import insert_metrics_into_db
from create_sku import create_sku
from db_functions import DATABASE, insert_into_db, select_collection_from_db

from constants import USER_ID, CUTTINGS_COUNT


def get_batch_ids(organization_id):
    ids = []
    batches = select_collection_from_db(
        resource='inventories',
        organization_id=organization_id,
        filters=[('type', '=', 'batch')]
    )
    for batch in batches[0]:
        ids.append(batch.get('id'))
    return ids


def propagate_cuttings(organization_id, batch_id, mothers, timestamp):
    """Propagate cuttings from mothers to given batch_id at specified timestamp

    Arguments:
        organization_id {int} -- Organization id to create propagate_cuttings activity for
        batch_id {int} -- Batch id to propagate cutting for
        mothers {list} -- List of mothers to propagate cuttings from
        timestamp {str} -- Timestamp for the propagate_cuttings activities

    Returns:
        list -- List of created propagate_cuttings activities
    """

    propagate_cuttings_ids = []
    for mother_id in mothers:
        propagate_cuttings_data = {
            'organization_id': organization_id,
            'created_by': USER_ID,
            'timestamp': timestamp,
            'name': 'propagate_cuttings',
            # Data columns
            'to_qty': CUTTINGS_COUNT,
            'approved_by': 'andrew.wilson@wilcompute.com',
            'prepared_by': 'daniel.favand@wilcompute.com',
            'reviewed_by': 'andrew.wilson@wilcompute.com',
            'target_type': 'batch',
            'to_qty_unit': 'plants',
            'source_count': 1,
            'to_inventory_id': batch_id,
            'from_inventory_id': mother_id,
        }

        activity_id = insert_into_db('activities', propagate_cuttings_data)
        propagate_cuttings_ids.append(activity_id)

    return propagate_cuttings_ids


def update_stage(organization_id, batch_id, stage, timestamp):
    """Updates the stage for a given batch_id to the specified stage at the given timestamp

    Arguments:
        organization_id {int} -- Organization id to create update_stage activity for
        batch_id {int} -- Batch id to update stage for
        stage {str} -- Stage to update batch to
        timestamp {str} -- Timestamp for the update_stage activity

    Returns:
        int -- Activity id for the update_stage activity
    """

    update_stage_data = {
        'organization_id': organization_id,
        'created_by': USER_ID,
        'timestamp': timestamp,
        'name': 'update_stage',
        'to_stage': stage,
        'inventory_id': batch_id
    }

    update_stage_id = insert_into_db('activities', update_stage_data)

    return update_stage_id


def create_batch_with_metrics(variety, start_date, mothers, organization_id=1, room="Bay 1", production_type="dry"):
    """Function that takes a variety, start_date and mothers as arguments and creates a batch
       with propagate_cuttings from the specified mothers and inserts metrics data for that batch"""
    todays_date = datetime.now()
    if start_date > todays_date:
        return print('Error: Please choose a start date that is not in the future')

    # Construct batch plan
    if production_type == 'dry':
        timeline = [
            {
                'name': 'propagation',
                'planned_length': 5
            },
            {
                'name': 'vegetation',
                'planned_length': 14
            },
            {
                'name': 'flowering',
                'planned_length': 22
            },
            {
                'name': 'harvesting',
                'planned_length': 3
            },
            {
                'name': 'drying',
                'planned_length': 10
            },
            {
                'name': 'qa',
                'planned_length': 10
            }
        ]
    elif production_type == 'oil':
        timeline = [
            {
                "name": "propagation",
                "days_after": 0
            },
            {
                "name": "vegetation",
                "days_after": 15
            },
            {
                "name": "flowering",
                "days_after": 26
            },
            {
                "name": "harvesting",
                "days_after": 3
            },
            {
                "name": "oil extraction",
                "days_after": 30
            },
            {
                "name": "qa",
                "days_after": None
            }
        ]

    plan = {
        'start_type': 'plants',
        'end_type': production_type,
        'timeline': timeline,
        'grow_room': room,
        'start_date': start_date.strftime('%Y-%m-%d')
    }

    # CREATE BATCH WITH BATCH PLAN
    batch_data = {
        'organization_id': organization_id,
        'created_by': USER_ID,
        'timestamp': start_date.strftime('%Y-%m-%d'),
        'name': variety,
        'type': 'batch',
        'variety': variety,
        'plan': plan
    }

    batch_id = insert_into_db('inventories', batch_data).get('id')

    if not batch_id:
        print('Error creating a batch')
        return DATABASE.dedicated_connection().rollback()

    # UPDATE STAGE TO PROPAGATION
    stage = 'propagation'
    update_stage_id = update_stage(
        organization_id,
        batch_id,
        stage,
        start_date.strftime('%Y-%m-%d')
    )

    if not update_stage_id:
        print('Error updating to propagation stage')
        return DATABASE.dedicated_connection().rollback()

    # UPDATE ROOM
    update_room_data = {
        'organization_id': organization_id,
        'created_by': USER_ID,
        'timestamp': start_date.strftime('%Y-%m-%d'),
        'name': 'update_room',
        'to_room': 'Propagation Room',
        'inventory_id': batch_id
    }

    update_room_id = insert_into_db('activities', update_room_data).get('id')

    if not update_room_id:
        print('Error updating the room')
        return DATABASE.dedicated_connection().rollback()

    # PROPAGATE CUTTINGS FROM MOTHERS TO BATCH
    # propagate_cuttings_ids = propagate_cuttings(
    #     organization_id,
    #     batch_id,
    #     mothers,
    #     start_date.strftime('%Y-%m-%d')
    # )

    # if not propagate_cuttings_ids:
    #     print('Error adding propagate cuttings activities')
    #     return DATABASE.dedicated_connection().rollback()

    # UPDATE STAGE TO VEGETATION
    vegetation_start_date = start_date + timedelta(days=5)

    if vegetation_start_date > todays_date:
        return print('Stopped before vegetation stage')

    stage = 'vegetation'
    update_stage_id = update_stage(
        organization_id,
        batch_id,
        stage,
        vegetation_start_date.strftime('%Y-%m-%d')
    )

    if not update_stage_id:
        print('Error updating to vegetation stage')
        return DATABASE.dedicated_connection().rollback()

    # UPDATE ROOM
    update_room_data = {
        'organization_id': organization_id,
        'created_by': USER_ID,
        'timestamp': vegetation_start_date.strftime('%Y-%m-%d'),
        'name': 'update_room',
        'to_room': room,
        'inventory_id': batch_id
    }

    update_room_id = insert_into_db('activities', update_room_data).get('id')

    if not update_room_id:
        print('Error updating the room')
        return DATABASE.dedicated_connection().rollback()

    # UPDATE STAGE TO FLOWERING
    flowering_start_date = vegetation_start_date + timedelta(days=15)
    if flowering_start_date > todays_date:
        return print('Stopped before flowering stage')

    stage = 'flowering'
    update_stage_id = update_stage(
        organization_id,
        batch_id,
        stage,
        flowering_start_date.strftime('%Y-%m-%d')
    )

    if not update_stage_id:
        print('Error updating to flowering stage')
        return DATABASE.dedicated_connection().rollback()

    # INSERT METRICS FOR BATCH
    insert_metrics_into_db(batch_id, start_date,
                           organization_id=organization_id)

    # UPDATE STAGE TO HARVESTING
    harvesting_start_date = flowering_start_date + timedelta(days=50)
    if harvesting_start_date > todays_date:
        return print('Stopped before harvesting stage begins')

    stage = 'harvesting'

    update_stage_id = update_stage(
        organization_id,
        batch_id,
        stage,
        harvesting_start_date.strftime('%Y-%m-%d')
    )

    if not update_stage_id:
        print('Error updating to harvesting stage')
        return DATABASE.dedicated_connection().rollback()

    # Record bud harvest weight
    harvesting_end_date = harvesting_start_date + timedelta(days=3)
    if harvesting_end_date > todays_date:
        return print('Stopped before harvesting stage ends')

    # total_plants = len(mothers) * CUTTINGS_COUNT
    total_plants = CUTTINGS_COUNT
    total_wet_weight = total_plants * 60

    bud_harvest_data = {
        'organization_id': organization_id,
        'created_by': USER_ID,
        'timestamp': harvesting_end_date.strftime('%Y-%m-%d'),
        'name': 'batch_record_harvest_weight',
        'from_inventory_id': batch_id,
        'to_inventory_id': batch_id,
        'from_qty_unit': 'plants',
        'to_qty_unit': 'g-wet',
        'from_qty': total_plants,
        'to_qty': total_wet_weight
    }

    bud_harvest_id = insert_into_db('activities', bud_harvest_data).get('id')

    if not bud_harvest_id:
        print('Error recording bud harvest weight')

        return DATABASE.dedicated_connection().rollback()

    if production_type == 'dry':
        # UPDATE STAGE TO DRYING
        drying_start_date = harvesting_end_date
        if drying_start_date > todays_date:
            return print('Stopped before drying stage begins')

        stage = 'drying'

        update_stage_id = update_stage(
            organization_id,
            batch_id,
            stage,
            drying_start_date.strftime('%Y-%m-%d')
        )

        if not update_stage_id:
            print('Error updating to drying stage')

            return DATABASE.dedicated_connection().rollback()

        # UPDATE ROOM
        update_room_data = {
            'organization_id': organization_id,
            'created_by': USER_ID,
            'timestamp': drying_start_date.strftime('%Y-%m-%d'),
            'name': 'update_room',
            'to_room': 'Drying Room',
            'inventory_id': batch_id
        }

        update_room_id = insert_into_db(
            'activities', update_room_data).get('id')

        if not update_room_id:
            print('Error updating the room')
            return DATABASE.dedicated_connection().rollback()

        # Record dry weight
        drying_end_date = drying_start_date + timedelta(days=10)
        if drying_end_date > todays_date:
            return print('Stopped before drying stage ends')

        total_dry_weight = total_plants * 15
        dry_weight_data = {
            'organization_id': organization_id,
            'created_by': USER_ID,
            'timestamp': drying_end_date.strftime('%Y-%m-%d'),
            'name': 'batch_record_dry_weight',
            'from_inventory_id': batch_id,
            'to_inventory_id': batch_id,
            'from_qty_unit': 'g-wet',
            'to_qty_unit': 'dry',
            'from_qty': total_wet_weight,
            'to_qty': total_dry_weight
        }

        dry_weight_id = insert_into_db('activities', dry_weight_data).get('id')

        if not dry_weight_id:
            print('Error recording dry weight')
            return DATABASE.dedicated_connection().rollback()

        # UPDATE STAGE TO CURING
        # curing_start_date = drying_end_date
        # if curing_start_date > todays_date:
        #     return print('Stopped before curing stage begins')

        # stage = 'curing'

        # update_stage_id = update_stage(
        #     organization_id,
        #     batch_id,
        #     stage,
        #     curing_start_date.strftime('%Y-%m-%d')
        # )

        # if not update_stage_id:
        #     print('Error updating to curing stage')

        #     return DATABASE.dedicated_connection().rollback()

        # # Record final yield
        # curing_end_date = curing_start_date + timedelta(days=14)
        # if curing_end_date > todays_date:
        #     return print('Stopped before curing stage ends')

        # total_cured_weight = total_plants * 13
        # final_yield_data = {
        #     'organization_id': organization_id,
        #     'created_by': USER_ID,
        #     'timestamp': curing_end_date.strftime('%Y-%m-%d'),
        #     'name': 'batch_record_final_yield',
        #     'from_inventory_id': batch_id,
        #     'to_inventory_id': batch_id,
        #     'from_qty_unit': 'g-dry',
        #     'to_qty_unit': 'g-dry',
        #     'from_qty': total_dry_weight,
        #     'to_qty': total_cured_weight
        # }

        # final_yield_id = insert_into_db(
        #     'activities', final_yield_data).get('id')

        # if not final_yield_id:
        #     print('Error recording final yield')

        #     return DATABASE.dedicated_connection().rollback()

    elif production_type == 'oil':
        # UPDATE STAGE TO EXTRACTION
        extraction_start_date = harvesting_end_date
        if extraction_start_date > todays_date:
            return print('Stopped before extraction stage begins')

        stage = 'oil_extraction'

        update_stage_id = update_stage(
            organization_id,
            batch_id,
            stage,
            extraction_start_date.strftime('%Y-%m-%d')
        )

        if not update_stage_id:
            print('Error updating to extraction stage')

            return DATABASE.dedicated_connection().rollback()

        # Record extracted weight
        extraction_end_date = extraction_start_date + timedelta(days=40)
        if extraction_end_date > todays_date:
            return print('Stopped before oil extraction stage ends')

        oil_density = 2

        total_extracted_weight = total_plants * (1 / oil_density)
        extracted_weight_data = {
            'organization_id': organization_id,
            'created_by': USER_ID,
            'timestamp': extraction_end_date.strftime('%Y-%m-%d'),
            'name': 'batch_record_oil_weight',
            'from_inventory_id': batch_id,
            'to_inventory_id': batch_id,
            'from_qty_unit': 'g-wet',
            'to_qty_unit': 'g-oil',
            'from_qty': total_wet_weight,
            'to_qty': total_extracted_weight,
            'oil_density': oil_density
        }

        extracted_weight_id = insert_into_db(
            'activities', extracted_weight_data).get('id')

        if not extracted_weight_id:
            print('Error recording extracted weight')
            return DATABASE.dedicated_connection().rollback()

    if production_type == "dry":
        total_weight = total_cured_weight
        end_date = curing_end_date
    elif production_type == "oil":
        total_weight = total_extracted_weight
        end_date = extraction_end_date

    # UPDATE STAGE TO QA
    qa_start_date = end_date
    if qa_start_date > todays_date:
        return print('Stopped before qa stage')

    stage = 'qa'

    update_stage_id = update_stage(
        organization_id,
        batch_id,
        stage,
        qa_start_date.strftime('%Y-%m-%d')
    )

    if not update_stage_id:
        print('Error updating to qa stage')
        return DATABASE.dedicated_connection().rollback()

    # Commit DB transaction

    # MOVE TO LOT
    qa_end_date = qa_start_date + timedelta(days=15)
    if qa_end_date > todays_date:
        return print('Stopped before moving to lot')

    lot_start_date = qa_end_date

    target_qty_unit = "dry"
    sku_qty = 15

    # CREATE LOT
    lot_data = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        "timestamp": lot_start_date.strftime('%Y-%m-%d'),
        "name": "{0}-{1}".format(lot_start_date.strftime('%Y-%m-%d'), variety),
        "type": "lot",
        "variety": variety,
        "from_inventory_id": batch_id,
        "stats": "{{ \"{0}\": {1} }}".format(target_qty_unit, total_weight)
    }

    result = insert_into_db('inventories', lot_data)

    if not result:
        return print("Failed to create lot")

    lot_id = result["id"]

    # CREATE LOT ACTIVITY
    create_lot_data = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        "timestamp": qa_end_date,
        "name": "create_lot",
        "variety": variety,
        "inventory_id": lot_id,
        "from_inventory_id": batch_id,
    }

    insert_into_db('activities', create_lot_data)

    # TRANSFER TO LOT
    transfer_inventory_data = {
        "organization_id": organization_id,
        "created_by": USER_ID,
        "timestamp": qa_end_date,
        "name": "transfer_inventory",
        "to_inventory_id": lot_id,
        "from_inventory_id": batch_id,
        "from_qty": total_weight,
        "to_qty": total_weight,
        "approvedBy": "daniel.favand@wilcompute.com"
    }

    # CREATE LOT ITEMS FOR ENTIRE LOT
    for i in range(1, total_weight, sku_qty):
        # CREATE LOT ITEM
        lot_item_data = {
            "organization_id": organization_id,
            "created_by": USER_ID,
            "timestamp": lot_start_date.strftime('%Y-%m-%d'),
            "name": "{0}-{1}".format(lot_start_date.strftime('%Y-%m-%d'), variety),
            "type": "lot item",
            "variety": variety,
            "sku_name": "{}-SKU".format(variety),
            "from_inventory_id": lot_id,
            "stats": "{{ \"{0}\": {1} }}".format(target_qty_unit, sku_qty)
        }

        result = insert_into_db('inventories', lot_item_data)
        if not result:
            return print("Failed to create a lot item")

        lot_item_id = result["id"]

        # CREATE LOT ITEM ACTIVITY
        create_lot_item_data = {
            "organization_id": organization_id,
            "created_by": USER_ID,
            "timestamp": qa_end_date,
            "name": "create_lot_item",
            "variety": variety,
            "sku_name": "{}-SKU".format(variety),
            "inventory_id": lot_item_id,
            "from_inventory_id": lot_id,
        }

        insert_into_db('activities', create_lot_item_data)


def main():
    """Main function that takes a start_date and mothers as arguments"""
    parser = argparse.ArgumentParser(
        description='Create a batch and insert metrics data into database'
    )

    parser.add_argument(
        '--variety',
        type=str,
        help='Variety for the batch',
        required=True
    )
    parser.add_argument(
        '--start_date',
        type=str,
        help='Start date for the batch (Format: YYYY-MM-DD)',
        required=True
    )
    parser.add_argument(
        '--mothers',
        type=int,
        nargs='+',
        help='Mother ids to propagate cuttings from',
        required=True
    )

    args = parser.parse_args()

    variety = args.variety
    start_date = datetime.strptime(args.start_date, '%Y-%m-%d')
    mothers = args.mothers

    create_batch_with_metrics(variety, start_date, mothers)


if __name__ == "__main__":
    # Begin DB transaction
    DATABASE.dedicated_connection().begin()

    main()

    # Commit DB transaction
    DATABASE.dedicated_connection().commit()
