"""
capa_action_cancel - cancel a capa action. updates the actions_total field (-1) of the capa which the action belongs to
"""

from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler


class CapaActionCancel(ActivityHandler):
    """
    Cancel a capa action. Updates the actions_total field (-1) of the capa which the action belongs to

    :param capa_action_id: ID of the capa action

    :returns: An object containing the new activity's id, as well as the affected rows of both the capa_actions and capas tables
    """

    required_args = {
        'capa_action_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Do the activity

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        cls.check_required_args(args)

        # TODO: make sure action isn't already closed???
        update_result = update_into_db('capa_actions', args['capa_action_id'], {
            'status': 'canceled'
        })
        activity_result = cls.insert_activity_into_db(args)

        return {
            'activity_id': activity_result['id'],
            'affected_rows': update_result['affected_rows'],
        }
