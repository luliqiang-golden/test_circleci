# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

import argparse
import psycopg2
import psycopg2.extras
import json
import datetime
import copy
import random

from db_functions import DATABASE
from datetime import datetime, timedelta
from utilities import select_from_db, get_random_user, update_timestamp, get_random_room
from shared_activities import transfer_inventory, update_room, create_signature
from constants import USER_ID, STANDARDIZED_LAB_RESULT
from create_taxonomy_option import get_taxonomy_option_data_from_name
from class_errors import DatabaseError

from activities.create_sample import BatchCreateSample
from activities.sample_sent_to_lab import SampleSentToLab
from activities.sample_lab_result_received import SampleLabResultReceived
from activities.sample_update_test_result import SampleUpdateTestResult
from activities.batch_qa_review import BatchQaReview


def create_samples(org_id):
    try:
        sample_data = get_sample_data(org_id)
        timestamp = sample_data["timestamp"]+timedelta(days=11)
        # create a random sample consisting of 3% to 6% of total quantity
        sample_quantity = round(random.uniform(0.03, 0.06) * float(sample_data["stats"]["g-dry"]["dry"]), 2)
        batch_in_qa = True
        

        # create 3 samples, only the last one will be send to lab
        for i in range(1, 4): 
            result_create_sample = create_sample(org_id, sample_data, sample_quantity, timestamp, batch_in_qa)

        # send result to lab
        send_sample_to_lab(org_id, sample_data["id"], result_create_sample["inventory_id"], sample_quantity, timestamp, batch_in_qa)

        # receive lab result
        sample_lab_result_received(org_id, sample_data["id"], result_create_sample["inventory_id"], timestamp, batch_in_qa)

        # update test result
        sample_update_test_result(org_id, sample_data["id"], result_create_sample["inventory_id"], timestamp, batch_in_qa)
        
        # release or reject by qa
        qa_review_result(org_id, sample_data["id"], timestamp)

        print("3 samples created and 1 has sent to lab")

    except:
        print('error creating samples on create_sample')
        raise 

def get_sample_data(org_id):
    params = { 'org_id': org_id }
    
    query = '''
        SELECT *
        FROM inventories AS t
        WHERE t.organization_id=%(org_id)s
        AND t.type = 'batch'
        AND t.attributes->>'stage' = 'qa'
        AND t.stats#>>'{g-dry,dry}'>'0'
        AND t.data#>>'{plan,end_type}' = 'dry'
        ORDER BY random() LIMIT 1
    '''
    return select_from_db(query, params)[0]

def create_sample(org_id, sample_data, sample_quantity, timestamp, batch_in_qa):
    sampled_by_user = get_random_user(org_id)
    approved_by_user = get_random_user(org_id)

    create_sample_data = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "create_sample",
        "from_inventory_id": sample_data["id"],
        "sampled_by": sampled_by_user["email"],
        "variety": sample_data["variety"],
        "approved_by": approved_by_user["email"],
        "to_test_status": "batch-create-sample",
        "batch_in_qa": batch_in_qa,
        "to_qty": 1,
        "to_qty_unit": "dry",
        "from_qty": 1,
        "from_qty_unit": "dry",
        "related_inventory_id": sample_data["id"],
    }

    try:
        result_sample = BatchCreateSample.do_activity(create_sample_data, {})
        update_timestamp('activities', result_sample['activity_id'], timestamp)
        create_signature(
            org_id, result_sample['activity_id'], "sampled_by", sampled_by_user["id"], timestamp)
        create_signature(
            org_id, result_sample['activity_id'], "approved_by", approved_by_user["id"], timestamp)
        transfer_inventory(org_id, sample_data["id"], result_sample["inventory_id"], sample_data["variety"], timestamp, sample_quantity, 'dry')
        update_room(org_id, result_sample["inventory_id"], get_random_room(org_id)['name'], timestamp) 
        return result_sample
    except:
        print('error creating sample on create_sample')
        raise 

