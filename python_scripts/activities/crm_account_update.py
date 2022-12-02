"""Class to handle requests to update a crm account"""
import psycopg2.extras
from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler
from copy import deepcopy
from class_external_webhooks import firing_webhooks


class CRMAccountUpdate(ActivityHandler):
    """
    Action to update a crm account
    :param crm_account_id: The existing CRM account id
    :param to_account_name: The new CRM account name
    :param to_account_type: The new CRM account type
    :param to_email: The new email address for the account - string@email.com
    :type to_email: string

    :param to_address : The new value for the account address array
    :type to_address: Array of address objects
    :param to_telephone: New telephone number
    :type to_telephone: String
    :param to_fax: New fax number
    :type to_fax: String


    :returns: An object containing the new activity's id and affected_rows for update

    """
    required_args = {
        'name',
        'crm_account_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Update crm accounts info

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """
        cls.check_required_args(args)

        crm_accounts_object = deepcopy(args)

        crm_accounts_object["name"] = args["account_name"]

        crm_accounts_object.pop("account_name")

        if (crm_accounts_object.get("account_type") == "patient") or (crm_accounts_object.get("expiration_date")):
            crm_accounts_object.pop("expiration_date")
        else:
            args["expiration_date"] = "notset"

        crm_accounts_object.pop("status")

        update_result = update_into_db(
            "crm_accounts", args['crm_account_id'], crm_accounts_object)
        activity_result = cls.insert_activity_into_db(args)

        if args.get('account_type') == 'patient':
            firing_webhooks(organization_id=args.get("organization_id"), event='crm_accounts.updated', event_data=crm_accounts_object)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": update_result['affected_rows']
        }
