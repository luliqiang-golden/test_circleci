"""Create Order"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler


class WebhookSubscribe(ActivityHandler):
    """
    Action to create subscribe entry
    :param crm_account_id: The existing CRM account id
    :param crm_account_name: The existing CRM account name
    :param shipping_address: Shipping address from CRM account
    :param order_placed_by: name of the person order placed
    :type order_paced_by: String

    :param order_received_by: Person order was received by
    :type order_received_by: Integer

    :param order_type: Type of the order

    :returns: An object containing the new activity's id and the new order's id
    """

    required_args = {
        'name',
        'event',
        'url'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new order

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        cls.check_required_args(args)

        subscribe_object = {
            'organization_id': args['organization_id'],
            'created_by': args['created_by'],
            'event': args['event'],
            'url': args['url'],
            'name': args['name']
        }

        subscribe_result = insert_into_db('webhook_subscriptions', subscribe_object, None)

        args['webhook_id'] = subscribe_result['id']

        activity_result = cls.insert_activity_into_db(args)

        return {
            'webhook_id': subscribe_result['id']
        }
