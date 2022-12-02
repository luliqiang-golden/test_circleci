"""Class to handle requests to create external crm account"""
from db_functions import insert_into_db
from copy import deepcopy

from activities.activity_handler_class import ActivityHandler


class CreateExternalCRMAccount(ActivityHandler):
    """Action to create an external crm account"""

    required_args = {
        'name',
        'organization_id',
        'created_by',
        'account_name',
        'account_type',
        'status'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new crm account"""
        
        cls.check_required_args(args)

        crm_accounts_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "name": args["account_name"],
            "account_type": args["account_type"],
        }

        crm_accounts_object = deepcopy(args)

        crm_accounts_object["name"] = args["account_name"]

        crm_accounts_object.pop("account_name")


        crm_accounts_result = insert_into_db('crm_accounts', crm_accounts_object)

        args["crm_account_id"] = crm_accounts_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "crm_account_id": crm_accounts_result["id"],
            "activity_id": activity_result["id"]
        }
