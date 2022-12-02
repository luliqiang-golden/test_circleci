"""
sop_assign_user - assign a user to an sop
"""

from db_functions import insert_into_db, update_single_table_multiple_params
from activities.activity_handler_class import ActivityHandler

class SopAssignUser(ActivityHandler):
    """
    Assign user to an Sop

    :param sop_version_id: ID of the sop version 
    :param assigned_by_id: ID of the user who assigned the sop
    :param assigned_to_id: ID of the user who the sop is assigned to

    :returns: An object containing the the corresponding activity's id 
    """

    required_args = {
        'sop_id',
        'version_id',
        'assigned_to_id'
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

        current_user_id = args.get('assigned_by_id') or current_user.get('user_id')
        record = {
            'sop_id': args['sop_id'],
            'sop_version_id': args['version_id'],
            'assigned_by_id': current_user_id,
            'assigned_to_id': args['assigned_to_id'],
            'organization_id': args['organization_id']
        }
        sop_assignments_result = {}
        try:
            sop_assignments_result = insert_into_db('sop_assignments', record)
        except:
            updates = {
                'status': 'enabled'
            }   
            update_result = update_single_table_multiple_params('sop_assignments', updates, record)

        activity_object = {
            "name": "sop_assign_user",
            "created_by": current_user_id,
            **record
        }
        activity_result = cls.insert_activity_into_db(activity_object)

        if sop_assignments_result != {}:

            return {
                'activity_id': activity_result['id'],
                'sop_assignments_id': sop_assignments_result['id']
            }

        else:
            return {
                'activity_id': activity_result['id']
            }