def send_sample_to_lab(org_id, from_inventory_id, sample_id, sample_quantity, timestamp, batch_in_qa):
    sample_sent_by_user = get_random_user(org_id)
    send_sample_to_lab_data = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "sample_sent_to_lab",
        "related_inventory_id": from_inventory_id,
        "from_inventory_id": sample_id,
        "from_qty": sample_quantity,
        "from_qty_unit": "dry",
        "sample_sent_by": sample_sent_by_user["email"],
        "lab_name": "Steep Hill Lab Testing",
        "to_test_status": "sample-sent-to-lab",
        "batch_in_qa": batch_in_qa,
        "inventory_id": sample_id,
        "timestamp": timestamp,
    }

    try:
        result_send_lab = SampleSentToLab.do_activity(send_sample_to_lab_data, {})
        update_timestamp('activities', result_send_lab['activity_id'], (timestamp-timedelta(days=2)))
        create_signature(
            org_id, result_send_lab['activity_id'], "sample_sent_by", sample_sent_by_user["id"], timestamp)
        result = result_send_lab
    except:
        print('error sending sample to lab on create_sample')
        raise 

def sample_lab_result_received(org_id, from_inventory_id, sample_id, timestamp, batch_in_qa):
    uploaded_by_user = get_random_user(org_id)

    sample_lab_result_received_data = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "sample_lab_result_received",
        "from_inventory_id": sample_id,
        "related_inventory_id": from_inventory_id,
        "to_test_status": "sample-lab-result-received",
        "uploaded_by": uploaded_by_user["email"],
        "upload_id": 287,
        "batch_in_qa": batch_in_qa,
        "inventory_id": sample_id,
    }

    try:
        sample_lab_result_received = SampleLabResultReceived.do_activity(sample_lab_result_received_data, {})
        update_timestamp('activities', sample_lab_result_received['activity_id'], (timestamp+timedelta(days=3)))
        create_signature(
            org_id, sample_lab_result_received['activity_id'], "received_by", uploaded_by_user["id"], timestamp)
        result = sample_lab_result_received
    except:
        print('error receving lab result on create_sample')
        raise 

def sample_update_test_result(org_id, from_inventory_id, sample_id, timestamp, batch_in_qa):

    updated_by_user = get_random_user(org_id)

    sample_update_test_result_data = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "sample_update_test_result",
        "inventory_id": sample_id,
        "related_inventory_id": from_inventory_id,
        "to_test_status": "sample-test-result-pass",
        "test_result": "pass",
        "uploaded_by": get_random_user(org_id)["email"],
        "batch_in_qa": batch_in_qa,
    }

    try:
        sample_lab_result_received = SampleUpdateTestResult.do_activity(sample_update_test_result_data, {})
        update_timestamp('activities', sample_lab_result_received['activity_id'], (timestamp+timedelta(days=4)))
        create_signature(
            org_id, sample_lab_result_received['activity_id'], "updated_by", updated_by_user["id"], timestamp)
        result = sample_lab_result_received
    except:
        print('error updating test result on create_sample')
        raise 

def qa_review_result(org_id, sample_id, timestamp):
    reviewed_by_user = get_random_user(org_id)
    qa_review_result_data = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": "batch_qa_review",
        "inventory_id": sample_id,
        "reviewed_by": reviewed_by_user["email"],
        "qa_review_result": "release",
        "to_test_status": "batch-release",
    }

    try:
        result_qa_review_result = BatchQaReview.do_activity(qa_review_result_data, {})
        update_timestamp('activities', result_qa_review_result['activity_id'], (timestamp+timedelta(days=5)))
        create_signature(
            org_id, result_qa_review_result['activity_id'], "reviewed_by", reviewed_by_user["id"], timestamp)
        result = result_qa_review_result
    except:
        print('error receving lab result on create_sample')
        raise 

if __name__ == "__main__":
    org_id = input("Type the organization's ID: ")  

    if (org_id):
        DATABASE.dedicated_connection().begin()
        try:
            create_mothers(org_id)
            DATABASE.dedicated_connection().commit()
        except:
            DATABASE.dedicated_connection().rollback()
