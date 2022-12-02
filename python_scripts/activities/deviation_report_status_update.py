"""Class to handle requests to update a deviation report status"""
import psycopg2.extras

from db_functions import update_into_db
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler


class DeviationReportUpdateStatus(ActivityHandler):
    """Action to update a deviation report status"""

    required_args = {
        'organization_id',
        'created_by',
        'deviation_report_id',
        'to_status'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Update a deviation report status"""

        cls.check_required_args(args)

        deviation_report_update_result = update_into_db('deviation_reports', args["deviation_report_id"], {
            "status": args["to_status"]
        })

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": deviation_report_update_result["affected_rows"]
        }