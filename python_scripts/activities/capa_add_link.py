"""
capa_add_link - add a capa link to a capa
"""

from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest


class CapaAddLink(ActivityHandler):
    """
    Add a capa link to a capa (argument can only have 1 of account_id, inventory_id, or order_id)

    :param capa_id: ID of the capa 
    :param account_id: ID of the account to link
    :type account_id: optional
    :param inventory_id: ID of the inventory to link
    :type inventory_id: optional
    :param order_id: ID of the order to link
    :type order_id: optional

    :returns: An object containing the new capa link id and the corresponding activity's id 

    :raises: 400 capa_link_invalid
    """

    required_args = {
        'capa_id',
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

        capa_link_object = {
            'capa_id': args['capa_id'],
            'link_type': args['link_type'],
            'link_id': args['link_id'],
            'organization_id': args['organization_id'],
            'created_by': args['created_by']
        }

        capa_link_result = insert_into_db('capa_links', capa_link_object)
        args['capa_link_id'] = capa_link_result['id']
        activity_result = cls.insert_activity_into_db(args)

        return {
            'capa_link_id': capa_link_result['id'],
            'activity_id': activity_result['id']
        }
