"""
sop_assignment_sign - sign an sop assignment
"""
from datetime import datetime

from db_functions import update_single_table_multiple_params
from activities.activity_handler_class import ActivityHandler
from activities.create_signature import CreateSignature

class SopAssignmentSign(ActivityHandler):
    """
    Sign off on an SOP

    :param sop_version_id: ID of the sop version
    :param assigned_by_id: ID of the user who assigned the SOP
    :param assigned_to_id: ID of the user to whom the SOP was assigned to

    :returns: An object containing the new activity's id, as well as the affected rows of the sop_assignments table
    """

    required_args = {
        'sop_id',
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

        # record the signature activity
        signature_response = cls.insert_activity_into_db(args)
        
        updates = {
            'signature_status': 'employee_signed',
            'employee_signed_date': args['signed_date'],
        }

        if 'department_head_id' in args:
            updates = {
            'dept_head_signed_date': args['signed_date'],
            'signature_status': 'dept_head_signed',
            }


        # update the sop assignment record
        params = {
            'assigned_by_id': args['assigned_by_id'],
            'assigned_to_id': args['assigned_to_id'],
            'sop_version_id': args['sop_version_id'],
        }

        update_result = update_single_table_multiple_params('sop_assignments', updates, params)
        
        return {
            'activity_id': signature_response['id'],
            'affected_rows': update_result['affected_rows']
        }
