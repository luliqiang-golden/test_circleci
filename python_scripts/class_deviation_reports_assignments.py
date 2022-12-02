"""Endpoints for Deviation Reports Assignments"""

from flask_restful import Resource

from resource_functions import get_collection, get_resource


from auth0_authentication import requires_auth


class DeviationReportsAssignments(Resource):

    # Read all article records
    @requires_auth
    def get(self, current_user, organization_id=None):
        return get_collection(
            current_user=current_user,
            organization_id=organization_id,
            resource='deviation_reports_assignments')


class DeviationReportsAssignment(Resource):

    # Read single Deviation Report by id
    @requires_auth
    def get(self, current_user, deviation_report_assignment_id, organization_id=None):
        return get_resource(
            current_user=current_user,
            resource_id=deviation_report_assignment_id,
            organization_id=organization_id,
            resource='deviation_reports_assignments')