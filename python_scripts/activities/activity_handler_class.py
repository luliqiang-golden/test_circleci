"""Parent class for activity handlers implementing shared logic"""

from class_errors import ClientBadRequest
from db_functions import insert_into_db


class ActivityHandler:
    """Parent class for activity handlers"""

    global_disallowed_args = {
        'to_qty',
        'to_qty_unit',
        'to_inventory_id',
        'from_qty',
        'from_qty_unit',
        'from_inventory_id',
        'to_stage',
        'quarantined',
        'to_room',
    }

    required_args = set()

    @classmethod
    def do_activity(cls, args, current_user):
        """Default activity handler. Can be overridden for custom functionality"""
        cls.check_required_args(args)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": activity_result["affected_rows"]
        }

    @classmethod
    def check_required_args(cls, args: dict):
        """Run required args through the disallowed args list"""

        args = set(args or {})

        disallowed_args = cls.global_disallowed_args - cls.required_args

        # if there is an intersection
        if args & disallowed_args:
            raise ClientBadRequest(
                {
                    "code": "sent_disallowed_fields",
                    "description": "Client sent activity with disallowed fields"
                }, 400)

        # if args doesn't have all of required args
        if cls.required_args - args:
            raise ClientBadRequest(
                {
                    "code": "missing_required_fields",
                    "description": "Missing one of {}".format(
                        ', '.join(cls.required_args))
                }, 400)


    @staticmethod
    def insert_activity_into_db(args):
        """Insert an activity into the db"""

        return insert_into_db('Activities', args)
