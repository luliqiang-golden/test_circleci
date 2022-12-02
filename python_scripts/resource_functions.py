"""Resource-related functions"""

import re

from flask import jsonify, request
from flask_restful import abort
from class_errors import ClientBadRequest

from db_functions import select_collection_from_db, select_resource_from_db, select_from_db
from db_functions import insert_into_db, update_into_db, delete_from_db
from db_functions import build_query


FILTER_REGEX = re.compile(
    r'([\w \|\-\:\.]+)(\*=|\^=|!=|=|>=|<=|<|>|@>)([ \S]+)')
ORDER_BY_REGEX = re.compile(r'([\w \-\:]+)\:(ASC|DESC)')


def prep_args(resource, organization_id, current_user):
    """Get arguments from the body of the request (POST, PATCH) and put them in a dict"""

    # Parse response
    args = request.get_json(force=True)

    # Are we filtering specifically by organization?, if so use that instead of posted data
    plural = resource.lower()
    if plural != 'organizations' and organization_id is not None:
        args['organization_id'] = organization_id

    # Fallback if header current user info is not defined, grab from resource
    if 'created_by' not in args:
        args['created_by'] = current_user['user_id']

    return args


def prep_filters():
    """
    Grabs the filters from query params and turns it into a list of tuples
    :returns: [("filter_key", "operator", "filter_value"),]
    """
    filters = []
    raw_filters = request.args.getlist('filter')

    if raw_filters:
        for raw_filter in raw_filters:
            # # remove the time of the datetime
            # if ("timestamp" in raw_filter):
            #     raw_filter = raw_filter[0:21]

            try:
                match = FILTER_REGEX.fullmatch(raw_filter)
                if match:
                    filters.append(match.groups())
                else:
                    raise ClientBadRequest(
                        {
                            "code": "bad_filter",
                            "message": "Malformed filter {}".format(raw_filter)
                        }, 400)
            except re.error:
                raise ClientBadRequest(
                    {
                        "code": "bad_filter",
                        "message": "Malformed filter {}".format(raw_filter)
                    }, 400)

    return filters


def prep_sorts():
    """
    Grabs order_by params from query and turns them into an array of tuples
    :returns: [("sort_key", "sort_direction"),]
    """

    sorts = []
    raw_sorts = request.args.getlist('order_by')
    if raw_sorts:
        for raw_sort in raw_sorts:
            try:
                match = ORDER_BY_REGEX.fullmatch(raw_sort)
                if match:
                    sorts.append(match.groups())
                else:
                    raise ClientBadRequest(
                        {
                            "code": "bad_order_by",
                            "message":
                            "Malformed order_by: {}".format(raw_sort)
                        }, 400)
            except re.error:
                raise ClientBadRequest(
                    {
                        "code": "bad_order_by",
                        "message": "Malformed order_by: {}".format(raw_sort)
                    }, 400)

    return sorts


def get_collection(current_user, organization_id, resource, filters=None, paginate=True, query = None, where = False):
    """Get collection for resource in question"""
    # Get sing / plural collection names; ie Clients / Client

    filters = filters or []
    filters += prep_filters()
    sorts = prep_sorts()
    per_page = request.args.get('per_page', 20, type=int)
    page = request.args.get('page', 1, type=int)

    if (not query):
        results = select_collection_from_db(
            resource,
            organization_id,
            page=page,
            per_page=per_page,
            filters=filters,
            sorts=sorts,
            paginate=paginate
        )  
    else:
        # wrap this query to avoid ambiguous column issue
        query =  """
             select * from (
                {0}
            ) as wrap_table
        """.format(query)
        query, params = build_query(resource=resource, query=query, organization_id=organization_id, filters=filters, sorts=sorts, where=where)
        results = select_from_db(query=query, params=params, paginate=paginate, page=page, per_page=per_page, hehydatre=True)


    if paginate:
        count = results[1]['count']
        data = results[0]
        return jsonify(
            page=page, per_page=per_page, total=count, data=data)
    else:
        return results


def post_new_resource(current_user,
                      organization_id,
                      resource,
                      meta=True,
                      taxonomy_id=None):
    """Insert new resource record, along with meta"""

    args = prep_args(resource, organization_id, current_user)

    db_result = insert_into_db(
        resource, args, meta=meta, taxonomy_id=taxonomy_id)

    # send back the results with the new id
    return jsonify(db_result)


def get_resource(current_user,
                 resource,
                 resource_id,
                 organization_id,
                 meta=True,
                 select: str = None):
    """Get single resource in question by ID"""
    # Get sing / plural collection names; ie Clients / Client

    result = select_resource_from_db(
        resource, resource_id, organization_id, meta=meta, select=select)

    if result:
        return jsonify(result)

    return abort(404)


def post_update_existing_resource(current_user,
                                  resource,
                                  resource_id,
                                  organization_id,
                                  meta=True):
    """Updates existing resource record, along with meta"""
    args = prep_args(resource, organization_id, current_user)

    db_result = update_into_db(resource, resource_id, args, meta=meta)

    return jsonify(db_result)


def delete_resource(current_user, resource, resource_id, organization_id):
    """Delete resource by id"""
    # Get sing / plural collection names; ie Clients / Client

    db_result = delete_from_db(resource, resource_id, organization_id)

    return jsonify(db_result)


def delete_subscription(resource, resource_id, organization_id):
    """Delete resource by id"""

    db_result = delete_from_db(resource, resource_id, organization_id)

    return jsonify(db_result)
