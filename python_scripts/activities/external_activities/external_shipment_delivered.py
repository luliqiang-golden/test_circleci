""" external shipment delivered """
from db_functions import update_into_db, update_inventories_attributes_for_shipping_from_db, update_inventories_stats_for_shipping_from_db, update_orders_shipping_status_from_db,  update_resource_attribute_into_db
from activities.activity_handler_class import ActivityHandler


class ExternalShipmentDelivered(ActivityHandler):
    """ external shipment delivered """

    required_args = {
        'name',
        'shipment_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """external shipment delivered"""
                
        cls.check_required_args(args)
            
        update_result = update_into_db("shipments", args['shipment_id'], {'status': "delivered"})

        update_all_rooms = update_inventories_attributes_for_shipping_from_db(args['shipment_id'], args['organization_id'], "room", "")
        update_orders_shipping_status = update_orders_shipping_status_from_db(args['shipment_id'], args['organization_id'], "delivered")
        # reduce_inventory_result = update_inventories_stats_for_shipping_from_db(args) 
        activity_result = cls.insert_activity_into_db(args)
        update_resource_attribute_into_db("shipments", args['shipment_id'], "room", "")

        return {
            "activity_id": activity_result["id"],
            "shipment_affected_rows": update_result["affected_rows"],
            "inventory_affected_rows_for_room": update_all_rooms["affected_rows"],
            # "inventory_affected_rows_for_stats":reduce_inventory_result["affected_rows"],
            "orders_affected_rows":update_orders_shipping_status["affected_rows"]
        }
