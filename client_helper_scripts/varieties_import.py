'''Makes insertion in taxonomies_options table based on given csv file'''
from dotenv import load_dotenv
load_dotenv('.env')  # pylint: disable=C0411
import csv
import sys
import os
import json
import psycopg2
import psycopg2.extras
from psycopg2 import sql

sys.path.append(os.path.join(os.path.dirname(__file__), "../python_scripts"))

from db_functions import select_from_db, get_tables, TABLE_COLUMNS, DATABASE, NO_DATA_COLUMNS_TABLES
from class_errors import DatabaseError
from utils import get_variety_taxonomy_id, check_variety_exists

def insert_into_db(resource, args: dict, taxonomy_id=None):
    ''''''
    plural = resource.lower()
    if plural == 'taxonomy_options' and taxonomy_id is not None:
        args['taxonomy_id'] = taxonomy_id
    get_tables()
    table_columns = TABLE_COLUMNS.get(plural, [])

    # build the database record,
    # pulling out known columns and leaving the rest in the data json blob
    record = {k: args.pop(k) for k in args.keys() & table_columns}
    if plural not in NO_DATA_COLUMNS_TABLES:
        record['data'] = psycopg2.extras.Json(args)

    # this is using list comprehension to format each column heading and then join into one string
    column_list = ', '.join(record.keys())
    column_values = ', '.join(
        [("%({})s".format(column)) for column in record.keys()])
    query = list()
    query.append('INSERT INTO {0} ({1})'.format(plural, column_list))
    query.append('VALUES ({})'.format(column_values))
    if 'id' in TABLE_COLUMNS.get(plural):
        query.append('RETURNING id')
    query = '\n'.join(query)
    cursor = DATABASE.dedicated_connection().cursor()
    try:
        print(query)
        print(record)
        cursor.execute(query, record)
        affected_rows = cursor.rowcount
        if 'id' in TABLE_COLUMNS.get(plural):
            lastrowid = cursor.fetchone()['id']
    except (psycopg2.IntegrityError, psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "insert_resource_error",
                "message": "There was an error inserting in the database"
            }, 500)
    cursor.close()
    DATABASE.dedicated_connection().commit()
    return {'affected_rows': affected_rows, 'id': lastrowid}


print('compiling data....')
with open('./template_client_helper_scripts/varieties import.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    column_index = {}
    for row in csv_reader:
        get_tables()
        if line_count == 0:
            # Getting column indices from the first row of csv file and store into dict
            column_index["strain"] = row.index("strain")
            column_index["variety"] = row.index("variety")
            column_index["organization_id"] = row.index("organization_id")
            print(f'Column names with respective index are as follows : \n {column_index}')
            line_count += 1
        else:
            if not check_variety_exists(row[column_index["variety"]], row[column_index["organization_id"]]):
                post_obj = {
                    'organization_id': row[column_index["organization_id"]],
                    'created_by': 1,
                    'name': row[column_index["variety"]],
                    'strain': row[column_index["strain"]]
                }
                res = insert_into_db('taxonomy_options', post_obj, taxonomy_id=get_variety_taxonomy_id(row[column_index["organization_id"]]))
                print(line_count, res)
            line_count += 1
