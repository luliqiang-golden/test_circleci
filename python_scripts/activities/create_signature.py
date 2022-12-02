"""Class to handle requests to create a signature"""
from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler


class CreateSignature(ActivityHandler):
    """Action to create a signature"""

    required_args = {
        'organization_id',
        'created_by',
        'signed_by',
        'field',
        'timestamp',
        'activity_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new signature"""

        cls.check_required_args(args)

        signature_object = {
            "organization_id": args["organization_id"],
            "created_by": args["created_by"],
            "signed_by": args["signed_by"],
            "field": args["field"],
            "timestamp": args["timestamp"],
            "activity_id": args["activity_id"],
        }

        if "version_id" in args:
            signature_object["version_id"] = args["version_id"]

        signature_result = insert_into_db('Signatures', signature_object)

        args["signature_id"] = signature_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "signature_id": signature_result["id"]
        }
