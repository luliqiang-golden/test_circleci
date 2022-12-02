"""
deviation_report_add_link - add a deviation deport link to a Deviation Report
"""

from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler


class DeviationReportAddLink(ActivityHandler):
    """
    Add a deviation report link to a Deviation Report

    :param deviation_report_id: ID of the Deviation Report

    :returns: An object containing the deviation report link id and the corresponding activity's id 
    """

    required_args = {
        'deviation_report_id',
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

        deviation_report_link_object = {
            **args,
            'name': 'deviation_report_add_link',
        }
        activity_result = cls.insert_activity_into_db(deviation_report_link_object)

        return {
            'activity_id': activity_result['id']
        }
