"""Org Update Currency"""

from db_functions import update_into_db

from class_errors import ClientBadRequest


from activities.activity_handler_class import ActivityHandler


class OrgUpdateCurrency(ActivityHandler):
    """Org Update Currency"""

    required_args = {'name', 'organization_id', 'currency'}

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        update_value = {"currency": args['currency']}

        db_result = update_into_db('organizations', args['organization_id'],
                                   update_value)

        activity_result = cls.insert_activity_into_db(args)

        if db_result['affected_rows'] == 0:
            raise ClientBadRequest({
                "code": "organization_currency_update_error",
                "message": "Error updating organization currency"
            }, 500)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": db_result['affected_rows']
        }
