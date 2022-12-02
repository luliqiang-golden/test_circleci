"""
sop_new_version - register the user who upload a new SOP version
"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler

class SopUploadedNewVersion(ActivityHandler):
    """
    Register who uploaded a new version

    :param sop_version_id: ID of the sop version 
    :param uploaded_by: email of logged in user

    :returns: An object containing the the corresponding activity's id 
    """

    required_args = {
        'created_by',
        'sop_id',
        'sop_version_id',
        'organization_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Do the activity

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :param current_user: current user object
        """
        cls.check_required_args(args)

        activity_object = {
            'name': 'sop_uploaded_new_version',
            **args
        }

        activity_result = cls.insert_activity_into_db(activity_object)
        print(activity_result)
        return {
            'activity_id': activity_result['id'],
        }
