# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
import psycopg2
import psycopg2.extras
import random
import copy 
from db_functions import DATABASE, insert_into_db


from constants import USER_ID
from class_errors import DatabaseError
from random import randint, sample, randrange
from create_crm_account import get_crm_accounts_by_id
from utilities import get_random_room, get_random_date_before_today, get_random_date_after_today, select_from_db, update_timestamp, get_random_user
from shared_activities import update_room, transfer_inventory, propagate_cuttings, create_signature
from create_taxonomy_option import get_taxonomy_option_by_taxonomy_name
from datetime import datetime, timedelta
from insert_metrics_for_batch import insert_metrics_into_db

from activities.create_batch import CreateBatch
from activities.batch_plan_update import BatchPlanUpdate
from activities.update_stage import UpdateStage
from activities.batch_record_harvest_weight import BatchRecordBudHarvestWeight
from activities.batch_record_dry_weight import RecordDryWeight
from activities.batch_record_cured_weight import RecordCuredWeight
from activities.batch_record_final_yield import BatchRecordFinalYield
from activities.batch_record_crude_oil_weight import RecordCrudeOilWeight
from activities.batch_record_distilled_oil_weight import RecordDistilledOilWeight
from activities.batch_visual_inspection import BatchVisualInspection

def create_batches(org_id):
    try:
        data_1 = get_batch_data(org_id) 
        data_2 = get_batch_data(org_id) 
        data = data_1 + data_2
        data_filtered  = list(filter(lambda x: x['name'] not in ('planning'), data))
        ramdom_batches_to_be_overdue = sample(data_filtered, 2)  
        count_room = 0
        start_type_list = []
        qa_end_stats = ['plants', 'g-wet', 'dry', 'cured', 'crude', 'distilled', 'plants']
        for i, batch_data in enumerate(data):
            # make sure at least the room has one batch
            if (batch_data['name'] not in ('planning', 'propagation', 'drying') and count_room <= 6):
                count_room += 1
                room = 'Bay {}'.format(count_room)   
            else:           
                room = get_random_room(org_id, False)['name']

            data_dict = {
                'harvesting': {'start_type':['seed', 'g-wet', 'plants'], 'end_type': 'g-wet'},
                'drying': {'start_type':['seed', 'g-wet', 'dry'], 'end_type': 'dry'},
                'curing': {'start_type':['seed', 'dry', 'cured'], 'end_type': 'cured'},
                'extracting_crude_oil': {'start_type':['dry', 'cured', 'crude'], 'end_type': 'crude'},
                'distilling': {'start_type':['plants', 'crude', 'distilled'], 'end_type': 'distilled'},
            }
            end_stats = ['g-wet', 'dry', 'cured', 'crude', 'distilled']
            if (batch_data['name'] in ('planning', 'propagation', 'vegetation', 'flowering')):
                #start_type = random.choice(['seeds', 'plants'])
                start_type = 'plants'
                end_type = random.choice(end_stats)
            elif(batch_data['name'] == 'germinating'):
                #start_type = 'seeds'
                start_type = 'plants'
                end_type = random.choice(end_stats)
            elif (batch_data['name'] in ('harvesting', 'drying', 'curing', 'extracting_crude_oil', 'distilling')):
                #start_type = data_dict[batch_data['name']]['start_type'][0]
                start_type = 'plants'
                end_type =  data_dict[batch_data['name']]['end_type']
                data_dict[batch_data['name']]['start_type'].pop(0)
            # stage == 'qa'
                
            start_date = get_start_date(org_id, batch_data['name'], start_type, end_type)
            overdue = batch_data in ramdom_batches_to_be_overdue                        
            if (overdue):
                plan_day = get_day_length(batch_data['name'])                
                start_date = start_date - timedelta(days=plan_day+randint(1,10))

            batch_data_copy = copy.copy(batch_data)
            batch_data_copy['name'] = 'qa'
            result = create_batch(org_id, start_type, end_type, start_date, batch_data_copy, room)
            result = create_batch(org_id, start_type, end_type, start_date, batch_data, room)
            # to ensure that we have batches in early stages to get projected yield
            result = create_new_batch(org_id, start_type, end_type, start_date, batch_data, room)
    except:
        print('error at creating batches on create_batch')
        raise

