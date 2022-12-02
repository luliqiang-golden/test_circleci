"""Record Transaction"""
from db_functions import insert_into_db
from activities.activity_handler_class import ActivityHandler


class RecordTransaction(ActivityHandler):
    """
    Record Transaction
    :param crm_account_id: account id tied to the transaction
    """

    required_args = {
        'crm_account_id',
        'purchase_order'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Do the activity

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param description: note associated with the transaction
        """

        cls.check_required_args(args)

        transaction_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "crm_account_id": args["crm_account_id"],
            "purchase_order": args["purchase_order"],
            "total_amount": 0, #inital transaction amount is 0
            "timestamp": args["timestamp"],
        }

        if "description" in args:
            transaction_object["description"] = args["description"]

        transaction_result = insert_into_db('transactions', transaction_object)

        args["transaction_id"] = transaction_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "transaction_id": transaction_result["id"]
        }
