"""Class to handle requests to update a fallback in taxes"""

from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler

class UpdateFallbackTax(ActivityHandler):
    """Action to update a record in taxes"""

    required_args = {
        'taxes_id',
        'attributes'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Update a fallback tax in taxes tables"""

        cls.check_required_args(args)

        update_result = update_into_db(
            "taxes", args['taxes_id'], {"attributes": args['attributes']})

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": update_result['affected_rows']
        }