# loop backward till fist growing stage (propagation) to find the start_date
def get_start_date(org_id, stage, start_type, end_type):
    start_date = datetime.now()
    stages = genarate_stages(start_type, end_type)
    index = stages.index(stage)
    stages = stages[0 : index]
    for stage in stages:
        plan_day = get_day_length(stage)
        start_date = start_date - timedelta(days=plan_day)
    return start_date

# AND CAST(stats->>'plants' AS integer) > 0 change to ???
def get_batch_data(org_id):
    params = {'organization_id': org_id}
    query = '''       
        SELECT T1.name, inv.id, inv.type, inv.variety
        FROM (
            SELECT T2.name,
                -- Get a randon inventory for mother and received inventory
                (SELECT id FROM inventories 
                    WHERE organization_id = %(organization_id)s 
                        AND type in ('mother', 'received inventory')
                        AND ((attributes->>'stage' is not null AND attributes->>'stage' = 'received-approved') OR attributes->>'stage' is null)
                        AND T2 = T2	  
                    ORDER BY random() LIMIT 1 ) as inventory_id
            FROM (  
                -- Generates series of 1 each for planning, germinating, propagation, vegetation, flowering
                SELECT op.name, generate_series(1, 1)
                FROM taxonomies AS t
                    INNER JOIN taxonomy_options AS op ON t.id = op.taxonomy_id AND t.organization_id = op.organization_id
                WHERE t.organization_id =  %(organization_id)s AND
                    t.name = 'stages' AND
                    op.name not in ('received-unapproved','received-approved','seedling') AND
					op.name != 'qa' AND op.name != 'planning' AND op.name != 'curing' AND op.name != 'drying' AND op.name != 'distilling' AND op.name != 'harvesting' AND op.name != 'extracting_crude_oil' AND op.name != 'germinating'
                UNION ALL
                -- Generates series of 3 each for harvesting, drying, curing, extracting_crude_oil, distilling stages
                SELECT op.name, generate_series(1, 1)
                FROM taxonomies AS t
                    INNER JOIN taxonomy_options AS op ON t.id = op.taxonomy_id AND t.organization_id = op.organization_id
                WHERE t.organization_id = %(organization_id)s AND
                    t.name = 'stages' AND
                    op.name not in ('received-unapproved','received-approved','seedling') AND 
				    op.name != 'qa' AND op.name != 'planning' AND op.name != 'germinating' AND op.name != 'propagation' AND op.name != 'vegetation' AND op.name != 'flowering' 
            ) AS T2
        ) AS T1 
        INNER JOIN inventories AS inv on inv.id = T1.inventory_id 
    '''
    
    return select_from_db(query, params)


def transfer_to_qa(end_date, org_id, batch_id, room):
    plan_day = get_day_length('qa')
    start_date_qa = end_date + timedelta(days=plan_day)
    update_stage(org_id, batch_id, 'qa', start_date_qa)
    visual_inpection(org_id, batch_id, start_date_qa+timedelta(days=6))
    print(batch_id, ' in qa stage, in room', room)  

def create_new_batch(org_id, start_type, end_type, start_date, batch_data, room):

    start_date = datetime.now()
    
    createBatchData = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": "create_batch",
      "variety": batch_data['variety']
    }

    try:
        stage = batch_data["name"]
        start_date_planning = start_date - timedelta(days=30)

        resultCreateBatch = CreateBatch.do_activity(createBatchData, {})
        batch_id = resultCreateBatch['inventory_id']
        
        # update timestamp for inventories and activity
        update_timestamp('inventories', batch_id, start_date_planning)
        update_timestamp('activities', resultCreateBatch['activity_id'], start_date)

        batch_plan_update(org_id, batch_id, start_type, end_type, start_date)    
       
        # UPDATE STAGE TO PLANNING        
        update_stage(org_id, batch_id, 'planning', start_date_planning)
        
        if (stage == 'planning' or stage == 'germinating'): 
            print(batch_id, ' in planning stage, in room', room)        
            return resultCreateBatch

        # UPDATE STAGE TO PROPAGATION
        start_date_propagation = start_date
        update_stage(org_id, batch_id, 'propagation', start_date_propagation)
        update_room(org_id, batch_id, 'Propagation Room', start_date_propagation)     
        
        qty_plants = randint(100,300)
        if(batch_data['type'] == 'mother'):
            # do propagation
            propagate_cuttings(org_id, batch_data['id'], batch_id, start_date_propagation, qty_plants)
        else:
            # do transfer
            transfer_inventory(org_id, batch_data['id'], batch_id, batch_data['variety'], start_date_propagation, qty_plants)

        if (stage == 'propagation'): 
            print(batch_id, ' in propgation stage, in room Propagation Room')                
            return resultCreateBatch
    except:
        print('error at creating batch on create_batch')
        raise



