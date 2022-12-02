"""Activity to update a Consumable class status"""

from activities.activity_handler_class import ActivityHandler
from db_functions import update_into_db


class UpdateStatus(ActivityHandler):
    """Consumable class status update"""

    required_args = {
        'name',
        'to_status',
        'consumable_class_id'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Update Status of Consumable Class"""

        cls.check_required_args(args)

        update_result = update_into_db(
            'consumable_classes', args['consumable_class_id'], {"status": args["to_status"]})

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": update_result['affected_rows']
        }
