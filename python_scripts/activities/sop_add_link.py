"""
sop_add_link - add a sop link to a SOP
"""

from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler


class SopAddLink(ActivityHandler):
    """
    Add a sop link to a SOP

    :param sop_id: ID of the SOP

    :returns: An object containing the sop link id and the corresponding activity's id 
    """

    required_args = {
        'sop_id',
        'sop_version_number',
        'link_type',
        'link_id'
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

        sop_link_object = {
            **args,
            'name': 'sop_add_link',
        }

        activity_result = cls.insert_activity_into_db(sop_link_object)

        return {
            'activity_id': activity_result['id']
        }
