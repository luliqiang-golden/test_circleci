"""Endpoints for Deviation Reports"""

from flask_restful import Resource

from resource_functions import get_collection, get_resource


from auth0_authentication import requires_auth


class DeviationReports(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='deviation_reports')

class DeviationReport(Resource):

    # Read single Deviation Report by id
    @requires_auth
    def get(self, current_user, deviation_report_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=deviation_report_id,
            organization_id=organization_id,
            resource='deviation_reports')

class DeviationReportsWithAssignments(Resource):
    
    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='vw_deviation_reports_with_assignments')

class DeviationReportWithAssignments(Resource):

    # Read single record by id
    @requires_auth
    def get(self, current_user, deviation_report_with_assignments_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=deviation_report_with_assignments_id,
            organization_id=organization_id,
            resource='vw_deviation_reports_with_assignments')