import copy
from copy import deepcopy
from datetime import datetime, timezone
from decimal import Decimal
import json
import psycopg2
import psycopg2.extras
from psycopg2 import sql
from DBUtils.PersistentDB import PersistentDB

from class_errors import DatabaseError, ClientBadRequest
from settings import Settings
from taxes.class_tax_factory import TaxFactory
from stats.class_stats import Stats


import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))) + '\\python_scripts\\taxes')

# Parse integers and floats from database as Decimal (for higher precision)
psycopg2.extras.register_default_jsonb(
    globally=True,
    loads=(lambda data: json.loads(data, parse_float=Decimal))
)

DATABASE = PersistentDB(
    psycopg2,
    host=Settings.get_setting('DB_HOST'),
    user=Settings.get_setting('DB_USERNAME'),
    password=Settings.get_setting('DB_PASSWORD'),
    dbname=Settings.get_setting('DB'),
    cursor_factory=psycopg2.extras.RealDictCursor)

NO_DATA_COLUMNS_TABLES = []
TABLE_COLUMNS = {}


def select_from_db(db_query, params={}, code="select_error"):
    """"""
    cursor = DATABASE.dedicated_connection().cursor()

    try:
        cursor.execute(db_query, params)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        DATABASE.dedicated_connection().rollback()
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": code,
                "message": "There was an error querying the database"
            }, 500)

    result = None
    if results:
        result = results

    cursor.close()

    return result



# in this method we need to add calculated fileds, or field that come from a join that we need to filter
def add_calculated_fields():
    TABLE_COLUMNS["audit"].append("related_ids")
    TABLE_COLUMNS["audit"].append("requested_by_name")

    TABLE_COLUMNS["inventories"].append("mother_batch_id")
    TABLE_COLUMNS["inventories"].append("unit")
    TABLE_COLUMNS["inventories"].append("qty")


    TABLE_COLUMNS["invoices"].append("invoice_status")
    TABLE_COLUMNS["orders"].append("invoice_id")

    TABLE_COLUMNS["consumable_classes"].append("current_qty")



# properties not on these lists will be inserted in the data json property
def get_tables():
    select_db_query = """
        SELECT column_name, table_name
            FROM information_schema.columns
        WHERE table_schema = 'public'
            AND column_name != 'data'
        ORDER BY table_name
    """
    values = select_from_db(select_db_query, None)
   
    if not values:
        values = []
    for data_object in values:
        list_obj = None
        try:
            list_obj = TABLE_COLUMNS[data_object['table_name']]
        except:
            TABLE_COLUMNS[data_object['table_name']] = []
            list_obj = TABLE_COLUMNS[data_object['table_name']]

        list_obj.append(data_object['column_name'])

    add_calculated_fields()


    select_db_query = """
        SELECT distinct (table_name) 
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name not in (
            SELECT table_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND column_name = 'data'
        )
    """

    values = select_from_db(select_db_query, None)
    if not values:
        values = []
    for data_object in values:
        NO_DATA_COLUMNS_TABLES.append(data_object["table_name"])



    
    

def comparison_formatter(comparison: str, value: str):
    """
    Translates api comparison operators to SQL comparsion operators
    and format the value as needed
    """

    if not comparison or not value:
        raise ClientBadRequest(
            {
                "code": "bad_filter",
                "message": "A required filter detail was not passed"
            }, 500)

    if comparison == '!=' and value == 'null':
        comparison = 'is not'
    elif comparison == '=' and value == 'null':
        comparison = 'is'
    elif comparison in ['=', '!=', '>=', '<=', '>', '<']:
        # Don't need to do anything if it's just equal
        pass
    elif comparison == '*=':
        comparison = 'ILIKE'
        value = '%{}%'.format(value)
    elif comparison == '^=':
        comparison = '::varchar ILIKE'
        value = '{}%'.format(value)
    elif comparison == '@>':
        comparison = '@>'
        value = '"{}"'.format(value)
    else:
        raise ClientBadRequest(
            {
                "code": "invalid_filter_type",
                "message": "Tried to filter with an unsupported comparison"
            }, 500)

    return comparison, value


def build_collection_filters(filters, plural=None):
    """
    Take a list of filter tuples (key, '=', value)
    and return list of SQL filters, dict of values to escape, and count of meta tables to join
    """
    columns_as_array = [
        "batch",
        "mother",
        "received inventory",
        "rooms",
        "supplies",
        "equipments",
    ]
    applied_filters = []
    escaped_values = {}

    for filt in filters:
        filter_columns = filt[0].split('|')
        try:
            filter_values = filt[2].split('|')
        except AttributeError:  # in case of numbers
            filter_values = [filt[2]]

        filter_parts = []

        for column in filter_columns:

            if (plural in ['inventories', 'orders', 'order_items']
            ) and column.startswith('stats:'):
                filter_array = column.split(':', 2)
                if len(filter_array) == 3:
                    column = sql.SQL(f"stats#>>'{{{filter_array[1]},{filter_array[2]}}}'")
                else:
                    column = sql.SQL(f"stats#>>'{{{filter_array[1]}}}'")
                # column = sql.SQL('stats->>{}').format(
                #     sql.Literal(column.split(':', 1)[1]))
            elif (plural in ['inventories', 'orders', 'order_items']
            ) and column.startswith('ordered_stats:'):
                filter_array = column.split(':', 2)
                if len(filter_array) == 3:
                    column = sql.SQL(f"ordered_stats#>>'{{{filter_array[1]},{filter_array[2]}}}'")
                else:
                    column = sql.SQL(f"ordered_stats#>>'{{{filter_array[1]}}}'")
            elif (plural in ['inventories', 'orders', 'order_items']
            ) and column.startswith('shipped_stats:'):
                filter_array = column.split(':', 2)
                if len(filter_array) == 3:
                    column = sql.SQL(f"shipped_stats#>>'{{{filter_array[1]},{filter_array[2]}}}'")
                else:
                    column = sql.SQL(f"shipped_stats#>>'{{{filter_array[1]}}}'")
            elif (plural in ['inventories', 'skus', 'crm_accounts', 'vw_mother_with_mother_batch_id']
            ) and column.startswith('attributes:'):
                column = sql.SQL('attributes->>{}').format(
                    sql.Literal(column.split(':', 1)[1]))
            elif column not in TABLE_COLUMNS.get(plural, '') and column not in ['name', 'timestamp']:
                if '.' in column:
                    column = '{' + column + '}'
                    column = sql.SQL('data#>>{}').format(
                        sql.Literal(column.replace('.', ',')))
                else:
                    # To query through an array in a json object, the json object must be returned as a jsonb object for @> to work
                    if column in columns_as_array:
                        column = sql.SQL('data->{}').format(sql.Literal(column))
                    # Regular queries need this to be returned as a string
                    else:
                        column = sql.SQL('data->>{}').format(sql.Literal(column))

            else:
                column = sql.Identifier(column)

            for value in filter_values:
                comparison, formatted_value = comparison_formatter(
                    filt[1], value)
                if value == "null":
                    filter_template = sql.SQL("{0} {1} null").format(
                        column, sql.SQL(comparison))

                else:
                    escaped_value_key = "escaped_value_{}".format(
                        len(escaped_values))
                    escaped_values[escaped_value_key] = formatted_value
                    filter_template = sql.SQL("{0} {1} {2}").format(
                        column, sql.SQL(comparison),
                        sql.Placeholder(escaped_value_key))

                filter_parts.append(filter_template)

        filter_whole = sql.SQL("({})").format(
            sql.Composed(filter_parts).join(' OR '))
        applied_filters.append(filter_whole)

    return applied_filters, escaped_values


def build_collection_sorts(sorts, plural):
    directions = {'DESC': ' DESC', 'ASC': ' ASC'}
    sort_parts = []
    for column, direction in sorts:
        if (plural == 'inventories') and column.startswith('stats:'):
            column = sql.SQL('stats->>{}').format(
                sql.Literal(column.split(':', 1)[1]))
        elif column not in TABLE_COLUMNS.get(plural, ''):
            column = sql.SQL('data->>{}').format(sql.Literal(column))
        else:
            column = sql.Identifier(column)
        sort_parts.append(
            sql.Composed([column, sql.SQL(directions[direction])]))

    order_by = sql.Composed(
        [sql.SQL('ORDER BY '),
         sql.Composed(sort_parts).join(', ')])

    return order_by


