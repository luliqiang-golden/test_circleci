""" external shipment packaged """
from db_functions import update_into_db, update_inventories_attributes_for_shipping_from_db, update_orders_shipping_status_from_db, update_resource_attribute_into_db
from activities.activity_handler_class import ActivityHandler


class ExternalShipmentPackaged(ActivityHandler):
    """
        Action to package the external shipment
        :param shipment_id: The existing shipment id
        :param to_room: name the room
        
        :returns: An object containing the activity_id, shipment_affected_rows,inventory_affected_rows and orders_affected_rows
    """

    required_args = {
        'name',
        'shipment_id',
        'to_room'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
            shipment packaged
            :param cls: this class
            :param args: arguments passed to the activity handler from the client
            :type args: dict
            :param current_user: current user object
        """
                
        cls.check_required_args(args)
            
        update_result = update_into_db("shipments", args['shipment_id'], {'status': "packaged"})
        update_orders_shipping_status = update_orders_shipping_status_from_db(args['shipment_id'], args['organization_id'], "packaged")
        update_all_rooms = update_inventories_attributes_for_shipping_from_db(args['shipment_id'], args['organization_id'], "room", args['to_room'])
        update_resource_attribute_into_db("shipments", args['shipment_id'], 'room', args['to_room'])


        activity_result = cls.insert_activity_into_db(args)

        return {
            "activity_id": activity_result["id"],
            "shipment_affected_rows": update_result["affected_rows"],
            "inventory_affected_rows": update_all_rooms["affected_rows"],
            "orders_affected_rows":update_orders_shipping_status["affected_rows"],
        }
