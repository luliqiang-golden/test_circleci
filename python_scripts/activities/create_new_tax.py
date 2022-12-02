"""Class to handle requests to create a new record in taxes"""

from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler

class CreateNewTax(ActivityHandler):
    """Action to create a new record in taxes"""

    required_args = {
        'created_by',
        'organization_id',
        'country',
        'province',
        'attributes'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new tax in taxes tables"""

        cls.check_required_args(args)

        __taxes_object = {
            "created_by": args["created_by"],
            "organization_id": args["organization_id"],
            "country": args["country"],
            "province": args["province"],
            "attributes": args["attributes"]
        }

        taxes_result = insert_into_db('taxes', __taxes_object)

        args["taxes_id"] = taxes_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "tax_id": taxes_result["id"]
        }