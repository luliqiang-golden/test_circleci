"""Activity to update a Consumable Lot status"""

from activities.activity_handler_class import ActivityHandler
from db_functions import update_into_db


class UpdateStatus(ActivityHandler):
    """
    Action to update a consumable lot
    :param consumable_lot_id: The existing consumable lot id
    :param to_status: New state of the consumable lot 
    """

    required_args = {
        'to_status',
        'consumable_lot_id'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Update Status of Consumable Lot
        :param cls: this classs
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        cls.check_required_args(args)

        update_result = update_into_db(
            'consumable_lots', args['consumable_lot_id'], {"status": args["to_status"]})

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": update_result['affected_rows']
        }
