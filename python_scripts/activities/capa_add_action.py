"""
capa_add_action - add an action to a capa. Updates the actions_total field (+1) of the capa which the action belongs to
"""

from db_functions import insert_into_db, update_capas_table_action_plan_fields
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest


class CapaAddAction(ActivityHandler):
    """
    Add an action to a capa. Updates the actions_total field (+1) of the capa which the action belongs to

    :param capa_action_id: ID of the capa action 
    :param description: description of the action
    :param comment: a comment about the action
    :type comment: optional
    :param staff_assigned: the staff member assigned to the action
    :type staff_assigned: optional
    :param due_date: the due date of the action
    :type due_date: optional

    :returns: An object containing the new capa action id, the corresponding activity's id, as well as the affected rows of the capas table
    """

    required_args = {
        'capa_id',
        'description'
    }

    optional_args = {
        'staff_assigned',
        'due_date',
        'comment'
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

        capa_action_object = {
            'capa_id': args['capa_id'],
            'description': args['description'],
            'organization_id': args['organization_id'],
            'created_by': args['created_by']
        }

        for optional_arg in [arg for arg in args.keys() if arg in cls.optional_args]:
            capa_action_object[optional_arg] = args[optional_arg]

        capa_action_result = insert_into_db('capa_actions', capa_action_object)
        args['capa_action_id'] = capa_action_result['id']
        activity_result = cls.insert_activity_into_db(args)
        capa_update_result = update_capas_table_action_plan_fields(args["capa_action_id"], {
            'actions_total': +1
        })

        return {
            'capa_action_id': capa_action_result['id'],
            'activity_id': activity_result['id'],
            'capa_affected_rows': capa_update_result['affected_rows']
        }
