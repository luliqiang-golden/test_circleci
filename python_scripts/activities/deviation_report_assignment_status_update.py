"""Class to handle requests to update a deviation report assignments status"""
import psycopg2.extras

from db_functions import update_into_db, select_from_db
from class_errors import ClientBadRequest, DatabaseError
from activities.activity_handler_class import ActivityHandler
from activities.deviation_report_status_update import DeviationReportUpdateStatus


class DeviationReportUpdateAssignment(ActivityHandler):
    """Action to update a deviation report assignment status"""

    required_args = {
        'organization_id',
        'created_by',
        'deviation_report_assignment_id',
        'to_status'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Update a deviation report assignment status"""

        cls.check_required_args(args)

        _deviation_report_assignment_update_result = update_into_db("deviation_reports_assignments", args["deviation_report_assignment_id"], {
            "status": args["to_status"]
        })

        deviation_report_update_result = cls.update_deviation_report_status(args)

        args["deviation_report_id"] = deviation_report_update_result["deviation_report_id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": _deviation_report_assignment_update_result["affected_rows"],
            "affected_deviaition_report_rows": deviation_report_update_result["affected_rows"]
        }

    @classmethod
    def update_deviation_report_status(cls, assignment_args):
        
        update_assignment_status = assignment_args["to_status"].lower()
        deviation_report = cls.get_deviation_report(assignment_args)
        deviation_status = deviation_report["status"].lower()
        other_deviaition_assignments = cls.get_other_deviation_assignments_of_deviation_report(deviation_report, assignment_args)

        if deviation_status == "archived" or deviation_status == "rejected":
            raise ClientBadRequest(
            {
                "code": "deviation_report_assignment_status_update_error",
                "message": "Deviation report is {}".format(deviation_status)
            }, 500)
        
        if deviation_status == "signed":
            raise ClientBadRequest(
            {
                "code": "deviation_report_assignment_status_update_error",
                "message": "Deviation report is already {} off".format(deviation_status)
            }, 500)

        other_assignments_status_array = []
        if other_deviaition_assignments is not None:
            for assignment in other_deviaition_assignments:
                other_assignments_status_array.append(assignment["status"].lower())

        if update_assignment_status.lower() == "signed":
            if "unsigned" in other_assignments_status_array:
                deviation_status = "partially signed"
            else:
                deviation_status = "signed"
            
        deviation_report_activity = {
            "name": "deviation_report_status_update",
            "organization_id": assignment_args["organization_id"],
            "created_by": assignment_args["created_by"],
            "deviation_report_id": deviation_report["id"],
            "to_status": deviation_status
        }

        update_result = DeviationReportUpdateStatus.do_activity(deviation_report_activity, {})
        update_result['deviation_report_id'] = deviation_report["id"]

        return update_result
    
    @staticmethod
    def get_deviation_report(args):
        params = {"id": args["deviation_report_assignment_id"]}
        try:
            query = '''
                SELECT dr.*
                FROM deviation_reports_assignments AS da
                LEFT JOIN deviation_reports AS dr ON da.deviation_reports_id = dr.id
                WHERE da.id = %(id)s 
            '''
            return select_from_db(query, params)[0]
        except:
            raise DatabaseError(
            {
                "code": "deviation_report_assignment_status_update_error",
                "message": "Deviation report query error"
            }, 500)

    @staticmethod
    def get_other_deviation_assignments_of_deviation_report(deviation_report, assignment):
        params = {
            "dr_id": deviation_report["id"],
            "id": assignment["deviation_report_assignment_id"]
            }
        try:
            query = '''
                SELECT *
                FROM deviation_reports_assignments               
                WHERE deviation_reports_id = %(dr_id)s AND NOT id = %(id)s
            '''
            return select_from_db(query, params)
        except:
            raise DatabaseError(
            {
                "code": "deviation_report_assignment_status_update_error",
                "message": "Deviation report assignments query error"
            }, 500)
