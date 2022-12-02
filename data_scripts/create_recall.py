# Import libraries from parent folder
from activities.create_recall import CreateRecall
from activities.recall_active import ActiveRecall
from activities.recall_close import CloseRecall
from activities.recall_update_detail import UpdateRecallDetail
from psycopg2 import sql
import psycopg2.extras
import psycopg2
from utilities import select_from_db
from random import getrandbits, randint
from datetime import timedelta
from constants import USER_ID
from db_functions import DATABASE
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')


def create_recalls(org_id):
    try:
        recall_data = get_recall_data(org_id)

        first_recall = recall_data.pop(0)

        create_recall(org_id,  first_recall["description"],
                      [first_recall["lot_id"]], first_recall['timestamp'])

        for x1, x2, x3 in zip(recall_data[::2], recall_data[1::2], recall_data[2::2]):
            choice_random = randint(0, 3)
            if choice_random == 0:
                lot_ids = [x1["lot_id"]]
                create_recall(org_id,  x1["description"],
                              lot_ids, x1['timestamp'])
            elif choice_random == 1:
                lot_ids = x1["lot_id"], x2["lot_id"]
                create_recall(org_id,  x1["description"],
                              lot_ids, x1['timestamp'])
            elif choice_random == 2:
                lot_ids = x1["lot_id"], x2["lot_id"], x3["lot_id"]
                create_recall(org_id,  x1["description"],
                              lot_ids, x1['timestamp'])

    except:
        print('error creating recalls on create_recall ')
        raise


def get_recall_data(org_id):
    params = {'organization_id': org_id}
    query = '''
        select distinct i2.id as lot_id, 
        CONCAT('Recall Lot# ', i2.id, ' Name: ', i2.name, ' for quality issues') as description,
        i.timestamp as timestamp
        from inventories i
		join inventories i2 ON CAST (i.data->>'from_inventory_id' AS INTEGER) = i2.id
        where i.organization_id = %(organization_id)s 
        and i.type = 'lot item' 
        and i.data->>'order_item_id' is not null 
        and i2.type = 'lot'
    '''

    return select_from_db(query, params)


def create_recall(org_id, description, lot_ids, timestamp):

    # Make Recall
    recall_data = {
        "organization_id": org_id,
        "created_by": USER_ID,
        "name": 'create_recall',
        "description": description,
        "lot_ids": lot_ids,
        "contact_user": USER_ID,
    }

    result_recall = CreateRecall.do_activity(recall_data, {})
    print("recall id {} created, from id {}".format(
        result_recall["recall_id"], lot_ids))

    if bool(getrandbits(1)):
        fill_recall_details(org_id, result_recall)

        if bool(getrandbits(1)):
            recall_active_date = timestamp + timedelta(days=15)
            activate_recall(org_id, result_recall, recall_active_date)

            if bool(getrandbits(1)):
                recall_end_date = recall_active_date + timedelta(days=60)
                close_recall(org_id, result_recall, recall_active_date)


def fill_recall_details(org_id, result_recall):
    ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed id lacus congue, congue nisi id, lobortis turpis. Vivamus at lectus nec tortor ornare feugiat et vel mi. Cras at ultrices urna, quis tincidunt nunc. Nulla eu mauris leo. Donec convallis nunc quis mi consequat dictum. Curabitur et maximus elit. Morbi mattis cursus tempus. Nunc vel erat dui. Vivamus ut lectus commodo, blandit mauris quis, venenatis lorem. Etiam a sapien et leo egestas rutrum quis vitae lorem. Aliquam at eros quis lectus elementum tempor ac ut eros. Suspendisse dui lorem, tempus luctus elit ac, condimentum lacinia sapien."

    recall_detail = {
        "recall_strategy": ipsum,
        "risks_evaluation": ipsum,
        "additional_details": ipsum,
        "communication_plan": ipsum
    }

    # Fill in Recall
    recall_update_detail_data = {
        "organization_id": org_id,
        "recall_id": result_recall["recall_id"],
        "recall_detail": recall_detail,
        "name": "recall_update_detail",
        "created_by": USER_ID,
    }

    result_recall_info = UpdateRecallDetail.do_activity(
        recall_update_detail_data, {})
    print("recall id {} detailed info".format(
        result_recall["recall_id"]))


def activate_recall(org_id, result_recall, recall_active_date):
    # Activate Recall
    recall_activate_data = {
        "organization_id": org_id,
        "recall_id": result_recall["recall_id"],
        "plan_time": recall_active_date.strftime("%Y-%m-%d"),
        "name": "recall_active",
        "created_by": USER_ID,
    }

    result_recall_activate = ActiveRecall.do_activity(recall_activate_data, {})
    print("recall id {} activated".format(result_recall["recall_id"]))


def close_recall(org_id, result_recall, recall_end_date):
    # Close Recall
    recall_close_data = {
        "organization_id": org_id,
        "recall_id": result_recall["recall_id"],
        "plan_time": recall_end_date.strftime("%Y-%m-%d"),
        "name": "recall_close",
        "created_by": USER_ID,
    }

    result_recall_close = CloseRecall.do_activity(
        recall_close_data, {})
    print("recall id {} closed".format(
        result_recall["recall_id"]))


if __name__ == "__main__":
    organization_id = input("Type the organization's ID: ")

    if (organization_id):
        DATABASE.dedicated_connection().begin()
        try:
            create_recalls(organization_id)
            DATABASE.dedicated_connection().commit()
        except(psycopg2.Error, psycopg2.Warning,
               psycopg2.ProgrammingError) as error:
            print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
            DATABASE.dedicated_connection().rollback()
