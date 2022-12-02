"""generate a csv report for an organization"""
from datetime import datetime
from decimal import Decimal
from io import StringIO
import csv
from dateutil.relativedelta import relativedelta

from flask_restful import Resource
from flask import request
import flask

from db_functions import select_resource_from_db, select_collection_from_db, DATABASE
from class_errors import ClientBadRequest
from resource_functions import prep_args, get_collection, get_resource, prep_sorts, prep_filters
import json

from auth0_authentication import requires_auth


class InventoryCSV(Resource):

    @requires_auth
    def get(self, current_user, organization_id):
        filters = prep_filters()
        sorts = prep_sorts()

        results = select_collection_from_db(
            resource='inventories',
            organization_id=organization_id,
            filters=filters,
            sorts=sorts,
            paginate=False
        )

        columns = list()

        for row in results:
            test = flatten_json(row)
            test = test.keys()
            columns.extend(test)

        columns = list(set(columns))
        columns.sort()

        output = StringIO()
        csv_writer = csv.writer(output)

        csv_writer.writerow(columns)

        for row in results:
            csv_writer.writerow(map(lambda x: flatten_json(row).get(x, ""), columns))

        csv_file = output.getvalue()

        org = select_resource_from_db(resource_id=organization_id,
                                      organization_id=organization_id,
                                      resource='Organizations')

        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        filename = org['name'] + ' Inventories ' + now + '.csv'
        response = flask.make_response(csv_file)
        response.headers.set('content-type', "text/csv")
        response.headers.set('content-disposition',
                             "attachment", filename=filename)
        response.headers.set('x-filename', filename)
        response.headers.set('Access-Control-Expose-Headers', 'x-filename')

        return response


def flatten_json(y):
    out = {}

    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out
