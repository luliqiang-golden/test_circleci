"""generate a csv report for an organization"""
from datetime import datetime
import pandas as pd

from flask import request

from flask_restful import Resource, abort
import flask

from auth0_authentication import requires_auth

from models.inventory.batch import Batch


class BatchesCSV(Resource):

    @requires_auth
    def get(self, current_user, organization_id):
        request_args = request.args
        available_args = ['id', 'variety', 'plan.end_type', 'attributes:stage', 'attributes:room', 'archive']
        if any(args not in available_args for args in request_args) and len(request_args) > 0:
            abort(400, description = 'available parameters are {}'.format(available_args))
        report = Batch.batches_report(self, organization_id, request_args)
        normal = pd.DataFrame.from_dict(report)
        now = datetime.now().strftime("%Y_%m_%dT%H:%M:%S")
        filename = 'batches-report-' + now + '.csv'

        response = flask.make_response(normal.to_csv(index=False))
        response.headers.set('content-type', "text/csv")
        response.headers.set('content-disposition',
                             "attachment", filename=filename)
        response.headers.set('x-filename', filename)
        response.headers.set('Access-Control-Expose-Headers', 'x-filename')

        return response
