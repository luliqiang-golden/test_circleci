"""
capa_approve_action_plan - approve all action plan actions
"""

from db_functions import update_into_db
from db_functions import bulk_update_column_into_db
from activities.activity_handler_class import ActivityHandler


class CapaApproveActionPlan(ActivityHandler):
    """
    Approve all action plan actions

    :param capa_id: ID of the capa 
    :returns: An object containing the new activity's id, as well as the affected rows of both the capa_actions and capas tables
    """

    required_args = {
        'capa_id',
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

        bulk_update_result = bulk_update_column_into_db("capa_actions", args["organization_id"], 'status', 'approved', [
            ('capa_id', '=', args['capa_id']),
            ('status', '!=', 'canceled')
        ])
        update = {
            'status': 'initiated',
            'actions_approved': bulk_update_result['affected_rows'],
        }
        update_result = update_into_db("capas", args['capa_id'], update)
        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "capas_affected_rows": update_result["affected_rows"],
            "capa_actions_affected_rows": bulk_update_result["affected_rows"]
        }
