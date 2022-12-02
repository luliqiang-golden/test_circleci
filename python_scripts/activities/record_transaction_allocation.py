"""Record Transaction Allocation - from consumable lot or inventory"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler

from class_errors import ClientBadRequest


class RecordTransactionAllocation(ActivityHandler):

    """ Record transaction allocation
    
    :raises ClientBadRequest: when neither inventory_id nor consumable_lot_id is provided
    :return: activity_id and transaction_allocation_id
    :rtype: dict
    """
    
    required_args = {
        'amount',
        'transaction_id',
        'type',
        'timestamp',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """ Do the activity - record transaction allocation
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param amount: transaction amount
        :param transaction_id: the id of the transaction
        :param type: credit/debit
        :param current_user: current user object

        """

        cls.check_required_args(args)

        transaction_allocation_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "amount": args["amount"],
            "transaction_id": args["transaction_id"],
            "type": args["type"],
            "timestamp": args["timestamp"],
        }

        if "inventory_id" in args:
            transaction_allocation_object['inventory_id'] = args['inventory_id']
        elif "consumable_lot_id" in args:
            transaction_allocation_object['consumable_lot_id'] = args['consumable_lot_id']
        else:
            raise ClientBadRequest(
                {
                    "code": "record_transaction_allocation_missing_args",
                    "description": "Client sent activity with missing fields - inventory_id or consumable_lot_id"
                }, 400)

        transaction_allocation_result = insert_into_db('transaction_allocations', transaction_allocation_object)

        args["transaction_allocation_id"] = transaction_allocation_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "transaction_allocation_id": transaction_allocation_result["id"]
        }
