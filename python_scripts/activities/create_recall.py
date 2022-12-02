"""Class to handle requests to create a recall"""
from db_functions import insert_into_db

from activities.activity_handler_class import ActivityHandler


class CreateRecall(ActivityHandler):
    """
    Create a Recall

    :param organization_id: ID of the organization 
    :param description: description of the recall
    :param created_by: staff member who is reporting the recall
    :param contact_user: staff member who is responsible the recall
    :param lot_ids: array of lots included in recall

    :returns: An object containing the new recall id and the corresponding activity's id 
    """

    required_args = {
        'description',
        'created_by',
        'organization_id',
        'contact_user',
        'lot_ids'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Do the activity

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        cls.check_required_args(args)

        recall_object = {
            "description": args["description"],
            "created_by": args["created_by"],
            "organization_id": args["organization_id"],
            "contact_user": args["contact_user"],
            "lot_ids": args["lot_ids"],
        }

        recall_result = insert_into_db('recalls', recall_object)

        args["recall_id"] = recall_result["id"]

        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "recall_id": recall_result["id"]
        }
