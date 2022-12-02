"""
capa_close - close a capa
"""

from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler


class CapaClose(ActivityHandler):
    """
    Close a capa

    :param capa_id: ID of the capa 

    :returns: An object containing the new activity's id, as well as the affected rows of the capas table
    """

    required_args = {
        'capa_id',
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
            'status': 'closed'
        }
        update_result = update_into_db('capas', args['capa_id'], update)
        activity_result = cls.insert_activity_into_db(args)
        
        return {
            'activity_id': activity_result['id'],
            'affected_rows': update_result['affected_rows']
        }
