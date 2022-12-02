"""Create Invoice"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler
from class_external_webhooks import firing_webhooks


class CreateInvoice(ActivityHandler):
    """
    Action to create an invoice
    :param order_id: The existing order id
    :param timestamp: The invoice date

    :returns: An object containing the new activity's id and the new invoice's id
    """

    required_args = {
      'order_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new invoice

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        cls.check_required_args(args)

        invoices_payload = {
            'order_id': args['order_id'],
            'organization_id': args['organization_id'],
            'created_by': args['created_by'],
            'timestamp': args['timestamp'],
        }

        activity_payload  = { **invoices_payload, 'name': 'create_invoice' }

        invoice_result = insert_into_db('Invoices', invoices_payload)

        args['invoice_id'] = invoice_result['id']

        activity_result = cls.insert_activity_into_db(activity_payload)

        firing_webhooks(organization_id=args["organization_id"], event='invoices.created', event_data=invoices_payload)

        return {
            'activity_id': activity_result['id'],
            'invoice_id': invoice_result['id'],
        }
