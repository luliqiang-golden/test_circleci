"""Class to handle requests to create a batch that will receive inventory"""
from datetime import datetime

from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler


class CreateBatch(ActivityHandler):
    """Action to create a batch"""

    required_args = {
        'variety',
        'variety_id',
        'name',
        'organization_id',
        'created_by',
        'timestamp',
    }
    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new batch inventory item"""

        cls.check_required_args(args)

        inventory_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "type": "batch",
            "variety": args["variety"],
            "variety_id": args["variety_id"],
            "name": CreateBatch.get_inventory_name(args),
            "timestamp": args.get("timestamp", datetime.now()),
        }
        if "merged_inventories" in args:
            inventory_object["merged_inventories"] = args["merged_inventories"]
        inventory_result = insert_into_db('Inventories', inventory_object)

        args["inventory_id"] = inventory_result["id"]
        args["to_test_status"] = ""

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "inventory_id": inventory_result["id"],
            "timestamp": args.get("timestamp", datetime.now()),
        }
    @classmethod
    def get_inventory_name(cls, args):
        """When custom_name property has a value then this value will be used to name the inventory
        Otherwise, the inventory will be named as it always was, using the variety name, current month and current year
        """
        if ("custom_name" in args and args["custom_name"]):
            return args["custom_name"]
        else:
            return "{0}-{1}-{2}".format(
                args["variety"],
                datetime.now().isocalendar()[1],
                datetime.now().year % 100,
            )
