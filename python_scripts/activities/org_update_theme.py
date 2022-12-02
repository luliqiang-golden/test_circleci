"""Org Update Theme"""

from db_functions import update_into_db

from class_errors import ClientBadRequest


from activities.activity_handler_class import ActivityHandler


class OrgUpdateTheme(ActivityHandler):
    """Org Update Theme"""

    required_args = {'name', 'organization_id', 'theme'}

    @classmethod
    def do_activity(cls, args, current_user):

        cls.check_required_args(args)

        if not args['theme']:
            raise ClientBadRequest(
                {
                    "code": "empty_organization_theme",
                    "message": "Update theme activity cannot have empty theme"
                }, 400)

        if ('logo' not in args['theme']
                or args['theme']['logo'].find('base64') == -1):
            raise ClientBadRequest({
                "code": "invalid_theme_info",
                "message": "Theme info format is invalid"
            }, 400)

        update_value = {"theme": args['theme']}

        db_result = update_into_db('organizations', args['organization_id'],
                                   update_value)

        activity_result = cls.insert_activity_into_db(args)

        if db_result['affected_rows'] == 0:
            raise ClientBadRequest({
                "code": "organization_theme_not_updated",
                "message": "Error updating organization theme."
            }, 500)

        return {
            "activity_id": activity_result["id"],
            "affected_rows": db_result['affected_rows']
        }
