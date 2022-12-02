"""Update the enabled status of a user"""
from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler


class UserUpdateEnabled(ActivityHandler):
    """
    Update enabled status of a user

    :param user_id: ID of the user to update
    :param enabled: Is the user enabled or not?
    :type enabled: boolean

    :returns: Object with activity_id, affected_rows
    """

    required_args = {
        'name',
        'user_id',
        'enabled',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Implementation function for user_update_enabled activity"""

        cls.check_required_args(args)

        update_arg = {'enabled': args['enabled']}
        update_result = update_into_db("users", args['user_id'], update_arg)
        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": update_result['affected_rows']
        }