def rehydrate_resource(resource: dict):
    """Merge data keys back into the object"""

    if 'id' in resource:
        resource['id'] = str(resource['id'])

    data = resource.pop('data', None)

    if data:
        resource = {**data, **resource}

    return resource


def select_collection_from_db(resource: str,
                              organization_id: int,
                              meta=True,
                              page=1,
                              per_page=20,
                              filters=None,
                              sorts=None,
                              paginate=True):
    """
    Select a collection of resources from the database
    meta -- set False to not query for resource_meta. Used when resource doesn't have a meta table
    """
    
    plural = resource.lower()

    query = sql.Composed([
        sql.SQL('SELECT *'),
        sql.SQL('FROM {}').format(sql.Identifier(plural)),
    ])

    query, params = build_query(resource, query, organization_id, filters, sorts, False)

    return select_from_db(query, params, paginate, page, per_page, 'select_collection_error', True)

    

def build_query(resource, query, organization_id, filters=None, sorts=None, where=False):
    if (type(query) is str):
           query = sql.SQL(query)

    filters = filters or []

    sorts = sorts or [('id', 'DESC')]

    plural = resource.lower()

    applied_filters, params = build_collection_filters(filters, plural)

    order_by = build_collection_sorts(sorts, plural)

    if plural != 'organizations' and organization_id is not None:
        applied_filters.append(
            sql.SQL("organization_id = %(organization_id)s"))
        params['organization_id'] = organization_id

    where = sql.SQL('')
    if applied_filters:
        where_clause = ' WHERE ' if where else ' AND '
        where = sql.SQL(where_clause) + sql.Composed(applied_filters).join(' AND ')
    

    query = sql.Composed([
        query,
        where,
        order_by,
    ])

    query = query.join('\n')

    return query, params



def select_from_db(query, params = {}, paginate = False, page = 1, per_page = 20, code = "select_from_db_error", hehydatre = False):

    if paginate:
        if per_page and per_page < 1:
            raise DatabaseError(
                {
                    "code": code,
                    "message": "There must be at least 1 query per page"
                }, 400)

        if page < 1:
            raise DatabaseError({
                "code": code,
                "message": "There must be at least 1 page"
            }, 400)

    
    cursor = DATABASE.dedicated_connection().cursor()
    try:
        if (type(query) is str):
           query = sql.SQL(query)

        if (paginate):
            query_count = sql.SQL("""
                SELECT COUNT(*) FROM (
                    {0}
                ) AS TCOUNT
            """).format(query)

            cursor.execute(query_count, params)
            count = cursor.fetchone()

            offset = (page - 1) * per_page
            
            pagination = sql.SQL(" LIMIT {} OFFSET {}").format(sql.Placeholder('per_page'), sql.Placeholder('offset'))
            if (not params):
                params = {}

            params['per_page'] = per_page
            params['offset'] = offset

            
            query = sql.Composed([
                        query,
                        pagination
                    ])
        

      
        cursor.execute(query, params)
        results = cursor.fetchall()
       
       
        # checks if there is data column 
        if (len(results) > 0 and any(r.get("data") for r in results) and hehydatre):
            result_data = [rehydrate_resource(row) for row in results]
        else:
            result_data = results


        if paginate:
            return result_data, count
        else:
            return result_data
         


    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": code,
                "message": "There was an error querying the database",
                "error": error.args[0]
            }, 500)
    finally:
        cursor.close()

    



def execute_query_into_db(query, params = {}, return_id: bool = False, code = "executing_query_into_db_error", alias = ""):
    """Executes query into database"""
    if (return_id):
        if (not alias):
            query = query + " RETURNING id"
        else:
            query = query + " RETURNING {}.id as id".format(alias)
            

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, params)
        affected_rows = cursor.rowcount

        result = {'affected_rows': affected_rows }
        if (return_id):
            result['id'] =  cursor.fetchone()['id']

        cursor.close()

        return result
                

    except (psycopg2.IntegrityError, psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": code,
                "message": "There was an error {}".format(code),
                "error": error.args[0]
            }, 500)


def select_resource_from_db(resource: str,
                            resource_id: int,
                            organization_id: int,
                            meta=True,
                            select: str = None):
    """Get a standard resource from the DB"""
    plural = resource.lower()
    escaped_values = {}

    query = list()

    if select:
        query.append(select)
    else:
        query.append('SELECT *')
    query.append('FROM {0} t'.format('public.' + plural))
    query.append('WHERE t.id = %(resource_id)s')
    escaped_values["resource_id"] = resource_id

    # Are we filtering specifically by organization?
    # we don't need to do this on the org table itself
    if plural != 'organizations' and organization_id is not None:
        query.append('AND t.organization_id = %(organization_id)s')
        escaped_values["organization_id"] = organization_id

    query = '\n'.join(query)

    cursor = DATABASE.dedicated_connection().cursor()

    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "select_resource_error",
                "message": "There was an error querying the database"
            }, 500)

    result = None
    if results:
        result = rehydrate_resource(results[0])

    cursor.close()

    return result


def insert_into_db(resource, args: dict, meta=True, taxonomy_id=None):
    """Insert resource into database"""
    # Get sing / plural collection names; ie Clients / Client
    plural = resource.lower()

    affected_rows = 0
    lastrowid = None

    org_id = args["organization_id"]

    args = copy.deepcopy(args)

    # TODO remove this and have the taxonomy_options route add taxonomy_id to the args
    if plural == 'taxonomy_options' and taxonomy_id is not None:
        args['taxonomy_id'] = taxonomy_id

    table_columns = TABLE_COLUMNS.get(plural, [])

    # build the database record,
    # pulling out known columns and leaving the rest in the data json blob
    record = {k: args.pop(k) for k in args.keys() & table_columns}

    # for roles
    if 'permissions' in record:
        record['permissions'] = psycopg2.extras.Json(record['permissions'])

    if plural == 'recalls' and 'lot_ids' in record:
        record['lot_ids'] = psycopg2.extras.Json(record['lot_ids'])

    if plural == 'orders' and 'shipping_address' in record:
        record['shipping_address'] = psycopg2.extras.Json(
            record['shipping_address'])

    if plural == 'orders' and 'ordered_stats' in record:
        record['ordered_stats'] = psycopg2.extras.Json(
            record['ordered_stats'])

    if plural == 'orders' and 'shipped_stats' in record:
        record['shipped_stats'] = psycopg2.extras.Json(
            record['shipped_stats'])

    if plural == 'shipments' and 'shipping_address' in record:
        record['shipping_address'] = psycopg2.extras.Json(
            record['shipping_address'])

    if plural == 'crm_accounts' and 'attributes' in record:
        record['attributes'] = psycopg2.extras.Json(
            record['attributes'])

    record = check_jsonb_column_by_resource(plural, 'equipment', 'attributes', record)
    
    # To solve two status values insertion into db 
    status_temp = None
    if 'status' in args:
        status_temp = args.pop('status')

    # for rules
    if 'conditions' in record:
        record['conditions'] = psycopg2.extras.Json(record['conditions'])

    if plural not in NO_DATA_COLUMNS_TABLES:
        record['data'] = psycopg2.extras.Json(args)

    # this is using list comprehension to format each column heading and then join into one string
    column_list = ', '.join(record.keys())
    column_values = ', '.join([("%({})s".format(column)) for column in record.keys()])
    query = list()
    query.append('INSERT INTO {0} ({1})'.format(plural, column_list))

    query.append('VALUES ({})'.format(column_values))

    if 'id' in TABLE_COLUMNS.get(plural):
        query.append('RETURNING id')

    query = '\n'.join(query)
    cursor = DATABASE.dedicated_connection().cursor()
    try:

        cursor.execute(query, record)
        affected_rows = cursor.rowcount

        if 'id' in TABLE_COLUMNS.get(plural):
            lastrowid = cursor.fetchone()['id']
            record['id'] = lastrowid

    except (psycopg2.IntegrityError, psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "insert_resource_error",
                "message": "There was an error inserting in the database"
            }, 500)

    cursor.close()

    # Second part of solution of dual 'status' into tables
    if status_temp:
        args['status'] = status_temp
        
    if plural == "activities":
        do_activity_db_updates(args, record, org_id)

    DATABASE.dedicated_connection().commit()

    return {'affected_rows': affected_rows, 'id': lastrowid}


