"""Clear the room data for an inventory item"""

from datetime import datetime
from time import timezone
from activities.activity_handler_class import ActivityHandler


class UnsetRoom(ActivityHandler):
    """Clear the room data for an inventory item. Do not submit 'to_room'"""

    required_args = {'inventory_id', 'timestamp'}

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        args['to_room'] = ''
        args['timestamp'] = args['timestamp'] or datetime.now(timezone('UTC'))

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
