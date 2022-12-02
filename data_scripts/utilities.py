# Import libraries from parent folder
from psycopg2 import sql
import psycopg2.extras
import psycopg2
from collections import defaultdict
from random import randint, sample
from datetime import datetime, timedelta

import argparse
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '/python_scripts')

from db_functions import DATABASE, update_into_db
from class_errors import DatabaseError


def select_from_db(query, params={}):
    cursor = DATABASE.dedicated_connection().cursor()

    try:
        cursor.execute(query, params)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        DATABASE.dedicated_connection().rollback()
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "select_resource_error",
                "message": "There was an error querying the database"
            }, 500)

    result = None
    if results:
        result = results

    cursor.close()

    return result


def get_consumables_by_organization(organization_id):
    params = {'organization_id': organization_id}

    query = '''        SELECT *
        FROM consumable_classes AS a
        WHERE a.organization_id=%(organization_id)s
    '''

    result = select_from_db(query, params)
    if (result):
        return result


def get_consumable_lots_by_organization(organization_id):
    params = {'organization_id': organization_id}

    query = '''        SELECT *
        FROM consumable_lots AS a
        WHERE a.organization_id=%(organization_id)s
    '''

    result = select_from_db(query, params)
    if (result):
        return result


def get_allocation_associated_with_consumable_lot(organization_id, consumable_lot_id):
    params = {'organization_id': organization_id,
              'consumable_lot_id': str(consumable_lot_id)}

    query = '''        SELECT *
        FROM transaction_allocations AS a
        WHERE a.organization_id=%(organization_id)s AND a.data ->> 'consumable_lot_id'=%(consumable_lot_id)s
    '''

    result = select_from_db(query, params)
    if (result):
        return result[0]


def get_consumable_type_from_consumable(organization_id, consumable_id):
    params = {'organization_id': organization_id,
              'consumable_id': consumable_id}

    query = '''        SELECT *
        FROM consumable_classes AS a
        WHERE a.organization_id=%(organization_id)s AND a.id=%(consumable_id)s
    '''

    result = select_from_db(query, params)
    if (result):
        return result[0]


def get_users_by_organization(organization_id):
    params = {'organization_id': organization_id}

    query = '''        SELECT *
        FROM users AS a
        WHERE a.organization_id=%(organization_id)s
    '''

    result = select_from_db(query, params)
    if (result):
        return result


def update_timestamp(table, id, timestamp):

    if isinstance(timestamp, datetime):
        time = timestamp.strftime('%Y-%m-%d')
    else:
        time = timestamp

    cursor = DATABASE.dedicated_connection().cursor()

    params = {"timestamp": time, "id": id}

    try:
        query = "UPDATE {0} SET timestamp =%(timestamp)s WHERE id=%(id)s".format(
            table)
        cursor.execute(query, params)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:

        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_resource_error",
                "message": error.args[0]
            }, 500)

    cursor.close()
    return {'affected_rows': affected_rows}


def update_timestamp(table, id, timestamp):

    if isinstance(timestamp, datetime):
        time = timestamp.strftime('%Y-%m-%d')
    else:
        time = timestamp

    cursor = DATABASE.dedicated_connection().cursor()

    params = {"timestamp": time, "id": id}

    try:
        query = "UPDATE {0} SET timestamp =%(timestamp)s WHERE id=%(id)s".format(
            table)
        cursor.execute(query, params)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:

        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_resource_error",
                "message": error.args[0]
            }, 500)

    cursor.close()
    return {'affected_rows': affected_rows}


def get_random_user(organization_id):
    params = {'organization_id': organization_id}
    query = '''        
        SELECT *
        FROM users
        WHERE organization_id = %(organization_id)s
        ORDER BY random() limit 1
    '''
    return select_from_db(query, params)[0]


def get_random_inventory(organization_id):
    params = {'organization_id': organization_id}
    query = '''        
        SELECT *
        FROM inventories
        WHERE organization_id = %(organization_id)s
        ORDER BY random() limit 1
    '''
    return select_from_db(query, params)[0]

def get_distinct_inventories(organization_id, limit=1):
    params = {'organization_id': organization_id, 'limit': limit}
    query = '''        
        SELECT DISTINCT ON(variety) *
        FROM inventories
        WHERE organization_id = %(organization_id)s
        ORDER BY variety limit %(limit)s
    '''
    return select_from_db(query, params)

def get_random_department(organization_id):
    params = {'organization_id': organization_id}
    query = '''        
        SELECT *
        FROM departments
        WHERE organization_id = %(organization_id)s
        ORDER BY random() limit 1
    '''
    return select_from_db(query, params)[0]


def get_department_by_name(organization_id, name):
    params = {'organization_id': organization_id, 'name': name}
    query = '''        
        SELECT *
        FROM departments
        WHERE organization_id = %(organization_id)s AND name = %(name)s
        limit 1
    '''
    return select_from_db(query, params)[0]


def get_user_by_id(user_id):
    params = {'id': user_id}
    query = '''        
        SELECT *
        FROM users
        WHERE id = %(id)s
        limit 1
    '''
    return select_from_db(query, params)[0]


def get_random_date_after_today(day_begin, day_end, format=None):
    day = randint(day_begin, day_end)
    expiration_date = datetime.now() + timedelta(days=day)
    if not format:
        return expiration_date.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return expiration_date.strftime(format)


def get_random_date_before_today(day_begin, day_end):
    days_from_today = randint(day_begin, day_end)
    expiration_date = datetime.now() - timedelta(days=days_from_today)
    return expiration_date.strftime("%Y-%m-%d %H:%M:%S")


def get_random_room(organization_id, withSpectialRooms=True):
    params = {'organization_id': organization_id,
              'withSpectialRooms': withSpectialRooms}
    query = '''  
        SELECT *
        FROM rooms
        WHERE organization_id = %(organization_id)s   
        AND (name like 'Bay%%' OR %(withSpectialRooms)s = True)
        ORDER BY random() limit 1
    '''
    return select_from_db(query, params)[0]


def get_ramdom_vendor(organization_id):
    params = {'organization_id': organization_id}
    query = '''        
        SELECT *
        FROM crm_accounts AS t
        WHERE t.organization_id=%(organization_id)s
        AND t.account_type = 'supplier'
        ORDER BY random() limit 1
    '''
    return select_from_db(query, params)[0]


def get_varieties():
    return [
        "Sour Diesel",
        "Girl Scout Cookies",
        "OG Kush",
        "White Widow",
        "Jack Herer",
        "Bubba Kush",
        "Purple Haze",
        "Super Silver Haze",
        "LA Confidential",
        "Hindu Kush"
    ]


def get_variety_strains():
    return {
        "Sour Diesel": "Sativa",
        "Girl Scout Cookies": "Hybrid",
        "OG Kush": "Hybrid",
        "White Widow": "Hybrid",
        "Jack Herer": "Sativa",
        "Bubba Kush": "Indica",
        "Purple Haze": "Indica",
        "Super Silver Haze": "Sativa",
        "LA Confidential": "Hybrid",
        "Hindu Kush": "Indica"
    }


def get_ramdon_document_id():
    upload_ids = [300, 301]
    return upload_ids[randint(0, len(upload_ids)-1)]
