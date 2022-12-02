"""generate a csv report for an organization"""
from datetime import datetime
from flask_restful import Resource
import flask

from db_functions import select_collection_from_db
from resource_functions import prep_sorts, prep_filters

from auth0_authentication import requires_auth

import pandas as pd

class RefActivitiesCSV(Resource):

    @requires_auth
    def get(self, current_user, organization_id):
        
        filters = prep_filters()
        sorts = prep_sorts()

        results = select_collection_from_db(
            resource='activities',
            organization_id=organization_id,
            filters=filters,
            sorts=sorts,
            paginate=False
        )
        
        report_csv = pd.json_normalize(results)
        report_csv = report_csv.reindex(sorted(report_csv.columns), axis=1)
        now = datetime.now().strftime("%Y_%m_%dT%H:%M:%S")
        filename = 'activity-log-report-' + now + '.csv'
        
        response = flask.make_response(report_csv.to_csv(index=False))
        response.headers.set('content-type', "text/csv")
        response.headers.set('content-disposition',
                             "attachment", filename=filename)
        response.headers.set('x-filename', filename)
        response.headers.set('Access-Control-Expose-Headers', 'x-filename')

        return response