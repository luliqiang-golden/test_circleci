"""Class to handle requests to update an external crm account"""
import psycopg2.extras
from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler
from copy import deepcopy


class ExternalCRMAccountUpdate(ActivityHandler):

    required_args = {
        'name',
        'crm_account_id',
        'account_name', 
        'account_type'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Update external crm accounts info

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """
        cls.check_required_args(args)
        
        crm_accounts_object = deepcopy(args)
        
        crm_accounts_object["name"] = args["account_name"]
            
        crm_accounts_object.pop("account_name")

        if (crm_accounts_object["account_type"] == "patient"):
            if "expiration_date" in crm_accounts_object:
                crm_accounts_object.pop("expiration_date")
        
        update_result = update_into_db(
            "crm_accounts", args['crm_account_id'], crm_accounts_object)
        
        activity_result = cls.insert_activity_into_db(args)
        return {
            "activity_id": activity_result["id"],
            "affected_rows": update_result['affected_rows']
        }
