"""Org Update Upload Formats"""

from db_functions import update_into_db

from class_errors import ClientBadRequest


from activities.activity_handler_class import ActivityHandler


class OrgUpdateUploadFormats(ActivityHandler):
    """Org Update Upload Formats"""

    required_args = {'name', 'organization_id', 'upload_formats'}

    @classmethod
    def do_activity(cls, args, current_user):
        cls.check_required_args(args)

        update_value = {"upload_formats": args['upload_formats']}

        db_result = update_into_db('organizations', args['organization_id'],
                                   update_value)

        activity_result = cls.insert_activity_into_db(args)

        if db_result['affected_rows'] == 0:
            raise ClientBadRequest({
                "code": "organization_upload_formats_update_error",
                "message": "Error updating organization upload formats"
            }, 500)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": db_result['affected_rows']
        }
