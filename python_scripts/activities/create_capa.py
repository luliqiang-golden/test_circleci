"""
create_capa - create a capa
"""

from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler


class CreateCapa(ActivityHandler):
    """
    Create a capa

    :param capa_id: ID of the capa action 
    :param description: description of the capa
    :param reported_by: staff member who is reporting the capa (the "initiator")

    :returns: An object containing the new capa id and the corresponding activity's id 
    """

    required_args = {
        'description',
        'reported_by',
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

        capas_object = {
            'description': args['description'],
            'reported_by': args['reported_by'],
            'organization_id': args['organization_id'],
            'created_by': args['created_by']
        }
        capa_result = insert_into_db('capas', capas_object)

        args['capa_id'] = capa_result['id']
        activity_result = cls.insert_activity_into_db(args)

        return {
            'activity_id': activity_result['id'],
            'capa_id': capa_result['id']
        }
