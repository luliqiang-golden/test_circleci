""" shipment update delivered date """
from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler
from class_external_webhooks import firing_webhooks

class ShipmentUpdateDeliveredDate(ActivityHandler):
    """ shipment updatedelivered date """

    required_args = {
        'name',
        'shipment_id',
        'to_delivered_date',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """shipment update delivered date"""
                
        cls.check_required_args(args)

        update_result = update_into_db("shipments", args['shipment_id'], {'delivered_date': args['to_delivered_date']})
        activity_result = cls.insert_activity_into_db(args)
        firing_webhooks(organization_id=args.get("organization_id"), event='shipments.updated',
                        event_data=args)
        return {
            "activity_id": activity_result["id"],
            "shipment_affected_rows": update_result["affected_rows"],
        }
