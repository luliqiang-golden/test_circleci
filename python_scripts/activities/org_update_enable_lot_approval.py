"""Org Update Enable Lot Approval"""

from db_functions import DATABASE, update_into_db

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler

import psycopg2


class OrgUpdateEnableLotApproval(ActivityHandler):
    """Org Update Enable Lot Approval"""

    required_args = {'name', 'organization_id', 'enable_lot_approval'}

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        update_value = {"enable_lot_approval": args['enable_lot_approval']}

        DATABASE.dedicated_connection().begin()
        try:
            db_result = update_into_db('organizations', args['organization_id'],
                                       update_value)

            activity_result = cls.insert_activity_into_db(args)

            DATABASE.dedicated_connection().commit()

            if db_result['affected_rows'] == 0:
                raise ClientBadRequest({
                    "code": "organization_enable_lot_approval_update_error",
                    "message": "Error updating organization enable signature"
                }, 500)

            return {
                "activity_id": activity_result["id"],
                "affected_rows": db_result['affected_rows']
            }

        except(psycopg2.Error, psycopg2.Warning,
               psycopg2.ProgrammingError) as error:
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
                {
                    "code": "organization_enable_lot_approval_update_error",
                    "message": "Error updating organization enable signature " + error.args[0]
                }, 500)