def bulk_update_column_into_db(resource, organization_id, column, new_value, filters=None):
    """Perform db queries to bulk update column"""

    record = {'new_value': new_value}

    filters = filters or []

    plural = resource.lower()

    applied_filters, escaped_values = build_collection_filters(filters, plural)

    if plural != 'organizations' and organization_id is not None:
        applied_filters.append(
            sql.SQL("organization_id = %(organization_id)s"))
        escaped_values['organization_id'] = organization_id

    where = sql.SQL('')
    if applied_filters:
        where = sql.SQL('WHERE ') + sql.Composed(applied_filters).join(' AND ')

    query = sql.Composed([
        sql.SQL('UPDATE {0}').format(sql.Identifier(plural)),
        sql.SQL("SET {} = %(new_value)s").format(sql.Identifier(column)),
        where
    ])

    query = query.join('\n')

    affected_rows = 0

    values = {
        **record,
        **escaped_values
    }

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, values)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_resource_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return {'affected_rows': affected_rows}

def check_jsonb_column_by_resource(plural, resource, jsonb_column, record):
    if plural == resource and jsonb_column in record:
        record[jsonb_column] = psycopg2.extras.Json(
            record[jsonb_column])

    return record        

def update_into_db(resource, resource_id, args, meta=True):
    """Perform db queries to update resource"""
    # Get sing / plural collection names; ie Clients / Client
    plural = resource.lower()

    table_columns = TABLE_COLUMNS.get(plural, [])

    args = copy.deepcopy(args)

    # remove so we don't put these items in the column list
    args.pop('id', '')
    args.pop('timestamp', '')

    # build the database record,
    # pulling out known columns and leaving the rest in the data json blob
    record = {k: args.pop(k) for k in args.keys() & table_columns}

    if plural not in NO_DATA_COLUMNS_TABLES:
        record['data'] = psycopg2.extras.Json(args)

    # this is using list comprehension to format each column heading and then join into one string
    column_list = ', '.join(
        ["{0} = %({0})s".format(key) for key in record.keys()])

    # set this after generating the column list since we don't want to actually update it

    record['id'] = resource_id

    # for roles
    if 'permissions' in record:
        record['permissions'] = psycopg2.extras.Json(record['permissions'])

    # for rules
    if 'conditions' in record:
        record['conditions'] = psycopg2.extras.Json(record['conditions'])

    if plural == 'orders' and 'shipping_address' in record:
        record['shipping_address'] = psycopg2.extras.Json(
            record['shipping_address'])

    if plural == 'orders' and 'ordered_stats' in record:
        record['ordered_stats'] = psycopg2.extras.Json(
            record['ordered_stats'])

    if plural == 'orders' and 'shipped_stats' in record:
        record['shipped_stats'] = psycopg2.extras.Json(
            record['shipped_stats'])

    if plural == 'shipments' and 'shipping_address' in record:
        record['shipping_address'] = psycopg2.extras.Json(
            record['shipping_address'])

    if plural == 'crm_accounts' and 'attributes' in record:
        record['attributes'] = psycopg2.extras.Json(
            record['attributes'])

    record = check_jsonb_column_by_resource(plural, 'equipment', 'attributes', record)

    query = list()
    query.append('UPDATE {0} SET {1}'.format(plural, column_list))
    if plural == 'sop_versions_departments':
        query.append("WHERE sop_version_id=%(id)s")
    else:
        query.append("WHERE id=%(id)s")
    query = '\n'.join(query)

    affected_rows = 0

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, record)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_resource_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return {'affected_rows': affected_rows}


def delete_from_db(resource, resource_id, organization_id):
    """Perform db queries to delete resource"""
    plural = resource.lower()

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        query = """
            DELETE FROM {0} WHERE id = %(id)s
        """
        query = query.format(plural)

        # Are we filtering specifically by organization?
        if plural != 'organizations' and organization_id is not None:
            query += 'AND organization_id = %(organization_id)s'

        cursor.execute(query, {
            'id': resource_id,
            'organization_id': organization_id
        })

        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "delete_resource_error",
                "message": "There was an error querying the database"
            }, 500)
    cursor.close()

    return {'affected_rows': affected_rows}


def select_rules_from_db(organization_id, activity_name):
    """Used by the rules engine to pull relevant rules"""
    cursor = DATABASE.dedicated_connection().cursor()
    try:
        query = """
            SELECT * FROM rules
            WHERE (organization_id = %s OR organization_id = 0) AND activity = %s
            """

        cursor.execute(query, [organization_id, activity_name])

        rules = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "select_rules_error",
                "message": "There was an error querying the database"
            }, 500)
    cursor.close()

    return rules


def do_activity_db_updates(args: dict, activity, org_id):
    """Run through an activity and process any required object attribute or stat updates"""

    if {'inventory_id', 'to_test_status'}.issubset(args):
        update_resource_attribute_into_db(
            'inventories', args['inventory_id'], 'test_status', args['to_test_status'])

    if {'related_inventory_id', 'to_test_status'}.issubset(args) and args['batch_in_qa'] is True:
        update_resource_attribute_into_db(
            'inventories', args['related_inventory_id'], 'test_status', args['to_test_status'])

    if {'inventory_id', 'to_stage'}.issubset(args):
        update_resource_attribute_into_db(
            'inventories', args['inventory_id'], 'stage', args['to_stage'])

    if {'inventory_id', 'to_room'}.issubset(args):
        update_resource_attribute_into_db(
            'inventories', args['inventory_id'], 'room', args['to_room'])

    if {'inventory_id', 'to_status'}.issubset(args):
        update_resource_attribute_into_db(
            'inventories', args['inventory_id'], 'status', args['to_status'])

    if {'inventory_id', 'quarantined'}.issubset(args):
        update_resource_attribute_into_db(
            'inventories', args['inventory_id'], 'quarantined', args['quarantined'])

    if {'to_inventory_id', 'oil_density'}.issubset(args):
        update_resource_attribute_into_db(
            'inventories', args['to_inventory_id'], 'g/ml-oil', args['oil_density'])

    if {'sku_id', 'to_status'}.issubset(args):
        update_resource_attribute_into_db(
            'skus', args['sku_id'], 'status', args['to_status'])

    if {'sku_id', 'to_gtin_12'}.issubset(args):
        update_resource_attribute_into_db(
            'skus', args['sku_id'], 'gtin_12', args['to_gtin_12'])

    if {'sku_id', 'to_gtin_14'}.issubset(args):
        update_resource_attribute_into_db(
            'skus', args['sku_id'], 'gtin_14', args['to_gtin_14'])

    if {'crm_account_id', 'to_status'}.issubset(args):
        update_resource_attribute_into_db(
            'crm_accounts', args['crm_account_id'], 'status', args['to_status'])

    if {'crm_account_id', 'expiration_date'}.issubset(args):
        update_resource_attribute_into_db(
            'crm_accounts', args['crm_account_id'], 'expiration_date', args['expiration_date'])

    if {'crm_account_id', 'status'}.issubset(args) and not {'order_type'}.issubset(args):
        update_resource_attribute_into_db(
            'crm_accounts', args['crm_account_id'], 'status', args['status'])

    if {'from_inventory_id', 'to_status'}.issubset(args):
        update_resource_attribute_into_db(
            'inventories', args['from_inventory_id'], 'status', args['to_status'])

    if {'crm_account_id', 'to_expiration_date'}.issubset(args):
        update_resource_attribute_into_db(
            'crm_accounts', args['crm_account_id'], 'expiration_date', args['to_expiration_date'])

    if {'from_inventory_id', 'from_qty', 'from_qty_unit'}.issubset(args) and (
            args['from_qty'] and float(args['from_qty']) >= 0.001):
        update_stat_into_db(
            'inventories', 'stats', args['from_inventory_id'], args['from_qty_unit'], args['from_qty'], org_id, activity,
            subtract=True)

    if {'to_inventory_id', 'to_qty', 'to_qty_unit'}.issubset(args) and (
            args['to_qty'] and float(args['to_qty']) >= 0.001):
        update_stat_into_db(
            'inventories', 'stats', args['to_inventory_id'], args['to_qty_unit'], args['to_qty'], org_id, activity)


