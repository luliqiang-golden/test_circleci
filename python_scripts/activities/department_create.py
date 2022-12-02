"""
department_create - create a department
"""

from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler


class DepartmentCreate(ActivityHandler):
    """
    Create a department

    :param department_name: name of the department

    :returns: An object containing the new department id and the corresponding activity's id 
    """

    required_args = {
        'department_name'
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
            'name': args['department_name'],
            'organization_id': args['organization_id'],
            'created_by': args['created_by']
        }
        result = insert_into_db('departments', record)

        args['department_id'] = result['id']
        activity_result = cls.insert_activity_into_db(args)

        return {
            'activity_id': activity_result['id'],
            'department_id': result['id']
        }
