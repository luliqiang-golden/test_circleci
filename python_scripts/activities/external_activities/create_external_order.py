"""Create Order"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler
from taxes.class_tax_base import TaxBase


class CreateExternalOrder(ActivityHandler):
    """
    Action to create an order
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
        'crm_account_id',
        'crm_account_name',
        'shipping_address',
        'order_placed_by',
        'order_received_date',
        'order_type',
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

        orders_object = {
            'status' : 'awaiting_approval',
            'organization_id': args['organization_id'],
            'created_by': args['created_by'],
            'crm_account_id': args['crm_account_id'],
            'crm_account_name': args['crm_account_name'],
            'shipping_address': args['shipping_address'],
            'order_placed_by': args['order_placed_by'],
            'order_received_date': args['order_received_date'],
            'order_type': args['order_type'],
            'shipping_status': 'pending'
        }

        if 'due_date' in args:
            orders_object['due_date'] = args['due_date']

        if 'external_order_id' in args:
            orders_object['external_order_id'] = args['external_order_id']

        tax_name = cls.get_tax_name(args['shipping_address']["country"], args['shipping_address']["province"])
        if (tax_name):
            orders_object["tax_name"] = tax_name
        
        order_result = insert_into_db('Orders', orders_object)

        args['order_id'] = order_result['id']

        activity_result = cls.insert_activity_into_db(args)

        return {
            'activity_id': activity_result['id'],
            'order_id': order_result['id']
        }


    def get_tax_name(country, province):
        tax = TaxBase.get_tax(country, province)
        if (tax):
            try:
                return tax["attributes"]["tax_name"]
            except:
                pass