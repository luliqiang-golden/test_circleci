"""Shipment Update Shipping Address"""
from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler
from class_external_webhooks import firing_webhooks


class ShipmentUpdateShippingAddress(ActivityHandler):
    """Shipment Update Shipping Address"""

    required_args = {
        'name',
        'shipment_id',
        'to_shipping_address',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Shipment Update Shipping Address"""

        cls.check_required_args(args)

        update_db_result = update_into_db(
            'shipments', args['shipment_id'], {'shipping_address': args["to_shipping_address"]})

        activity_result = cls.insert_activity_into_db(args)
        firing_webhooks(organization_id=args.get("organization_id"), event='shipments.updated',
                        event_data=args)
        return {
            "activity_id": activity_result["id"],
            "affected_shipment_rows": update_db_result["affected_rows"]
        }
