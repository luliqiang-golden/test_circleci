from datetime import datetime
from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler


class CloseRecall(ActivityHandler):
    """
    close a recall
    :recall_id: ID of the reacll need to be closed
    :close_date: the date plan to close the recall
    :returns: An object containing the new activity's id, as well as the affected rows of the capas table
    """
    required_args = {
        'recall_id',
        'plan_time',
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

        timestamp = datetime.strptime(args['plan_time'], '%Y-%m-%d')
        update = {
            'end_date': timestamp
        }
        update_result = update_into_db('recalls', args['recall_id'], update)
        activity_result = cls.insert_activity_into_db(args)

        return {
            'activity_id': activity_result['id'],
            'affected_rows': update_result['affected_rows']
        }
