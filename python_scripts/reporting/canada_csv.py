"""generate a csv report for an organization"""
import csv
import json
import os
import sys
import flask

from io import StringIO
from flask_restful import Resource
from app import db
from db_functions import select_resource_from_db, DATABASE, select_from_db
from class_errors import ClientBadRequest
from auth0_authentication import requires_auth
from sqlalchemy import func
import calendar
import datetime

class CanadaCSV(Resource):

    @requires_auth
    def get(self, current_user, organization_id):

        try:
            year = flask.request.args['year']
            month = flask.request.args['month']
        except KeyError:
            raise ClientBadRequest({
                "code": "missing_required_arg",
                "message": "requires both year and month"
            }, 400)

        try:
            assert len(year) == 4
            month = int(month)
            year = int(year)
            assert 1 <= month <= 12
        except (AssertionError, ValueError):
            raise ClientBadRequest({
                "code": "invalid_parameter",
                "message": "Month must be 1 through 12, year must be four digits"
            }, 400)

        reprocessing = True
        report = get_formated_report(organization_id, year, month, current_user['user_id'], reprocessing)
        errors = get_report_erros(report['report_id'])
        csv_file = get_csv_file(report, errors)

        org = select_resource_from_db(resource_id=organization_id,
                                      organization_id=organization_id,
                                      resource='Organizations')

        filename = org['name'] + ' Canada ' + str(month) + '/' + str(year) + '.csv'

        response = flask.make_response(csv_file)
        response.headers.set('content-type', "text/csv")
        response.headers.set('content-disposition',
                             "attachment", filename=filename)
        response.headers.set('x-filename', filename)
        response.headers.set('Access-Control-Expose-Headers', 'x-filename')

        

        return response
    
    def process_report_sqa(month, year, organization_id, created_by):
        return db.session.query(func.public.f_hc_report(month, year, organization_id, created_by)).all()


    def get_report_sqa(month, year, organization_id):
        statement = " SELECT * \
        FROM health_canada_report \
        WHERE organization_id =  '" + str(organization_id) + "' AND \
              report_period_year = '" + year + "' AND \
              report_period_month = '" + month + "'"
        result = db.session.execute(statement)
        return result
    
def get_formated_report(organization_id, year, month, current_user, reprocess = False):

    with open(os.path.join(sys.path[0], "reporting/canada_report_columns.json"), "r") as f:
        report_columns_template = json.load(f)

    year = str(year)
    month = str(month)
    current_user = int(current_user)

   
    report_result = get_report(month, year, organization_id)

    report_id = 0
    if (not report_result or reprocess):
        clear_report(month, year, organization_id)
        report_id = process_report(month, year, organization_id, current_user)
        report_result = get_report(month, year, organization_id)


    value = 0
    for att in report_columns_template.keys():
        try:
            value = report_result[report_columns_template[att]]
            if (not isinstance(value, str)):
                value = round(float(value), 3)

            if ("_closing_inventory" in report_columns_template[att] and "_weight" not in report_columns_template[att]):
                closing_value_prop_name = report_columns_template[att]+"_value"

                # gets the prop name for closing_value
                key_closing_value_prop_name = [x for x in report_columns_template if report_columns_template[x] == closing_value_prop_name][0]
                
                if (value > 0):
                    report_columns_template[key_closing_value_prop_name] = 0.01
                else:
                    report_columns_template[key_closing_value_prop_name] = 0.0

            report_columns_template[att] = value
            
            
        except:
            pass

    
    return {
                "formated_report": report_columns_template,
                "report_id": report_id["report_id"]
           }

def get_csv_file(report, errors):
    output = StringIO()
    csv_writer = csv.writer(output)

    csv_writer.writerow(report["formated_report"].keys())

    csv_writer.writerow(report["formated_report"].values())

    if (errors):
        csv_writer.writerow("")
        csv_writer.writerow(["Errors:"])
        for error in errors:
            csv_writer.writerow([error])

    return output.getvalue()

def get_report(month, year, organization_id):
    params = {'organization_id': organization_id, 'year': year, 'month': month}
    query = '''
        SELECT *
        FROM health_canada_report 
        WHERE organization_id = %(organization_id)s AND
              report_period_year = %(year)s AND
              report_period_month = %(month)s
    '''

    result = select_from_db(query, params)
    if result:
        return result[0]

def clear_report(month, year, organization_id):
    params = {'organization_id': organization_id, 'year': str(year), 'month': str(month)}
    cursor = DATABASE.dedicated_connection().cursor()
    query = '''
        DELETE FROM health_canada_report 
        WHERE organization_id = %(organization_id)s AND
            report_period_year = %(year)s AND
            report_period_month = %(month)s
    '''
    cursor.execute(query, params)

def process_report(month, year, organization_id, created_by):
    cursor = DATABASE.dedicated_connection().cursor()  
    cursor.callproc('f_hc_report', [month, year, organization_id, created_by])
    return cursor.fetchone()

def get_report_erros(report_id):
    cursor = DATABASE.dedicated_connection().cursor()  
    cursor.callproc('f_test_report_result', [report_id])
    return cursor.fetchone()['f_test_report_result']

def get_hcr_breakdown(month, year, organization_id):

    date = datetime.datetime(year,month,1,23,59,59)
    final_date = date.replace(day = calendar.monthrange(year, month)[1]).isoformat()

    report = db.session.execute("""

    				SELECT * FROM (
    				SELECT inv.id, inv.type, latest_quantity, latest_unit, inv.variety, st."data"->>'reportSection' AS report_section
    				FROM f_inventories_latest_stats_stage(:final_date, :org_id) AS inv 
                    INNER JOIN stats_taxonomies AS st ON st.name = inv.latest_unit AND st.organization_id = inv.organization_id
                    WHERE inv.latest_quantity > 0 AND
                    inv.organization_id = :org_id AND
                    TYPE IN ('batch','mother', 'mother batch', 'lot', 'lot item', 'received inventory')
            
                    UNION ALL
                    
					SELECT inv.id, inv.type, latest_quantity, latest_unit, inv.variety, st."data"->>'reportSection' AS report_section
					FROM f_inventories_latest_stats_stage(:final_date, :org_id) as inv
                    INNER JOIN stats_taxonomies as st on st.name = inv.latest_unit and st.organization_id = inv.organization_id
                    INNER JOIN (
                        SELECT 
                            CAST(sample_activity.data->>'inventory_id' AS bigint) AS id,
                            MAX(sample_activity.id) AS act_id
                        FROM activities AS sample_activity
                        WHERE 
                            sample_activity.name in ('create_sample', 'sample_sent_to_lab') 
                            AND TO_CHAR(sample_activity.timestamp,'YYYY-MM-DD') <= :final_date
                        GROUP BY sample_activity.data->>'inventory_id'
                    ) AS latest_activity ON inv.id = latest_activity.id
                    INNER JOIN activities AS act ON act.id = latest_activity.act_id AND act.name='create_sample' 
                    WHERE inv.latest_quantity > 0 AND
                    inv.type ='sample' AND
                    inv.organization_id = :org_id
                    ) AS T1
                    ORDER BY report_section ASC
                        
                                      """, {'org_id': organization_id, 'final_date': final_date})
    
    return report.mappings().all()
