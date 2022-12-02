"""
sop_set_status - set the status of an sop
"""

from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest


class SopSetStatus(ActivityHandler):
    """
    Set the status of an sop

    :param sop_id: ID of the sop version 
    
    :returns: An object containing the new activity's id, as well as the affected rows of the sop_versions table

    :raises: 400 missing_required_fields
    """

    required_args = {
        'sop_id',
        'status'
    }

    valid_statuses = {
        'enabled',
        'archived',
        'disabled' # deleted (NOT IMPLEMENTED)
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

        if not args['status'] in cls.valid_statuses:
            raise ClientBadRequest(
                {
                    'code': 'invalid_property',
                    'description': 'Sop status must be one of the following: {}'.format(
                        ', '.join(cls.valid_statuses))
                }, 400)

        update_result = update_into_db('sops', args['sop_id'], {
                'status': args['status']
            })
        activity_result = cls.insert_activity_into_db(args) 

        return {
            'activity_id': activity_result['id'],
            'affected_rows': update_result['affected_rows']
        }
