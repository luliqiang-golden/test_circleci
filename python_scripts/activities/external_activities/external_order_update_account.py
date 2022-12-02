"""Update external order account"""
from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler


class ExternalOrderUpdateAccount(ActivityHandler):
    """Update external order account"""

    required_args = {
        'name',
        'order_id',
        'to_crm_account_id',
        'to_crm_account_name',
        'to_shipping_address',
        'to_order_placed_by',
        'to_order_received_date',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """update external order account and address"""

        cls.check_required_args(args)

        update_object = {
            'crm_account_id': args['to_crm_account_id'],
            'crm_account_name': args['to_crm_account_name'],
            'shipping_address': args['to_shipping_address'],
            'order_placed_by': args['to_order_placed_by'],
            'order_received_date': args['to_order_received_date'],
            'due_date': args['to_due_date'],
        }
        
        update_result = update_into_db(
            'orders', args['order_id'], update_object)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": update_result["affected_rows"]
        }