def update_resource_attribute_into_db(resource, resource_id, attribute, new_value):
    """update attribute on a given resource"""

    record = {"resource_id": resource_id,
              'attribute': attribute, 'new_value': psycopg2.extras.Json(new_value)}

    query = list()
    query.append(
        "UPDATE {0} SET attributes = jsonb_set(coalesce(attributes, '{{}}'), ARRAY[%(attribute)s], %(new_value)s)".format(
            resource
        ))
    query.append("WHERE id=%(resource_id)s")

    query = '\n'.join(query)

    affected_rows = 0

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, record)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:

        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_resource_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return {'affected_rows': affected_rows}


def update_stat_into_db(resource, stats_name, resource_id, unit, change, organization_id, activity=None, subtract=False):
    """update order, order_items and inventory stats"""
    change = float(change)

    if subtract:
        change = change * -1

    stats = Stats.get_instance(organization_id)
    stats_obj = stats.get_stats_object_by_name(unit)

    """
    QUERY EXAMPLE:

        update inventories 
            set stats =
                case 
                    when stats->'g-extract'->>'biomass' is null then 
                    stats || '{"g-extract": {"biomass":10}}'
                else 
                    jsonb_set((stats), array['g-extract','biomass'], ( (cast(stats->'g-extract'->>'biomass' as decimal) + 10)::text::jsonb))  
                end
        where id = 561
    """

    if stats_obj["parent"]:
        query = """
            update {0} 
            set {1} =
                case 
                    when {1}->'{4}'->>'{3}' is null then 
                    {1} || '{{"{4}": {{"{3}":{2}}}}}'
                else 
                    jsonb_set(({1}), array['{4}','{3}'], ((cast({1}->'{4}'->>'{3}' as decimal) + {2})::text::jsonb))  
                end
            where id=%(id)s
        """.format(resource, stats_name, change, stats_obj["name"], stats_obj["parent"])


    else:
        query = """
            update {0} 
            set {1} =
                case 
                    when {1}->>'{3}' is null then 
                    {1} || '{{"{3}":{2}}}'
                else 
                    jsonb_set(({1}), array['{3}'], ( (cast({1}->>'{3}' as decimal) + {2})::text::jsonb))  
                end
            where id=%(id)s
        """.format(resource, stats_name, change, stats_obj["name"])

    # query = '\n'.join(query)


    param = {'id': resource_id }

    affected_rows = 0
    total_amount = 0

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, param)
        affected_rows = cursor.rowcount

        if (resource == 'inventories'):
            inv = select_resource_from_db(resource, resource_id, None)
            serialized_stats = Stats.serialize_stats(inv["stats"])
            if (serialized_stats):
                total_amount = serialized_stats['qty']
                

            activity_object = {
                'name': 'inventory_adjustment',
                'created_by': activity['created_by'],
                'organization_id': activity['organization_id'],
                'inventory_id': resource_id,
                'activity_name': activity['name'],
                'activity_id': activity['id'],
                'invetory_type': inv['type'],
                'quantity': float(total_amount),
                'unit': unit,
                'timestamp': activity.get('timestamp', datetime.utcnow())
            }

            insert_into_db('Activities', activity_object)


    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_resource_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return {'affected_rows': affected_rows}


def update_inventories_attributes_for_shipping_from_db(shipment_id, organization_id, attribute_name, new_value):
    """Update lot item attributes eg. room
        shipment collected for matching order-item: 'in-transit'
        shipment pacakged for matching order-item: any room passed
        shipment delivered for matching order-item: '' to indicate inventory already left facility
        with given shipment_id
    
    """
    new_value = psycopg2.extras.Json(new_value)
    query = '''
        UPDATE inventories SET 
        attributes = jsonb_set(coalesce(attributes, '{}'), ARRAY[%(attribute_name)s], %(new_value)s)
        WHERE id IN
        (
            SELECT I.id 
            FROM order_items O
            JOIN inventories I
            ON (I.data->>\'order_item_id\')::bigint = O.id
            AND I.type = \'lot item\' 
            WHERE O.shipment_id = %(shipment_id)s
            AND I.organization_id = %(organization_id)s
        ) 
    '''
    escaped_values = {
        'organization_id': organization_id,
        'shipment_id': shipment_id,
        'attribute_name': attribute_name,
        'new_value': new_value,
    }

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        affected_rows = cursor.rowcount


    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_inventories_attributes_for_shipping_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return {'affected_rows': affected_rows}


def update_inventories_stats_for_shipping_from_db(args):
    """Update stats of lot item to 0 that has matching order_item_id in data column 
        indicating the inventory already left facility or ready for collection
    """
    query = '''
            SELECT *
            FROM order_items O
            JOIN inventories I
            ON (I.data->>\'order_item_id\')::bigint = O.id
            AND I.type = \'lot item\' 
            WHERE O.shipment_id = %(shipment_id)s
            AND I.organization_id = %(organization_id)s
    '''
    escaped_values = {
        'organization_id': args['organization_id'],
        'shipment_id': args['shipment_id'],
    }
    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        inventories = select_from_db(query, escaped_values)
        for inventory in inventories:
            result = Stats.serialize_stats(inventory['stats'])
            update_stat_into_db('inventories', 'stats', inventory['id'], result['unit'], result['qty'], args["organization_id"], args,
                                subtract=True)

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_inventories_stats_for_shipping_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return {'affected_rows': len(inventories)}




def update_orders_shipping_status_from_db(shipment_id, organization_id, status):
    """Updates shipping_status of order to 'delivered' or 'partially_shipped'
       depending on whether all order-items in order is delivered or not
       Unless all order-item in order is delivered, shipping_status of order will be set to partially-shipped
    """

    query = '''
        UPDATE orders as o
            set shipping_status =  CASE 
                                        WHEN (%(status)s = 'packaged') AND 
                                            (t1.total_items = t1.total_packaged) 
                                        THEN 'packaged'
                                        WHEN (%(status)s = 'packaged') AND 
                                            (t1.total_items > t1.total_packaged)
                                        THEN 'partially_packaged'
                                        WHEN (%(status)s = 'shipped') AND 
                                            (t1.total_items = t1.total_shipped) 
                                        THEN 'shipped'
                                        WHEN (%(status)s = 'shipped') AND 
                                            (t1.total_items > t1.total_shipped) AND
                                            ((o.shipping_status != 'partially_delivered') OR (o.shipping_status IS NULL))
                                        THEN 'partially_shipped'
                                        WHEN (%(status)s = 'delivered') AND 
                                            (t1.total_items = t1.total_delivered)
                                        THEN 'delivered'
                                        WHEN (%(status)s = 'delivered') AND 
                                            (t1.total_items > t1.total_delivered)
                                        THEN 'partially_delivered'
                                        ELSE o.shipping_status
                                    END
                                            
            FROM 
            (
                SELECT
                    o.order_id,
                    count(o.id) total_items,
                    count(o.id) FILTER (WHERE s.status = 'packaged') as total_packaged,
                    count(o.id) FILTER (WHERE s.status = 'shipped') as total_shipped,
                    count(o.id) FILTER (WHERE s.status = 'delivered') as total_delivered
                FROM
                    order_items o
                LEFT JOIN shipments s ON s.id = o.shipment_id
                WHERE 
                o.order_id in
                (
                    SELECT 
                        DISTINCT order_id
                    FROM 
                        order_items
                    WHERE 
                        shipment_id = %(shipment_id)s AND 
                        organization_id = %(organization_id)s
                ) and  o.status = 'approved'
                GROUP BY order_id
            ) t1 
            WHERE t1.order_id = o.id;
    '''
    escaped_values = {
        'organization_id': organization_id,
        'shipment_id': shipment_id,
        'status': status,
    }

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        affected_rows = cursor.rowcount


    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_orders_shipping_status_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()
    return {'affected_rows': affected_rows}


