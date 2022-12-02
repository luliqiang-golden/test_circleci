

from auth0_authentication import requires_auth
import reporting.canada_csv as canada_csv
from controllers import BaseController
from flask import Blueprint, request
from flask.json import jsonify
import pandas as pd
import flask

class ReportsHCRBreakdownCSV(BaseController):
    
    @requires_auth
    def get(self, current_user, organization_id):

        queryparams = request.args

        year = int(queryparams.get('year'))
        month = int(queryparams.get('month'))
        
        report = canada_csv.get_hcr_breakdown(month, year, organization_id)
        
        normal = pd.DataFrame.from_dict(report)
        filename = 'hcr-breakdown-' + str(year) + '-' + str(month) + '.csv'

        response = flask.make_response(normal.to_csv(index=False))
        response.headers.set('content-type', "text/csv")
        response.headers.set('content-disposition',
                                "attachment", filename=filename)
        response.headers.set('x-filename', filename)
        response.headers.set('Access-Control-Expose-Headers', 'x-filename')
        
        return response