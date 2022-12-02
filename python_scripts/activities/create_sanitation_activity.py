"""Class to handle requests to create a deviation report"""
from class_errors import ClientBadRequest
from activities.activity_handler_class import ActivityHandler

class CreateSanitationActivity(ActivityHandler):
    """Action to create a sanitation activity"""

    required_args = {
        'name',
        'organization_id',
        'created_by',
        'activity_type',
        'activity_name',
        'rooms',
        'logged_by',
    }
    def validate_args(args):
        if not args["rooms"]:
            raise ClientBadRequest({
                "code": "create_sanitation_rooms_error",
                "message": "rooms can not be empty"
            }, 400)

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new sanitation activity"""
        
        cls.check_required_args(args)
        cls.validate_args(args)

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
        }
