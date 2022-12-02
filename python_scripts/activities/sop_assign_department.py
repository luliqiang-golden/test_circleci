"""
sop_assign_department - assign a department to an sop
"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler

class SopAssignDepartment(ActivityHandler):
    """
    Assign department to an Sop

    :param sop_version_id: ID of the sop version 
    :param department_id: ID of the department to assign the sop to

    :returns: An object containing the the corresponding activity's id 
    """

    required_args = {
        'sop_id',
        'version_id',
        'department_id',
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
        record = {
            'sop_id': args['sop_id'],
            'sop_version_id': args['version_id'],
            'department_id': args['department_id'],
            'organization_id': args['organization_id']
        }

        db_object = insert_into_db('sop_versions_departments', record)

        activity_object = {
            'name': 'sop_assign_department',
            'created_by': args['created_by_id'],
            'sop_assign_department_id': db_object['id'],
            **record
        }
        activity_result = cls.insert_activity_into_db(activity_object)

        return {
            'activity_id': activity_result['id'],
            'sop_versions_departments_id': db_object['id']
        }