def create_batch(org_id, start_type, end_type, start_date, batch_data, room):
    createBatchData = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": "create_batch",
      "variety": batch_data['variety']
    }

    try:
        stage = batch_data["name"]
        start_date_planning = start_date - timedelta(days=30)

        resultCreateBatch = CreateBatch.do_activity(createBatchData, {})
        batch_id = resultCreateBatch['inventory_id']
        
        # update timestamp for inventories and activity
        update_timestamp('inventories', batch_id, start_date_planning)
        update_timestamp('activities', resultCreateBatch['activity_id'], start_date)

        batch_plan_update(org_id, batch_id, start_type, end_type, start_date)    
       
        # UPDATE STAGE TO PLANNING        
        update_stage(org_id, batch_id, 'planning', start_date_planning)
        
        if (stage == 'planning' or stage == 'germinating'): 
            print(batch_id, ' in planning stage, in room', room)        
            return resultCreateBatch

            
        
        # UPDATE STAGE TO PROPAGATION
        start_date_propagation = start_date
        update_stage(org_id, batch_id, 'propagation', start_date_propagation)
        update_room(org_id, batch_id, 'Propagation Room', start_date_propagation)     
        
        qty_plants = randint(100,300)
        if(batch_data['type'] == 'mother'):
            # do propagation
            propagate_cuttings(org_id, batch_data['id'], batch_id, start_date_propagation, qty_plants)
        else:
            # do transfer
            transfer_inventory(org_id, batch_data['id'], batch_id, batch_data['variety'], start_date_propagation, qty_plants)

        if (stage == 'propagation'): 
            print(batch_id, ' in propgation stage, in room Propagation Room')                
            return resultCreateBatch

        # UPDATE STAGE TO VEGETATION
        plan_day = get_day_length('vegetation')
        start_date_vegetation = start_date_propagation + timedelta(days=plan_day)
        update_stage(org_id, batch_id, 'vegetation', start_date_vegetation)
        update_room(org_id, batch_id, room, start_date_vegetation)  
        if (stage == 'vegetation'): 
            print(batch_id, ' in vegetation stage, in room', room)   
            return resultCreateBatch

        # UPDATE STAGE TO FLOWERING
        plan_day = get_day_length('flowering')
        start_date_flowering = start_date_vegetation + timedelta(days=plan_day)
        update_stage(org_id, batch_id, 'flowering', start_date_flowering)
        
        # insert metrics
        insert_metrics_into_db(batch_id, start_date, org_id)
        
        if (stage == 'flowering'):  
            print(batch_id, ' in flowering stage, in room', room)   
            return resultCreateBatch
            
        # UPDATE STAGE TO HARVESTING
        plan_day = get_day_length('harvesting')
        start_date_harvesting = start_date_flowering + timedelta(days=plan_day)
        update_stage(org_id, batch_id, 'harvesting', start_date_harvesting)

        if (stage == 'qa' and end_type == 'plants'):
            transfer_to_qa(start_date_harvesting, org_id, batch_id, room)
            return resultCreateBatch

        # Record bud harvest weight
        harvesting_end_date = start_date_harvesting + timedelta(days=3)
        end_date = harvesting_end_date
        result_haverst_weight = record_bud_harvest_weight(org_id, batch_id, qty_plants,  harvesting_end_date)
        bud_weight = result_haverst_weight["bud_weight"]
        
        if (stage == 'qa' and end_type  == 'g-wet'):
            transfer_to_qa(end_date, org_id, batch_id, room)
            return resultCreateBatch
              
        if (stage == 'harvesting'): 
            print(batch_id, ' in harvesting stage, in room', room)   
            return resultCreateBatch
        if end_type == 'dry' or end_type == 'cured':
            # UPDATE STAGE TO DRYING
            plan_day = get_day_length('drying')
            start_date_drying = start_date_harvesting + timedelta(days=plan_day)
            update_stage(org_id, batch_id, 'drying', start_date_drying)
            update_room(org_id, batch_id, 'Drying Room', start_date_drying) 
            
            # Record dry weigth
            drying_end_date = start_date_drying + timedelta(days=10)
            end_date = drying_end_date
            result_dry_weight = record_dry_weight(org_id, batch_id, bud_weight , drying_end_date, 'batch_record_dry_weight')
            total_weight = result_dry_weight["dry_weight"]

            if (stage == 'drying'): 
                print(batch_id, ' in drying stage, in room', room)  
                return resultCreateBatch
            
            if (stage == 'qa' and end_type == 'dry'):
                transfer_to_qa(end_date, org_id, batch_id, room)
                return resultCreateBatch

            # UPDATE STAGE TO CURING
            plan_day = get_day_length('curing')
            start_date_curing = start_date_drying + timedelta(days=plan_day)
            update_stage(org_id, batch_id, 'curing', start_date_curing)
           
            # Record cured
            curing_end_date = start_date_curing + timedelta(days=14)
            end_date = curing_end_date
            result_cured_weight = record_dry_weight(org_id, batch_id, total_weight, drying_end_date, 'batch_record_cured_weight')

            if (stage == 'curing'): 
                print(batch_id, ' in curing stage, in room', room)  
                return resultCreateBatch
            if (stage == 'qa' and end_type == 'cured'):
                transfer_to_qa(end_date, org_id, batch_id, room)
                return resultCreateBatch
        elif end_type == 'crude' or end_type == 'distilled':
            # UPDATE STAGE TO EXTRACTION
            plan_day = get_day_length('extracting_crude_oil')
            start_date_extraction = start_date_harvesting + timedelta(days=plan_day)
            update_stage(org_id, batch_id, 'extracting_crude_oil', start_date_extraction)
           
            # Record extracted weight 
            extraction_end_date = start_date_extraction + timedelta(days=40)
            end_date = extraction_end_date
            result_oil_weight = record_oil_weight(org_id, batch_id, bud_weight, extraction_end_date, 'batch_record_crude_oil_weight')
            total_weight = result_oil_weight["oil_weight"]

            if (stage == 'extracting_crude_oil'):  
                print(batch_id, ' in extracting crude oil stage, in room', room)  
                return resultCreateBatch
            if (stage == 'qa' and end_type == 'crude'):
                transfer_to_qa(end_date, org_id, batch_id, room)
                return resultCreateBatch
            # UPDATE STAGE TO DISTILLING
            plan_day = get_day_length('distilling')
            start_date_distilling = start_date_extraction + timedelta(days=plan_day)
            update_stage(org_id, batch_id, 'distilling', start_date_distilling)
            # Record distilled
            distilling_end_date = start_date_distilling + timedelta(days=14)
            end_date = distilling_end_date
            result_oil_weight = record_oil_weight(org_id, batch_id, total_weight, extraction_end_date, 'batch_record_distilled_oil_weight')

            if (stage == 'distilling'): 
                print(batch_id, ' in distilling stage, in room', room)  
                return resultCreateBatch
            if (stage == 'qa' and end_type == 'distilled'):
                transfer_to_qa(end_date, org_id, batch_id, room)
                return resultCreateBatch

    except:
        print('error at creating batch on create_batch')
        raise

