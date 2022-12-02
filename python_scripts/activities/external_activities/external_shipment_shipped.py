""" external shipment collected """
from db_functions import update_into_db, update_inventories_attributes_for_shipping_from_db, update_inventories_stats_for_shipping_from_db, update_orders_shipping_status_from_db, execute_query_into_db, update_resource_attribute_into_db, DATABASE
from activities.activity_handler_class import ActivityHandler
import psycopg2


class ExternalShipmentShipped(ActivityHandler):
    """
        Action to ship the external shipment
        :param shipment_id: The existing shipment id
        
        :returns: An object containing the activity_id, shipment_affected_rows, inventory_affected_rows_for_room and orders_affected_rows
    """

    required_args = {
        'name',
        'shipment_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
            shipment shipped
            :param cls: this class
            :param args: arguments passed to the activity handler from the client
            :type args: dict
            :param current_user: current user object
        """
                
        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()  

        try:
            update_result = update_into_db("shipments", args['shipment_id'], {'status': "shipped"})

            update_all_rooms = update_inventories_attributes_for_shipping_from_db(args['shipment_id'], args['organization_id'], "room", "in_transit")
            update_orders_shipping_status = update_orders_shipping_status_from_db(args['shipment_id'], args['organization_id'], "shipped")
            update_resource_attribute_into_db("shipments", args['shipment_id'], "room", "in_transit")
            activity_result = cls.insert_activity_into_db(args)

            response_object = {
                "activity_id": activity_result["id"],
                "shipment_affected_rows": update_result["affected_rows"],
                "inventory_affected_rows_for_room": update_all_rooms["affected_rows"],
                "orders_affected_rows":update_orders_shipping_status["affected_rows"]
            }


            if 'reduce_inventory' in args:
                reduce_inventory_result = update_inventories_stats_for_shipping_from_db(args)
                remove_reserved = cls.remove_reserved_quantity(args['shipment_id'], args['organization_id'])
                response_object['inventory_affected_rows_for_stats'] = reduce_inventory_result["affected_rows"]
                response_object['remove_reserved_affected_rows'] = remove_reserved["affected_rows"]

            DATABASE.dedicated_connection().commit()
            return response_object
        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:            
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "shipment_shipped",
                "message": "There was an error shipping the shipment. Error: "+error.args[0]
            }, 500)

    def remove_reserved_quantity(shipment_id, organization_id):
        """
            Remove quantity reserverd after ship it out    
            :param shipment_id: The existing shipment id
            :param organization_id: organization ID
        """
        params = { 'org_id': organization_id, 'shipment_id': shipment_id }
            
        query = '''
            update skus
                set attributes = jsonb_set(attributes, array['reserved'], (t1.reserved-t1.quantity)::text::jsonb)  
            from (
                select s.id, s.name, oi.quantity, cast(s.attributes->>'reserved' as integer) as reserved from shipments as sp
                    inner join order_items as oi on oi.shipment_id = sp.id
                    inner join skus as s on s.id = oi.sku_id
                where sp.id = %(shipment_id)s and
                    sp.organization_id=%(org_id)s and
                    oi.status = 'approved'
                group by s.id, s.name, oi.quantity, cast(s.attributes->>'reserved' as integer)
            ) as t1
                        
        '''

        result = execute_query_into_db(query, params)
        if (result):            
            return result
