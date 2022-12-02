from datetime import datetime
from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler


class UpdateRecallDetail(ActivityHandler):
    """
    update recall's detail input by user
    :recall_id: ID of the reacll need to be actived
    :recall_detail: the recall detail
    :returns: An object containing the new activity's id, as well as the affected rows of the capas table
    """
    required_args = {
        'recall_id',
        'recall_detail',
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

        update = {
            'data': args['recall_detail']
        }
        update_result = update_into_db('recalls', args['recall_id'], update)
        activity_result = cls.insert_activity_into_db(args)

        return {
            'activity_id': activity_result['id'],
            'affected_rows': update_result['affected_rows']
        }
