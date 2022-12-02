"""Create a mother plant from either a batch or a received inventory"""

from datetime import datetime
from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler


class CreateMother(ActivityHandler):
    """Activity for creating a mother"""

    required_args = {
        'name',
        'variety',
        'variety_id',
        'organization_id',
        'created_by',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a mother plant from either a batch or a received inventory"""

        cls.check_required_args(args)

        name = ''
        if 'inventory_name' in args:
            name = args['inventory_name']
        else:
            name = "{} Mother".format(args['variety'])
            

        inventory_object = {
            "name": name,
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "type": "mother",
            "variety": args["variety"],
            "variety_id": args["variety_id"],
            "timestamp": args["timestamp"] or datetime.datetime.now(),
        }

        inventory_result = insert_into_db('Inventories', inventory_object)

        args["inventory_id"] = inventory_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "inventory_id": inventory_result["id"]
        }
