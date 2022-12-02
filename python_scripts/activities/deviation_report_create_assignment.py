"""Class to handle requests to create a deviation report assignments"""
import psycopg2.extras

from db_functions import insert_into_db
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler


class DeviationReportCreateAssignment(ActivityHandler):
    """Action to create a deviation report assignment"""

    required_args = {
        'organization_id',
        'created_by',
        'deviation_report_id',
        'user_id',
        'type'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new deviation report assignment"""

        cls.check_required_args(args)

        _deviation_report_assignment_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "deviation_reports_id": args["deviation_report_id"],
            "type": args["type"],
            "user_id": args["user_id"],
            "status": "unsigned"
        }
        args["to_status"] = "unsigned"

        _deviation_report_assignment_result = insert_into_db('deviation_reports_assignments', _deviation_report_assignment_object)

        args["deviation_report_assignment_id"] = _deviation_report_assignment_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "deviation_report_assignment_id": _deviation_report_assignment_result["id"]
        }