def batch_plan_update(org_id, inventory_id, start_type, end_type, start_date):     

    plan = {
        'start_type': start_type,
        'end_type': end_type,
        'timeline': get_timeline_plan(start_type, end_type),
        'start_date': start_date.strftime('%Y-%m-%d')
    }
    
    batchPlanUpdateData = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": "batch_plan_update",
      "inventory_id": inventory_id, 
      "plan": plan,
    }

    
    try:
        result = BatchPlanUpdate.do_activity(batchPlanUpdateData, {})       
        update_timestamp('activities', result['activity_id'], start_date)
        return result 
    except:
        print('error at updating batch plan on create_batch')
        raise 

def genarate_stages(start, end):
    startStats = ['seeds', 'plants', 'g-wet', 'dry', 'cured', 'crude', 'distilled']
    stages = ['germinating', 'propagation', 'harvesting', 'drying', 'curing', 'extracting_crude_oil', 'distilling']
    fromIndex = startStats.index(start)
    toIndex = startStats.index(end)
    startStages = []
    if fromIndex <= 1 :
        startStages = ['propagation', 'vegetation', 'flowering', 'harvesting']
    if (fromIndex == 0): 
        startStages.insert(0,'germinating')
    if (fromIndex == 2):
        startStages.insert(0,'harvesting')
    if (fromIndex == 3):
        startStages.insert(0,'drying')
    startStages.insert(0,'planning')

    if (start == end):
      return ['planning', stages[fromIndex], 'qa']
    elif (start == 'dry' and end == 'cured'):
      return ['planning', 'drying', 'curing', 'qa']
    elif end == 'plants':
      return startStages + ['qa']
    elif fromIndex <= 3 and toIndex >= 5:
      return startStages + stages[5 : toIndex + 1] + ['qa']
    else:
      return startStages + stages[max(fromIndex, 3): toIndex + 1] + ['qa']

