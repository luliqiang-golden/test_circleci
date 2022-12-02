"""External Shipment Update Shipping Address"""
from db_functions import update_into_db
from activities.activity_handler_class import ActivityHandler


class ExternalShipmentUpdateShippingAddress(ActivityHandler):
    """External Shipment Update Shipping Address"""

    required_args = {
        'name',
        'shipment_id', 
        'to_shipping_address',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """External Shipment Update Shipping Address"""

        cls.check_required_args(args)

        update_db_result = update_into_db(
            'shipments', args['shipment_id'], {'shipping_address': args["to_shipping_address"]})
     
        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "affected_shipment_rows":update_db_result["affected_rows"]
        }
