"""Org Update Fallback Tax Value"""

from db_functions import DATABASE, update_into_db

from class_errors import ClientBadRequest


from activities.activity_handler_class import ActivityHandler


class OrgUpdateFallbackTaxValue(ActivityHandler):
    """Org Update Fallback Tax Value"""

    required_args = {'name', 'organization_id', 'fallback_tax_value'}

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        update_value = {"fallback_tax_value": args['fallback_tax_value']}
        
        DATABASE.dedicated_connection().begin() 
        try:

            db_result = update_into_db('organizations', args['organization_id'],
                                   update_value)

            activity_result = cls.insert_activity_into_db(args)

            if db_result['affected_rows'] == 0:
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest({
                "code": "organization_use_batch_name_column_as_link_update_error",
                "message": "Error updating organization use batch name column as hyperlink"
                }, 500)

            DATABASE.dedicated_connection().commit()
        except:
            DATABASE.dedicated_connection().rollback()
            
        return {
            "activity_id": activity_result["id"],
            "affected_rows": db_result['affected_rows']
        }