def get_timeline_plan(start, end):
    stages = genarate_stages(start, end)
    timeline = []
    for stage in stages:
        timeline.append(
            {
                'name': stage,
                'planned_length': get_day_length(stage)
            })
    return timeline

def get_day_length(stage):    
    all_stages = ['planning', 'germinating', 'propagation','vegetation', 'flowering', 'harvesting', 'drying', 'curing', 'extracting_crude_oil', 'distilling', 'qa']
    planned_length = [5, 10, 15, 8, 15, 28, 15, 10, 20, 13, 10]
    return planned_length[all_stages.index(stage)]

def update_stage(org_id, inventory_id, stage, timestamp):
    updateStageData = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": "update_stage",
      "inventory_id": inventory_id, 
      "to_stage": stage,
    }
    
    try:
        result = UpdateStage.do_activity(updateStageData, {})        
        update_timestamp('activities', result['activity_id'], timestamp)
        return result 
    except:
        print('error at updating stage on create_batch')
        raise 
        
def record_bud_harvest_weight(org_id, inventory_id, plants_count, timestamp):
    bud_weight = plants_count * 40

    weighed_by_user = get_random_user(org_id)
    checked_by_user = get_random_user(org_id)
    approved_by_user = get_random_user(org_id)


    batch_record_harvest_weight_data = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": "batch_record_harvest_weight",
      "from_inventory_id": inventory_id,
      "from_qty": plants_count,
      "from_qty_unit": "plants",
      "to_inventory_id": inventory_id,
      "to_qty": bud_weight,
      "to_qty_unit": "g-wet",
      "weighed_by": weighed_by_user["email"],
      "checked_by": checked_by_user["email"],
      "approved_by": approved_by_user["email"],
    }

    try:
        result = BatchRecordBudHarvestWeight.do_activity(batch_record_harvest_weight_data, {})
        update_timestamp('activities', result['activity_id'], timestamp)
        create_signature(
            org_id, result['activity_id'], "weighed_by", weighed_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "checked_by", checked_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "approved_by", approved_by_user["id"], timestamp)
        result["bud_weight"] = bud_weight
        return result 
    except:
        print('error at recording bud harvest weight on create_batch')
        raise 

def record_dry_weight(org_id, inventory_id, bud_weight, timestamp, activity_name):
    dry_weight = bud_weight * 0.20
    if (activity_name == 'batch_record_dry_weight'):
        from_qty_unit = 'g-wet'
        to_qty_unit = 'dry'
    else:
        from_qty_unit = 'dry'
        to_qty_unit = 'cured'
    weighed_by_user = get_random_user(org_id)
    checked_by_user = get_random_user(org_id)
    approved_by_user = get_random_user(org_id)
    
    batch_record_dry_weight_data = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": activity_name,
      "from_inventory_id": inventory_id,
      "from_qty": bud_weight,
      "from_qty_unit": from_qty_unit,
      "to_inventory_id": inventory_id,
      "to_qty": dry_weight,
      "to_qty_unit": to_qty_unit,
      "weighed_by": get_random_user(org_id)["email"],
      "checked_by": get_random_user(org_id)["email"],
      "approved_by": get_random_user(org_id)["email"],
    }

    try:
        if (activity_name == 'batch_record_dry_weight'):
            result = RecordDryWeight.do_activity(batch_record_dry_weight_data, {})
        else:
            result = RecordCuredWeight.do_activity(batch_record_dry_weight_data, {})
        update_timestamp('activities', result['activity_id'], timestamp)
        create_signature(
            org_id, result['activity_id'], "weighed_by", weighed_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "checked_by", checked_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "approved_by", approved_by_user["id"], timestamp)
        result["dry_weight"] = dry_weight
        return result 
    except:
        print('error at recording dry weight on create_batch')
        raise 

