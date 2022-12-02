"""Class to handle requests to create a crm account"""
from db_functions import insert_into_db
from copy import deepcopy

from activities.activity_handler_class import ActivityHandler
from class_external_webhooks import firing_webhooks


class CreateCRMAccount(ActivityHandler):
    """Action to create a crm account"""

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
        if args.get("account_type") == "patient":
            cls.required_args.add("expiration_date")

        cls.check_required_args(args)

        crm_accounts_object = deepcopy(args)

        crm_accounts_object["name"] = args["account_name"]

        crm_accounts_object.pop("account_name")

        if (crm_accounts_object.get("account_type") == "patient") or (crm_accounts_object.get("expiration_date")):
            crm_accounts_object.pop("expiration_date")
        else:
            args["expiration_date"] = "notset"

        crm_accounts_object.pop("status")

        crm_accounts_result = insert_into_db(
            'crm_accounts', crm_accounts_object)

        args["crm_account_id"] = crm_accounts_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        if args.get('account_type') == 'patient':
            firing_webhooks(organization_id=args["organization_id"], event='crm_accounts.created', event_data=crm_accounts_object)

        return {
            "crm_account_id": crm_accounts_result["id"],
            "activity_id": activity_result["id"],

        }
