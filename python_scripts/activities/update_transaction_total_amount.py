from activities.activity_handler_class import ActivityHandler
from db_functions import update_into_db, select_resource_from_db
from decimal import Decimal


class UpdateTransactionTotalAmount(ActivityHandler):

    """ Activity to update the total amount in transactions
    
    :param amount: amount associated with the transacation allocation
    :param organization_id: ID of the organization
    :param from_transaction_id: Transaction ID when amount has to be reduced from the transaction
    :param to_transaction_id: Transaction ID when amount has to be added to the transaction
    
    """
   
    required_args = {
        'amount',
        'organization_id',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):

        """
        Do the activity - update the transaction amount 

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict 
        """

        cls.check_required_args(args)

        if 'from_transaction_id' in args:

            transaction_object = select_resource_from_db(
            'transactions', args['from_transaction_id'], args['organization_id'])

            previous_transaction_amount = transaction_object['total_amount']

            current_transaction_amount = previous_transaction_amount - Decimal(args["amount"])

            update_db_result = update_into_db(
            'transactions', args['from_transaction_id'], {'total_amount': current_transaction_amount})

        elif 'to_transaction_id' in args:

            transaction_object = select_resource_from_db(
            'transactions', args['to_transaction_id'], args['organization_id'])

            previous_transaction_amount = transaction_object['total_amount']

            current_transaction_amount = previous_transaction_amount + Decimal(args["amount"])

            update_db_result = update_into_db(
            'transactions', args['to_transaction_id'], {'total_amount': current_transaction_amount})

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": update_db_result['affected_rows']
        }
