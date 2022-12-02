"""Org Update Tax Details"""
from db_functions import update_into_db
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler
class OrgUpdateTaxNumbers(ActivityHandler):
    """Org Update Tax Details"""
    required_args = {'name', 'organization_id', 'tax_numbers'}
    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)
        update_value = {"tax_numbers": args['tax_numbers']}
        db_result = update_into_db('organizations', args['organization_id'],
                                   update_value)
        activity_result = cls.insert_activity_into_db(args)
        if db_result['affected_rows'] == 0:
            raise ClientBadRequest({
                "code": "organization_tax_numbers_update_error",
                "message": "Error updating organization's tax_numbers"
            }, 500)
        return {
            "activity_id": activity_result["id"],
            "affected_rows": db_result['affected_rows']
        }