# Import libraries from parent folder
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/python_scripts')

import argparse
from datetime import datetime, timedelta
import psycopg2
import psycopg2.extras
from psycopg2 import sql

from DBUtils.PersistentDB import PersistentDB
from class_errors import DatabaseError
from db_functions import DATABASE
from shared_activities import create_signature

from constants import USER_ID


def prepare_metrics_data(batch_id, metric, days_elapsed):
    """Generates metrics data

    Arguments:
        batch_id {int} -- The batch id to generate metrics data for
        metric {str} -- The metric to generate data for
        days_elapsed {int} -- Indicates number of days elapsed since batch started

    Returns:
        dict -- Dictionary containing generated metrics data
    """

    if metric == 'metrics_collect_height':
        height = days_elapsed * 10
        return {
            'inventory_id': batch_id,
            'collected_by': 'David',
            'height': height
        }

    if metric == 'metrics_collect_branch_count':
        branch_count = (days_elapsed // 10) if (days_elapsed > 10) else 1
        return {
            'inventory_id': batch_id,
            'collected_by': 'David',
            'branch_count': branch_count
        }

    if metric == 'metrics_collect_internodal_space':
        internodal_space = 1
        if 5 < days_elapsed <= 10:
            internodal_space = 2
        elif 10 < days_elapsed <= 20:
            internodal_space = 3
        elif 20 < days_elapsed <= 30:
            internodal_space = 4
        elif days_elapsed > 30:
            internodal_space = 5

        return {
            'inventory_id': batch_id,
            'collected_by': 'David',
            'internodal_space': internodal_space
        }

    if metric == 'metrics_collect_bud_diameter':
        if days_elapsed < 20:
            return {}

        bud_diameter = days_elapsed / 10

        return {
            'inventory_id': batch_id,
            'collected_by': 'David',
            'bud_diameter': bud_diameter
        }

    if metric == 'metrics_collect_bud_density':
        if days_elapsed < 20:
            return {}

        bud_density = days_elapsed // 10

        return {
            'inventory_id': batch_id,
            'collected_by': 'David',
            'bud_density': bud_density
        }

    if metric == 'metrics_collect_bud_moisture':
        if days_elapsed < 20:
            return {}

        bud_moisture = days_elapsed + 0.5

        return {
            'inventory_id': batch_id,
            'collected_by': 'David',
            'bud_moisture': bud_moisture
        }


def insert_metric_into_db(cursor, record):
    """Inserts a metric data entry into the database

    Arguments:
        cursor {DBUtils.SteadyDB.SteadyDBCursor} -- Database cursor instance
        record {dict} -- Dictionary containing metrics data to be inserted into the database

    Raises:
        DatabaseError -- Error is raised if there was a problem inserting a metric into the db
    """

    table = 'activities'
    columns = ', '.join(record.keys())
    values = ', '.join(
        [("%({})s".format(column)) for column in record])

    query = list()

    query.append('INSERT INTO {0} ({1})'.format(table, columns))
    query.append('VALUES ({})'.format(values))
    query.append('RETURNING id')

    query = '\n'.join(query)

    try:
        cursor.execute(query, record)

        lastrowid = cursor.fetchone()['id']

    except (psycopg2.IntegrityError, psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        DATABASE.dedicated_connection().rollback()
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "insert_resource_error",
                "message": "There was an error inserting in the database"
            }, 500)

    DATABASE.dedicated_connection().commit()

    return {'activity_id': lastrowid}


def insert_metrics_into_db(batch_id, start_date, organization_id=1):
    """Insert metrics data into database for testing purposes

    Arguments:
        batch_id {int} -- The batch id to insert metrics for
        start_date {datetime} -- The start date for the specified batch
        organization_id {int} -- Organization id to insert metrics activities for

    Raises:
        DatabaseError -- Error is raised if there was a problem inserting metrics into db
    """

    metrics = [
        'metrics_collect_height',
        'metrics_collect_branch_count',
        'metrics_collect_internodal_space',
        'metrics_collect_bud_diameter',
        'metrics_collect_bud_density',
        'metrics_collect_bud_moisture'
    ]

    record = {
        'name': None,
        'organization_id': organization_id,
        'created_by': USER_ID,
        'timestamp': None,
        'data': None
    }

    # Use timezone info from start_date
    now = datetime.now(tz=start_date.tzinfo)

    cursor = DATABASE.dedicated_connection().cursor()

    for metric in metrics:
        record['name'] = metric

        for days_elapsed in range(50, 71):
            then = start_date + timedelta(days=days_elapsed)
            # Stop inserting metrics when the date exceeds the current date
            if now < then:
                break

            timestamp = then.strftime('%Y-%m-%d %H:%M:%S')

            data = prepare_metrics_data(
                batch_id,
                metric,
                days_elapsed
            )
            if not data:
                continue

            record['timestamp'] = timestamp
            record['data'] = psycopg2.extras.Json(data)

            result = insert_metric_into_db(cursor, record)
            create_signature(organization_id, result['activity_id'], "collected_by", USER_ID, timestamp)

    cursor.close()

    return


def get_start_date(batch_id):
    """Get the start date for the specified batch id

    Arguments:
        batch_id {int} -- Batch id to fetch start date for

    Raises:
        DatabaseError -- Error is raised if there was a problem with fetching 
                         propagate_cuttings or transfer_inventory for the batch

    Returns:
        datetime -- Start date for the batch
    """

    query = [
        sql.SQL('SELECT *'),
        sql.SQL('FROM activities AS A'),
        sql.SQL('WHERE (A.data->>\'to_inventory_id\')::bigint={}'.format(batch_id)),
        sql.SQL('AND (A.name=\'propagate_cuttings\' OR A.name=\'transfer_inventory\')'),
        sql.SQL('LIMIT 1')
    ]

    query = sql.Composed(query)
    query = query.join('\n')

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        DATABASE.dedicated_connection().rollback()
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "join_inventories_activities_error",
                "message": "There was an error querying the database"
            }, 500)

    DATABASE.dedicated_connection().commit()

    cursor.close()

    return results[0]['timestamp'] if results else None


def main():
    """Main function that takes a batch_id as an argument and inserts metrics for that batch"""

    parser = argparse.ArgumentParser(
        description='Generate and insert metrics data into database')
    parser.add_argument(
        '--batch_id',
        type=int,
        help='Batch id to insert metrics data for',
        required=True
    )

    args = parser.parse_args()

    batch_id = args.batch_id
    start_date = get_start_date(batch_id)

    if not start_date:
        print('No propagate_cuttings or transfer_inventory for the specified batch')
        return

    insert_metrics_into_db(batch_id, start_date)


if __name__ == "__main__":
    main()