def select_user_active_orgs_and_roles(email):
    """
    Query the database for all orgs and roles for an email address
    returns a dictionary like this:
    {
        email: "email@address.com"
        org_roles: [
            {
                user_id: user.id
                organization: organization-object,
                role: role-object,
            },
        ]
    }
    """

    query = """
        SELECT 
            email,
            jsonb_agg(
                json_build_object(
                    'user_id', users.id,
                    'organization', organizations,
                    'role', json_build_object(
                        'id', '1', 'name', 'Admin', 'organization_id', organizations.id, 'created_by', '1', 'timestamp', now(), 'permissions', %(permissions)s::jsonb
                    )
                )
            ) as org_roles
        FROM users
        LEFT JOIN organizations ON organizations.id = users.organization_id
        WHERE 
            lower(email) = lower(%(email)s)
            AND enabled = true
        GROUP BY email
    """

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        permissions = '[{"object": "activities", "methods": ["GET", "POST", "PATCH"]}, {"object": "alembic_version", "methods": ["GET", "POST", "PATCH"]}, {"object": "audit", "methods": ["GET", "POST", "PATCH"]}, {"object": "audit_detail", "methods": ["GET", "POST", "PATCH"]}, {"object": "capa_actions", "methods": ["GET", "POST", "PATCH"]}, {"object": "capa_links", "methods": ["GET", "POST", "PATCH"]}, {"object": "capas", "methods": ["GET", "POST", "PATCH"]}, {"object": "consumable_classes", "methods": ["GET", "POST", "PATCH"]}, {"object": "consumable_lots", "methods": ["GET", "POST", "PATCH"]}, {"object": "crm_accounts", "methods": ["GET", "POST", "PATCH"]}, {"object": "currencies", "methods": ["GET", "POST", "PATCH"]}, {"object": "departments", "methods": ["GET", "POST", "PATCH"]}, {"object": "deviation_reports", "methods": ["GET", "POST", "PATCH"]}, {"object": "deviation_reports_assignments", "methods": ["GET", "POST", "PATCH"]}, {"object": "equipment", "methods": ["GET", "POST", "PATCH"]}, {"object": "health_canada_report", "methods": ["GET", "POST", "PATCH"]}, {"object": "inventories", "methods": ["GET", "POST", "PATCH"]}, {"object": "invoices", "methods": ["GET", "POST", "PATCH"]}, {"object": "order_items", "methods": ["GET", "POST", "PATCH"]}, {"object": "orders", "methods": ["GET", "POST", "PATCH"]}, {"object": "organizations", "methods": ["GET", "POST", "PATCH"]}, {"object": "recalls", "methods": ["GET", "POST", "PATCH"]}, {"object": "roles", "methods": ["GET", "POST", "PATCH"]}, {"object": "rooms", "methods": ["GET", "POST", "PATCH"]}, {"object": "rules", "methods": ["GET", "POST", "PATCH"]}, {"object": "sensors_data", "methods": ["GET", "POST", "PATCH"]}, {"object": "shipments", "methods": ["GET", "POST", "PATCH"]}, {"object": "signatures", "methods": ["GET", "POST", "PATCH"]}, {"object": "skus", "methods": ["GET", "POST", "PATCH"]}, {"object": "sop_assignments", "methods": ["GET", "POST", "PATCH"]}, {"object": "sops", "methods": ["GET", "POST", "PATCH"]}, {"object": "sop_versions", "methods": ["GET", "POST", "PATCH"]}, {"object": "sop_versions_departments", "methods": ["GET", "POST", "PATCH"]}, {"object": "srfax", "methods": ["GET", "POST", "PATCH"]}, {"object": "stats_taxonomies", "methods": ["GET", "POST", "PATCH"]}, {"object": "taxes", "methods": ["GET", "POST", "PATCH"]}, {"object": "taxonomies", "methods": ["GET", "POST", "PATCH"]}, {"object": "taxonomy_options", "methods": ["GET", "POST", "PATCH"]}, {"object": "transaction_allocations", "methods": ["GET", "POST", "PATCH"]}, {"object": "transactions", "methods": ["GET", "POST", "PATCH"]}, {"object": "uploads", "methods": ["GET", "POST", "PATCH"]}, {"object": "users", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_deviation_reports_with_assignments", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_mother_with_mother_batch_id", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sop_assignments", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sop_logs", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sop_notifications", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sops", "methods": ["GET", "POST", "PATCH"]}, {"object": "vw_sop_versions", "methods": ["GET", "POST", "PATCH"]}, {"object": "webhook_subscriptions", "methods": ["GET", "POST", "PATCH"]}, {"action": "admin_adjustment"}, {"action": "approve_received_inventory"}, {"action": "batch_record_harvest_weight"}, {"action": "complete_destruction"}, {"action": "batch_record_dry_weight"}, {"action": "split_batch"}, {"action": "batch_record_cured_weight"}, {"action": "batch_record_final_yield"}, {"action": "complete_oil_extraction"}, {"action": "create_activity_log"}, {"action": "create_batch"}, {"action": "create_mother_batch"}, {"action": "transfer_mother_plants_to_mother_batch"}, {"action": "transfer_batch_plant_to_mother_batch"}, {"action": "create_mother"}, {"action": "update_mother_status"}, {"action": "create_rule"}, {"action": "destroy_material"}, {"action": "germinate_seeds"}, {"action": "metrics_collect_branch_count"}, {"action": "metrics_collect_bud_density"}, {"action": "metrics_collect_bud_moisture"}, {"action": "metrics_collect_bud_diameter"}, {"action": "metrics_collect_height"}, {"action": "metrics_collect_internodal_space"}, {"action": "metrics_collect_trichome_color"}, {"action": "metrics_record_deficiency"}, {"action": "org_update_license_id"}, {"action": "org_update_theme"}, {"action": "org_update_date_format"}, {"action": "org_update_date_time_format"}, {"action": "org_update_metric_system"}, {"action": "org_update_temperature_scale"}, {"action": "org_update_currency"}, {"action": "org_update_upload_formats"}, {"action": "org_update_enable_signature"}, {"action": "org_update_use_batch_name_column_as_link"}, {"action": "plants_add_pesticide"}, {"action": "plants_add_fertilizer"}, {"action": "plants_add_ipm"}, {"action": "plants_defoliate"}, {"action": "plants_flush"}, {"action": "plants_prune"}, {"action": "propagate_cuttings"}, {"action": "queue_for_destruction"}, {"action": "receive_inventory"}, {"action": "transfer_inventory"}, {"action": "unset_room"}, {"action": "update_room"}, {"action": "update_rule"}, {"action": "update_stage"}, {"action": "update_inventory_name"}, {"action": "sample_sent_to_lab"}, {"action": "create_sample"}, {"action": "batch_visual_inspection"}, {"action": "create_sku"}, {"action": "sku_update_status"}, {"action": "sample_lab_result_received"}, {"action": "create_lot"}, {"action": "create_lot_item"}, {"action": "sample_update_test_result"}, {"action": "batch_qa_review"}, {"action": "create_crm_account"}, {"action": "crm_account_update_status"}, {"action": "crm_account_update"}, {"action": "crm_account_attach_document"}, {"action": "batch_plan_update"}, {"action": "batch_record_crude_oil_weight"}, {"action": "batch_record_distilled_oil_weight"}, {"action": "crm_account_create_note"}, {"action": "create_order"}, {"action": "create_external_order"}, {"action": "update_external_order"}, {"action": "order_add_item"}, {"action": "order_update_account"}, {"action": "order_cancel_item"}, {"action": "order_attach_document"}, {"action": "order_create_note"}, {"action": "order_update_status"}, {"action": "order_payment_status"}, {"action": "create_shipment"}, {"action": "order_item_add_shipment"}, {"action": "order_item_map_to_lot_item"}, {"action": "shipment_update_shipping_address"}, {"action": "shipment_update_tracking_number"}, {"action": "shipment_packaged"}, {"action": "shipment_update_shipped_date"}, {"action": "shipment_shipped"}, {"action": "shipment_delivered"}, {"action": "shipment_update_delivered_date"}, {"action": "create_capa"}, {"action": "capa_update_description"}, {"action": "capa_initiate"}, {"action": "capa_dismiss"}, {"action": "capa_close"}, {"action": "capa_add_note"}, {"action": "capa_add_link"}, {"action": "capa_link_disable"}, {"action": "capa_add_action"}, {"action": "capa_approve_action_plan"}, {"action": "capa_action_update"}, {"action": "capa_action_cancel"}, {"action": "capa_action_close"}, {"action": "receive_consumable_lot"}, {"action": "consumable_class_update_status"}, {"action": "create_consumable_class"}, {"action": "consumable_lot_use_items"}, {"action": "user_create"}, {"action": "user_update_enabled"}, {"action": "user_update_role"}, {"action": "consumable_lot_destroy_items"}, {"action": "consumable_lot_update_status"}, {"action": "record_transaction"}, {"action": "record_transaction_allocation"}, {"action": "create_recall"}, {"action": "recall_close"}, {"action": "recall_update_detail"}, {"action": "recall_active"}, {"action": "update_transaction_total_amount"}, {"action": "consumable_lot_return_items"}, {"action": "create_signature"}, {"action": "sop_assignment_delete"}, {"action": "sop_assignment_sign"}, {"action": "sop_version_update"}, {"action": "sop_assign_department"}, {"action": "sop_assign_user"}, {"action": "sop_uploaded_new_version"}, {"action": "department_create"}, {"action": "sop_set_status"}, {"action": "create_organization"}, {"action": "org_update_facility_details"}, {"action": "received_inventory_return"}, {"action": "salvage_batch"}, {"action": "lot_update_thc"}, {"action": "lot_update_cbd"}, {"action": "order_update"}, {"action": "order_item_update"}, {"action": "sku_update"}, {"action": "create_deviation_report"}, {"action": "deviation_report_create_assignment"}, {"action": "deviation_report_status_update"}, {"action": "deviation_report_assignment_status_update"}, {"action": "deviation_report_attach_document"}, {"action": "deviation_report_create_note"}, {"action": "merge_batch"}, {"action": "merge_lot"}, {"action": "create_sanitation_activity"}, {"action": "send_to_extraction"}, {"action": "batch_record_final_extracted_weight"}, {"action": "batch_add_additive"}, {"action": "external_order_update_status"}, {"action": "external_order_payment_status"}, {"action": "external_order_update_account"}, {"action": "external_order_create_note"}, {"action": "external_order_attach_document"}, {"action": "external_order_add_item"}, {"action": "external_order_item_update"}, {"action": "external_order_cancel_item"}, {"action": "external_order_item_map_to_lot_item"}, {"action": "external_order_item_add_shipment"}, {"action": "create_external_shipment"}, {"action": "external_shipment_packaged"}, {"action": "external_shipment_shipped"}, {"action": "external_shipment_delivered"}, {"action": "external_shipment_update_shipped_date"}, {"action": "external_shipment_update_delivered_date"}, {"action": "external_shipment_update_tracking_number"}, {"action": "external_shipment_update_shipping_address"}, {"action": "create_external_crm_account"}, {"action": "external_crm_account_update"}, {"action": "batch_add_links"}, {"action": "lot_review"}, {"action": "sop_add_link"}, {"action": "deviation_report_add_link"}, {"action": "create_invoice"}, {"action": "send_processor"}, {"action": "receive_processor"}, {"action": "org_update_fallback_tax_value"}, {"action": "update_fallback_tax"}, {"action": "org_update_enable_lot_approval"}]'
        cursor.execute(query, {'permissions': permissions, 'email': email})
        results = cursor.fetchall()
    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "select_user_active_orgs_and_roles_error",
                "message": "There was an error querying the database"
            }, 500)

    result = None
    if results:
        result = rehydrate_resource(results[0])
        result['org_roles'] = [{'user_id': o_r['user_id'], 'organization': rehydrate_resource(o_r['organization']),  'role': rehydrate_resource(o_r['role'])} for o_r in result['org_roles']]

    cursor.close()

    return result


