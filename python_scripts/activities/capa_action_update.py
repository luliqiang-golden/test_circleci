"""
capa_action_update - update a capa action (arguments must contain at least 1 of the description, comment, staff_assigned. due_date fields)
"""

from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest


class CapaActionUpdate(ActivityHandler):
    """
    Update a capa action (arguments must contain at least 1 of the description, comment, staff_assigned. due_date fields)

    :param capa_action_id: ID of the capa action 
    :param description: description of the action
    :type description: optional
    :param comment: a comment about the action
    :type comment: optional
    :param staff_assigned: the staff member assigned to the action
    :type staff_assigned: optional
    :param due_date: the due date of the action
    :type due_date: optional

    :returns: An object containing the new activity's id, as well as the affected rows of the capa_actions table

    :raises: 400 missing_required_fields
    """

    required_args = {
        'capa_action_id',
    }

    action_fields = {
        'description',
        'comment',
        'staff_assigned',
        'due_date'
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

        # pull all fields from args
        update_fields = [field for field in args.keys() if field in cls.action_fields]

        if not update_fields:
            raise ClientBadRequest(
                {
                    'code': 'missing_required_fields',
                    'description': 'Capa action update must contain one of {}'.format(
                        ', '.join(cls.action_fields))
                }, 400)

        cls.check_required_args(args)

        capa_action_updates = {}
        # copy fields into update object
        # QUESTION: more pythonic and elegant way of doing this???
        for field in update_fields:
            capa_action_updates[field] = args[field]

        update_result = update_into_db('capa_actions', args['capa_action_id'], capa_action_updates)
        activity_result = cls.insert_activity_into_db(args)

        # QUESTION: do i need to return affected rows if its just going to be 1???
        return {
            'activity_id': activity_result['id'],
            'affected_rows': update_result['affected_rows']
        }
