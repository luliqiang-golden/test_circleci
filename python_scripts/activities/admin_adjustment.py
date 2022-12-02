"""Activity that allows any fields and thus allows arbitrary changes to inventory and status"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler


class AdminAdjustment(ActivityHandler):
    """Insert an admin adjustment activity"""
    required_args = {'name', 'admin_adjustment_explanation'}

    @classmethod
    def do_activity(cls, args, current_user):
        """Record completion of drying process"""

        # All other activities should use check_required_args from the parent class
        # the admin_adjustment does its own because there are no disallowed args

        if not all(arg in args for arg in cls.required_args):
            raise ClientBadRequest(
                {
                    "code": "missing_required_fields",
                    "description": "Missing one of {}".format(
                        ', '.join(cls.required_args))
                }, 400)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