def record_final_weight(org_id, inventory_id, dry_weight, timestamp):
    final_weight = dry_weight

    weighed_by_user = get_random_user(org_id)
    checked_by_user = get_random_user(org_id)
    approved_by_user = get_random_user(org_id)

    batch_record_final_yield_data = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": "batch_record_final_yield",
      "from_inventory_id": inventory_id,
      "from_qty": dry_weight,
      "from_qty_unit": "g-dry",
      "to_inventory_id": inventory_id,
      "to_qty": final_weight,
      "to_qty_unit": "cured",
      "weighed_by": get_random_user(org_id)["email"],
      "checked_by": get_random_user(org_id)["email"],
      "approved_by": get_random_user(org_id)["email"],
    }

    try:
        result = BatchRecordFinalYield.do_activity(batch_record_final_yield_data, {})        
        update_timestamp('activities', result['activity_id'], timestamp)
        create_signature(
            org_id, result['activity_id'], "weighed_by", weighed_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "checked_by", checked_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "approved_by", approved_by_user["id"], timestamp)
        result["final_weight"] = final_weight
        return result 
    except:
        print('error at recording final harvest weight on create_batch')
        raise 

def record_oil_weight(org_id, inventory_id, bud_weight, timestamp, activity_name):
    weighed_by_user = get_random_user(org_id)
    approved_by_user = get_random_user(org_id)
    if (activity_name == 'batch_record_crude_oil_weight'):
        from_qty_unit = 'g-wet'
        to_qty_unit = 'crude'
    else:
        from_qty_unit = 'crude'
        to_qty_unit = 'distilled'
    oil_density = 2
    oil_weight = bud_weight * (1 / oil_density)
    batch_record_oil_data = {
      "organization_id": org_id,
      "created_by": USER_ID,
      "name": activity_name,
      "from_inventory_id": inventory_id,
      "from_qty": bud_weight,
      "from_qty_unit": from_qty_unit,
      "to_inventory_id": inventory_id,
      "to_qty": oil_weight,
      "to_qty_unit": to_qty_unit,
      "oil_density": oil_density,
      "weighed_by": weighed_by_user["email"],
      "approved_by": approved_by_user["email"],
    }

    try:
        if (activity_name == 'batch_record_crude_oil_weight'):
            result = RecordCrudeOilWeight.do_activity(batch_record_oil_data, {}) 
        else:
            result = RecordDistilledOilWeight.do_activity(batch_record_oil_data, {}) 
        update_timestamp('activities', result['activity_id'], timestamp)
        create_signature(
            org_id, result['activity_id'], "weighed_by", weighed_by_user["id"], timestamp)
        create_signature(
            org_id, result['activity_id'], "approved_by", approved_by_user["id"], timestamp)
        result["oil_weight"] = oil_weight
        return result 
    except:
        print('error at recording final harvest weight on create_batch')
        raise 


def visual_inpection(org_id, from_inventory_id, timestamp):

    inspected_by_user = get_random_user(org_id)
    approved_by_user = get_random_user(org_id)

    visual_inspection_data = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "batch_visual_inspection",
        "inventory_id": from_inventory_id,
        "inspection_result": 'pass',
        "description": "{} - passed".format(from_inventory_id),
        "inspected_by": inspected_by_user["email"],
        "approved_by": approved_by_user["email"],
        "to_test_status":  "batch-visual-inspection-pass"
    }

    try:
        result_visual_inspection = BatchVisualInspection.do_activity(visual_inspection_data, {})
        update_timestamp('activities', result_visual_inspection['activity_id'], (timestamp-timedelta(days=1)))
        create_signature(
            org_id, result_visual_inspection['activity_id'], "inspected_by", inspected_by_user["id"], timestamp)
        create_signature(
            org_id, result_visual_inspection['activity_id'], "approved_by", approved_by_user["id"], timestamp)
        result = result_visual_inspection
    except:
        print('error creating visual inspection sample on create_sample')
        raise 




def get_batches(org_id):
    params = {'org_id': org_id}
    query = '''        
        SELECT *, attributes->>'room' as room
        FROM inventories
        WHERE organization_id = %(org_id)s
        AND type = 'batch'
        ORDER BY random()
    '''
    return select_from_db(query, params)

if __name__ == "__main__":
    org_id = input("Type the organization's ID: ")  

    if (org_id):
        DATABASE.dedicated_connection().begin()
        try:
            create_mothers(org_id)
            DATABASE.dedicated_connection().commit()
        except:
            DATABASE.dedicated_connection().rollback()
