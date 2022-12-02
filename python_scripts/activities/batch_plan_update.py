"""Record batch_plan_update"""
from datetime import datetime
from activities.activity_handler_class import ActivityHandler
from db_functions import update_into_db
# from class_errors import ClientBadRequest


class BatchPlanUpdate(ActivityHandler):
    """Record batch_plan_update"""

    required_args = {'inventory_id', 'plan'}

    @classmethod
    def do_activity(cls, args, current_user):
        """Update the plan for a batch"""

        cls.check_required_args(args)

        update_result = update_into_db(
            "inventories", args['inventory_id'], {"plan": args['plan']}, args.get('timestamp', datetime.now()) )

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": update_result['affected_rows']
        }
