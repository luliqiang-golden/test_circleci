"""
capa_link_disable - disable a capa link
"""

from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler


class CapaLinkDisable(ActivityHandler):
    """
    Disable a capa link

    :param capa_link_id: ID of the capa link
 
    :returns: An object containing the new activity's id, as well as the affected rows of the capa_links table
    """

    required_args = {
        'capa_link_id',
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
            'status': 'disabled'
        }
        update_result = update_into_db('capa_links', args['capa_link_id'], update)
        activity_result = cls.insert_activity_into_db(args)

        return {
            'activity_id': activity_result['id'],
            'affected_rows': update_result['affected_rows']
        }