def join_inventories_and_activities_from_db(variety=None, inventory_id=None):
    """Joins inventories and activities tables to find batches with a propagate_cuttings or transfer_inventory activity

    Keyword Arguments:
        variety {str} -- The variety to find analytics activities (default: {None})
        inventory_id {int} -- The inventory/batch id to query for (default: {None})

    Raises:
        DatabaseError -- Raise error if there was an issue with querying the database

    Returns:
        list -- All metrics, propagate_cuttings and transfer_inventory activities for a variety or batch
    """

    query = [
        sql.SQL('SELECT A.*'),
        sql.SQL('FROM inventories AS I'),
        sql.SQL('JOIN activities AS A'),
        sql.SQL('ON I.id=(A.data->>\'to_inventory_id\')::bigint'),
        sql.SQL('WHERE I.type=\'batch\''),
        sql.SQL('AND (A.name=\'propagate_cuttings\' OR A.name=\'transfer_inventory\')'),
    ]

    escaped_values = {}
    if variety:
        condition = sql.SQL('AND I.variety=%(variety)s')
        escaped_values['variety'] = variety
        query.append(condition)
    elif inventory_id:
        condition = sql.SQL(
            'AND (A.data->>\'to_inventory_id\')::bigint=%(inventory_id)s')
        escaped_values['inventory_id'] = inventory_id
        query.append(condition)

    query = sql.Composed(query)
    query = query.join('\n')

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "join_inventories_activities_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    results = [rehydrate_resource(row) for row in results]

    return results


def get_total_plants_from_db(organization_id=None, batch_id=None, variety=None, varieties=None, production_type=None):
    query = '''
        SELECT *
        FROM inventories AS I
        JOIN activities AS A
        ON I.id=(A.data->>\'to_inventory_id\')::bigint
        WHERE I.type=\'batch\'
        AND (A.name=\'propagate_cuttings\' OR A.name=\'transfer_inventory\')
        AND (A.data->>\'to_qty_unit\')=\'plants\'
        AND I.organization_id=%(organization_id)s
    '''

    escaped_values = {'organization_id': organization_id}
    if variety:
        query += '\n AND I.variety=%(variety)s'

        escaped_values['variety'] = variety

    if varieties:
        query += '\n AND I.variety IN %(varieties)s'

        # psycopg uses tuples for WHERE IN clause
        escaped_values['varieties'] = tuple(varieties)

    if batch_id:
        query += '\n AND I.id=%(batch_id)s'

        escaped_values['batch_id'] = batch_id
    else:
        query += '\n AND I.attributes->>\'stage\'=\'qa\''

    if production_type:
        query += '\n AND I.data @> \'{"plan": {"type": "%(production_type)s"} }\''
        escaped_values['production_type'] = production_type

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "get_total_plants_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    results = [rehydrate_resource(row) for row in results]

    return results


def get_total_qty_from_db(organization_id=None, batch_id=None, variety=None, varieties=None, production_type=None):
    query = '''
        SELECT *
        FROM inventories AS I
        JOIN activities AS A
        ON I.id=(A.data->>\'to_inventory_id\')::bigint
        WHERE I.type=\'batch\'
        AND (A.name=\'propagate_cuttings\' OR A.name=\'transfer_inventory\')
        AND I.organization_id=%(organization_id)s
    '''

    escaped_values = {'organization_id': organization_id}
    if variety:
        query += '\n AND I.variety=%(variety)s'

        escaped_values['variety'] = variety

    if varieties:
        query += '\n AND I.variety IN %(varieties)s'

        # psycopg uses tuples for WHERE IN clause
        escaped_values['varieties'] = tuple(varieties)

    if batch_id:
        query += '\n AND I.id=%(batch_id)s'

        escaped_values['batch_id'] = batch_id
    # else:
    #     query += '\n AND I.attributes->>\'stage\'=\'qa\''

    if production_type:
        query += '\n AND I.data @> \'{"plan": {"type": "%(production_type)s"} }\''
        escaped_values['production_type'] = production_type

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "get_total_qty_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    results = [rehydrate_resource(row) for row in results]

    return results


def get_total_units_from_db(organization_id=None, batch_id=None, start_type=None, end_type=None, units_added=None,
                            variety=None, varieties=None, stage=None):
    # change activity names based on the units_added flag
    if units_added:
        query = '''
        SELECT *
        FROM inventories AS I
        JOIN activities AS A
        ON I.id=(A.data->>'to_inventory_id')::bigint
        WHERE I.type=\'batch\'
        AND (A.name=\'propagate_cuttings\' OR A.name=\'transfer_inventory\')
        AND I.organization_id=%(organization_id)s
    '''
    else:
        query = '''
        SELECT *
        FROM inventories AS I
        JOIN activities AS A
        ON I.id=(A.data->>'from_inventory_id')::bigint
        WHERE I.type=\'batch\'
        AND A.name=\'queue_for_destruction\'
        AND I.organization_id=%(organization_id)s
    '''

    escaped_values = {'organization_id': organization_id}
    escaped_values['variety'] = variety
    if variety:
        query += '\n AND I.variety= %(variety)s'
        escaped_values['variety'] = variety

    if varieties:
        query += '\n AND I.variety IN %(varieties)s'
        # psycopg uses tuples for WHERE IN clause
        escaped_values['varieties'] = tuple(varieties)

    if batch_id:
        query += '\n AND I.id=%(batch_id)s'
        escaped_values['batch_id'] = batch_id
    elif variety is None:
        query += '\n AND I.attributes->>\'stage\'=\'qa\''

    if start_type:
        query += '\n AND CAST (I.data #>> \'{"plan","start_type"}\' AS VARCHAR) = %(start_type)s'
        escaped_values['start_type'] = start_type

    if end_type:
        query += '\n AND CAST (I.data #>> \'{"plan","end_type"}\' AS VARCHAR) = %(end_type)s'
        escaped_values['end_type'] = end_type

    if stage:
        query += '\n AND I.attributes->>\'stage\'=%(stage)s'
        escaped_values['stage'] = stage

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "get_total_units_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    results = [rehydrate_resource(row) for row in results]

    return results


