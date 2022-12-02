"""
capa_action_close - close a capa action and set the result. updates the actions_closed field (+1) of the capa which the action belongs to
"""

from db_functions import update_into_db, update_capas_table_action_plan_fields
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest


class CapaActionClose(ActivityHandler):
    """
    Close a capa action and set the result. Updates the actions_closed field (+1) of the capa which the action belongs to

    :param capa_action_id: ID of the capa action
    :param result: Result of the capa action. Should be 'completd', 'completed with exceptions', or 'not completed'

    :returns: An object containing the new activity's id, as well as the affected rows of both the capa_actions and capas tables

    :raises: 400 capa_result_invalid
    """

    required_args = {
        'capa_action_id',
        'result'
    }

    valid_results = {
        'completed',
        'completed with exceptions',
        'not completed'
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

        if args['result'] not in cls.valid_results:
            raise ClientBadRequest(
                {
                    "code": "capa_result_invalid",
                    "description": "Capa action result must be one of {}".format(
                        ', '.join(cls.valid_results))
                }, 400)

        # TODO: make sure action isn't already canceled or closed???
        update_result = update_into_db('capa_actions', args['capa_action_id'], {
            'status': 'closed',
            'result': args['result']
        })
        activity_result = cls.insert_activity_into_db(args)
        capa_update_result = update_capas_table_action_plan_fields(args['capa_action_id'], {
            'actions_closed': +1
        })

        return {
            'activity_id': activity_result['id'],
            'affected_rows': update_result['affected_rows'],
            'capa_affected_rows': capa_update_result['affected_rows']
        }
