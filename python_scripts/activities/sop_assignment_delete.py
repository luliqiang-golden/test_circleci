"""
sop_assignment_delete - delete an sop assignment
"""

from db_functions import update_single_table_multiple_params
from activities.activity_handler_class import ActivityHandler

class SopAssignmentDelete(ActivityHandler):
    """
    Update a sop description

    :param sop_id: ID of the sop 
    :param status: description of the action

    :returns: An object containing the new activity's id, as well as the affected rows of the sops table
    """

    required_args = {
        'sop_version_id',
        'assigned_by_id',
        'assigned_to_id',
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

        updates = {
            'status': 'disabled'
        }

        params = {
            'assigned_by_id': args['assigned_by_id'],
            'assigned_to_id': args['assigned_to_id'],
            'sop_version_id': args['sop_version_id']
        }

        update_result = update_single_table_multiple_params('sop_assignments', updates, params)
        activity_result = cls.insert_activity_into_db(args)

        return {
            'activity_id': activity_result['id'],
            'affected_rows': update_result['affected_rows']
        }