def get_final_yield_from_db(organization_id=None, batch_id=None, variety=None, varieties=None, units=None):
    query = '''
        SELECT *
        FROM inventories AS I
        JOIN activities as A
        ON I.id=(A.data->>\'to_inventory_id\')::bigint
        WHERE A.name=\'batch_record_final_yield\'
        AND I.organization_id=%(organization_id)s
    '''

    escaped_values = {'organization_id': organization_id}
    if variety:
        query += '\n AND I.variety=%(variety)s'
        escaped_values['variety'] = variety

    if varieties:
        query += '\n AND I.variety IN %(varieties)s'
        # psycopg uses tuples for WHERE IN clause
        escaped_values['varieties'] = tuple(varieties)

    if batch_id:
        query += '\n AND I.id=%(batch_id)s'
        escaped_values['batch_id'] = batch_id

    if units:
        query += '\n AND A.data->>\'to_qty_unit\'=%(units)s'
        escaped_values['units'] = units

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "get_final_yield_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    results = [rehydrate_resource(row) for row in results]

    return results


def get_all_batches_from_db(organization_id=None):
    query = '''
        SELECT *
        FROM inventories AS I
        WHERE I.type=\'batch\'
        AND I.organization_id=%(organization_id)s
    '''

    escaped_values = {'organization_id': organization_id}

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "get_all_batches_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    results = [rehydrate_resource(row) for row in results]

    return results


def get_latest_yield_from_db(organization_id=None, activity_name=None, batch_id=None, variety=None, varieties=None,
                             units=None, stage=None):
    query = '''
        SELECT A.data->>\'to_qty\' as to_qty, I.timestamp as batch_created, A.timestamp as batch_completed, A.name as name
        FROM inventories AS I
        JOIN activities as A
        ON I.id=(A.data->>\'to_inventory_id\')::bigint
        WHERE A.name=%(activity_name)s
        AND I.organization_id=%(organization_id)s
    '''

    escaped_values = {'organization_id': organization_id}
    escaped_values['activity_name'] = activity_name
    if variety:
        query += '\n AND I.variety=%(variety)s'
        escaped_values['variety'] = variety

    if stage:
        query += '\n AND I.attributes->>\'stage\' IN (%(stage)s, \'qa\')'
        escaped_values['stage'] = stage

    if varieties:
        query += '\n AND I.variety IN %(varieties)s'
        # psycopg uses tuples for WHERE IN clause
        escaped_values['varieties'] = tuple(varieties)

    if batch_id:
        query += '\n AND I.id=%(batch_id)s'
        escaped_values['batch_id'] = batch_id

    if units:
        query += '\n AND A.data->>\'to_qty_unit\'=%(units)s'
        escaped_values['units'] = units

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "get_final_yield_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    results = [rehydrate_resource(row) for row in results]

    return results


def get_incomplete_batches_from_db(organization_id=None, varieties=None):
    query = '''
        SELECT I.id, I.variety, (A.data->>\'to_qty\')::bigint AS to_qty, I.timestamp
        FROM inventories AS I
        JOIN activities as A
        ON I.id=(A.data->>\'to_inventory_id\')::bigint
        WHERE I.type=\'batch\'
        AND (A.name=\'propagate_cuttings\' OR A.name=\'transfer_inventory\')
        AND (A.data->>\'to_qty_unit\')=\'plants\'
        AND I.organization_id=%(organization_id)s
        AND NOT I.attributes->>\'stage\'=\'qa\'
    '''

    escaped_values = {'organization_id': organization_id}

    if varieties:
        condition = '\n AND I.variety IN %(varieties)s'
        # psycopg uses tuples for WHERE IN clause
        escaped_values['varieties'] = tuple(varieties)
        query += condition

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "get_incomplete_batches_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return results


def get_stages_from_db(organization_id=None, batch_id=None, variety=None, production_type=None):
    query = '''
        SELECT *
        FROM inventories AS I
        JOIN activities AS A
        ON I.id=(A.data->>\'inventory_id\')::bigint
        WHERE I.type=\'batch\'
        AND A.name=\'update_stage\'
        AND I.organization_id=%(organization_id)s
    '''

    escaped_values = {'organization_id': organization_id}
    if batch_id:
        query += '\n AND I.id=%(batch_id)s'

        escaped_values['batch_id'] = batch_id

    if variety:
        query += '\n AND I.variety=%(variety)s'

        escaped_values['variety'] = variety

    if production_type:
        query += '\n AND I.data->\'plan\'->>\'type\'=%(production_type)s'

        escaped_values['production_type'] = production_type

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, escaped_values)
        results = cursor.fetchall()

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "get_stages_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    results = [rehydrate_resource(row) for row in results]

    return results


def update_capas_table_action_plan_fields(capa_action_id, updates):
    '''
        e.g
        UPDATE capas
        SET actions_approved = actions_approved + 1, 
            actions_closed = actions_closed + -1
        FROM capa_actions
        WHERE capa_actions.capa_id = capas.id AND capa_actions.id = 5
    '''

    escaped_values = {
        'capa_action_id': capa_action_id,
        **updates
    }

    query_update = sql.SQL('UPDATE {}').format(sql.Identifier('capas'))

    set_statements = []
    for attribute in updates:
        set_statements.append(sql.SQL('{} = {} + {}').format(
            sql.Identifier(attribute),
            sql.Identifier(attribute),
            sql.Placeholder(attribute)
        ))

    query_set = sql.SQL('SET {}').format(
        sql.SQL(', ').join(set_statements)
    )

    query_from = sql.SQL('FROM {}').format(sql.Identifier('capa_actions'))

    query_where = sql.SQL('WHERE {}.{} = {}.{} AND {}.{} = {}').format(
        sql.Identifier('capa_actions'),
        sql.Identifier('capa_id'),
        sql.Identifier('capas'),
        sql.Identifier('id'),
        sql.Identifier('capa_actions'),
        sql.Identifier('id'),
        sql.Placeholder('capa_action_id')
    )

    query_composed = query_update + query_set + query_from + query_where
    query = query_composed.join('\n')

    cursor = DATABASE.dedicated_connection().cursor()

    try:
        cursor.execute(query, escaped_values)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_capas_table_action_plan_fields",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return {'affected_rows': affected_rows}


def clear_table_in_org(organization_id=None, table=None):
    if not organization_id or not table:
        return print("No organization id was given")

    print("Deleting data in {} table".format(table))
    query = '''
        DELETE FROM {0} as t
        WHERE t.organization_id=%(organization_id)s
    '''.format(table)

    escaped_values = {'organization_id': organization_id}
    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()

    try:
        cursor.execute(query, escaped_values)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "clear_table_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return affected_rows


def clear_table(table=None):
    print("Deleting data in {} table".format(table))
    query = '''
        DELETE FROM {0} as t
    '''.format(table)

    query = sql.SQL(query)

    cursor = DATABASE.dedicated_connection().cursor()

    try:
        cursor.execute(query)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "clear_table_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return affected_rows


# builds a list of sql composables which are used often for SET and WHERE clauses
# e.g [some_cold = 1, another_cold = 2, last_col = 3]
def build_sql_composables_equalities_list_from_dict(dct):
    return [
        sql.SQL('{} = {}').format(
            sql.Identifier(key),
            sql.Placeholder(key)
        ) for key in dct.keys()
    ]


def build_sql_composables_for_jsonb(field_name, attribute_fields):
    result = []

    for attr in attribute_fields:
        query = ('attributes = jsonb_set(attributes, ARRAY[{0}], {1})').format(
            sql.Identifier(attr),
            sql.Placeholder(attr)
        )

        result.append(sql.SQL(query))

    return result


def update_data_column_in_sop_assignments(resource, updates, params, record):
    query = list()
    for column_name, value in updates.items():
        new_value = psycopg2.extras.Json(value)
        query.append(
            "UPDATE {0} SET data = jsonb_set(data, ARRAY['{1}'], {2}) WHERE".format(
                resource, column_name, new_value
            ))
    for param_key, param_value in params.items():
        if param_key == 'sop_version_id':
            query.append("{0}={1}".format(param_key, param_value))
        else:
            query.append("{0}={1} AND".format(param_key, param_value))

    query = '\n'.join(query)

    affected_rows = 0

    cursor = DATABASE.dedicated_connection().cursor()
    try:
        cursor.execute(query, record)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_resource_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return {'affected_rows': affected_rows}


# for queries which look like
"""
UPDATE some_table 
SET col_1 = 'a', col_2 = 'b' 
WHERE some_col = 1 AND another_col = 2 AND last_col = 3
"""


def update_single_table_multiple_params(resource, updates, params):
    con = DATABASE.dedicated_connection()
    cursor = con.cursor()

    table_columns = TABLE_COLUMNS.get(resource, [])

    record = {k: updates.pop(k) for k in updates.keys() & table_columns}

    # build the update and where clauses
    query_updates = sql.SQL(', ').join(build_sql_composables_equalities_list_from_dict(record))
    query_where = sql.SQL(' AND ').join(build_sql_composables_equalities_list_from_dict(params))

    ### update data column separately
    if resource not in NO_DATA_COLUMNS_TABLES and \
            ('employee_signed_date' in updates or 'dept_head_signed_date' in updates):
        record['data'] = psycopg2.extras.Json(updates)
        update_data_column_in_sop_assignments(resource, updates, params, record)

    query = sql.SQL('''
        UPDATE {} 
        SET {} 
        WHERE {}'''
                    ).format(
        sql.SQL(resource.lower()),
        query_updates,
        query_where
    )

    params = {
        **record,
        **params
    }

    affected_rows = 0

    try:
        cursor.execute(query, params)
        affected_rows = cursor.rowcount

    except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:
        print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
        raise DatabaseError(
            {
                "code": "update_resource_error",
                "message": "There was an error querying the database"
            }, 500)

    cursor.close()

    return {'affected_rows': affected_rows}


def update_multiple_columns(resource, args, params, attributes_fields=None):
    args = deepcopy(args)

    table_columns = TABLE_COLUMNS.get(resource, [])

    not_updatable_columns = ["id", "organization_id", "timestamp", "created_by"]
    for column in not_updatable_columns:
        try:
            del args[column]
        except:
            pass

    args = {k: args.pop(k) for k in args.keys() & table_columns}

    if (args):
        con = DATABASE.dedicated_connection()
        cursor = con.cursor()

        # build the update and where clauses
        query_updates = sql.SQL(', ').join(build_sql_composables_equalities_list_from_dict(args))
        if (attributes_fields):
            query_updates = sql.SQL(', ').join(build_sql_composables_for_jsonb('attributes', attributes_fields))

        query_where = sql.SQL(' AND ').join(build_sql_composables_equalities_list_from_dict(params))

        query = sql.SQL('''
            UPDATE {}
            SET {} 
            WHERE {}'''
                        ).format(
            sql.SQL(resource.lower()),
            query_updates,
            query_where
        )

        params = {
            **args,
            **params
        }

        affected_rows = 0

        try:

            cursor.execute(query, params)
            affected_rows = cursor.rowcount

            # print(cursor.fetchone()['id'], 'cursor')

        except (psycopg2.Error, psycopg2.Warning,
                psycopg2.ProgrammingError) as error:
            print('SQL: {!r}, errno is {}'.format(error, error.args[0]))
            raise DatabaseError(
                {
                    "code": "update_multiple_columns_error",
                    "message": "There was an error querying the database"
                }, 500)


        finally:
            cursor.close()

        return {'affected_rows': affected_rows}


def update_total_order(order_id, organization_id, include_tax, old_provincial=None):
    order_items = select_collection_from_db(
        resource='order_items',
        organization_id=organization_id,
        filters=[('order_id', '=', order_id), ('status', '!=', 'cancelled')]
    )

    if (order_items):
        order_items = order_items[0]

        total_order_item = sum([item['price'] for item in order_items])
        order = select_resource_from_db('orders', order_id, organization_id)
        tax_name = order['tax_name'] if hasattr(order, 'tax_name') else 'null'

        total_provincial_tax = 0
        if (include_tax):
            total_provincial_tax = sum([item['provincial_tax'] for item in order_items])
            if tax_name == 'fallback':
                if old_provincial != None and (order['provincial_tax'] != total_provincial_tax and old_provincial != total_provincial_tax):
                    total_provincial_tax = order['provincial_tax']
            else:
            # Check if already exist provincial tax to update value when user clicked on fallback tax edit button
                if (order['provincial_tax'] and total_provincial_tax != order['provincial_tax']):
                    total_provincial_tax = order['provincial_tax']

        total = (total_order_item + total_provincial_tax + order["shipping_value"])

        discount = order["discount_percent"] * total / 100

        total = total - discount

        args = {
            "id": order["id"],
            "sub_total": total_order_item,
            "total": total,
            "provincial_tax": total_provincial_tax,
            "discount": discount
        }
        
        update_multiple_columns('orders', args, {"id": order["id"]})


def get_avarage_seed_weight(organization_id=None, batch_id=None):
    '''
        this function is responsable to get the avarage of the seed weight from the received inventory
    '''
    params = {'organization_id': organization_id, 'batch_id': batch_id}
    query = '''
        select 
            ROUND(COALESCE(AVG(T1.seed_weight),0),3) as seed_weight
        from (
            select 
                CAST(inv_received.data->>'seed_weight' as decimal) as seed_weight
            from inventories as inv_batch 
                inner join activities as act on act.name = 'transfer_inventory' and act.data->>'to_inventory_id' = cast(inv_batch.id as varchar) and act.organization_id = inv_batch.organization_id 
                inner join inventories as inv_received on cast(inv_received.id as varchar) = act.data->>'from_inventory_id' and inv_received.organization_id = inv_batch.organization_id
            where inv_batch.type = 'batch'           
                and inv_batch.id = %(batch_id)s
                and inv_batch.organization_id = %(organization_id)s
            group by inv_received.id
        ) as T1
    '''

    result = select_from_db(query, params)
    if (result):
        return float(result[0]['seed_weight'])


def update_batch_seed_weight(inventory_id, seeds_weight):
    return update_resource_attribute_into_db(
        'inventories', inventory_id, 'seeds_weight', seeds_weight)


def update_salvage_batch(inventory_id, salvage_batch_flag):
    return update_resource_attribute_into_db(
        'inventories', inventory_id, 'salvage_batch', salvage_batch_flag)

def update_skus_current_inventory(organization_id, sku_id, quantity):
    '''updates current_inventory in skus'''
    params = {'organization_id': organization_id, 'sku_id': sku_id, 'quantity': quantity}
    query = '''
        UPDATE skus
        SET current_inventory = skus.current_inventory + %(quantity)s
        WHERE skus.id = %(sku_id)s
        AND
        skus.organization_id = %(organization_id)s
    '''
    return execute_query_into_db(query, params)

def get_sku_detail(organization_id, sku_id):
        '''Returns sku detail by order_item_id'''
        params = {'organization_id': organization_id, 'sku_id': sku_id}
        query = '''
            select  s.id as sku_id, s.id as id, s.name, s.current_inventory, s.price, s.variety, s.data->>'external_sku_id' as external_sku_id, s.data->>'external_sku_variant_id' as external_sku_variant_id from skus as s where s.organization_id=%(organization_id)s and s.id = %(sku_id)s '''
        result = select_from_db(query, params)
        if (result):            
            return result[0]


def get_sku_by_order_item(org_id, order_item_id):
    """
        Get the sku id and reserverd quantity by order item id        
        :org_id: organization id
        :param order_item_id: order item it
    """
    params = { 'org_id': org_id, 'order_item_id': order_item_id }
    
    query = '''
        select  s.id as sku_id, s.id as id,  s.name, s.current_inventory, s.price,
                cast(coalesce(s.attributes->>'reserved','0') as integer) as reserved_quantity,
                s.data->>'external_sku_id' as external_sku_id,
                s.data->>'external_sku_variant_id' as external_sku_variant_id
        from skus as s 
        inner join order_items as o on o.sku_id = s.id
        where s.organization_id=%(org_id)s 
        and o.id = %(order_item_id)s  
        '''
    result = select_from_db(query, params)
    if (result):            
        return result[0]
