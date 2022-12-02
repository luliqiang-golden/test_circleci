"""Update external_order_item_map_to_lot_item"""
from db_functions import update_into_db, update_stat_into_db, select_resource_from_db, DATABASE
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest
from stats.class_stats import Stats
import psycopg2



class ExternalOrderItemMapToLotItem(ActivityHandler):
    """
        Action to map from external order item to lot item
        :param order_item_id: The order item id we wanna map from
        :param inventory_id: The inventory id we wanna map to

        :returns: An object containing the new activity's id, affected_inventories_rows and affected_order_items_rows

    """

    required_args = {
        'name',
        'order_item_id',
        'inventory_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
            update order_item_map_to_lot_item 
            :param cls: this class
            :param args: arguments passed to the activity handler from the client
            :type args: dict
            :param current_user: current user object        
        """

        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()  

        try:

            update_inventories_result = update_into_db(
                'inventories', args['inventory_id'], {'order_item_id': args['order_item_id']})

            inventory_result = select_resource_from_db(
                'inventories', args['inventory_id'], args['organization_id'])

            qty_unit = ''
            for stat in inventory_result['stats']:
                qty_unit = stat

            
            serialized_stats = Stats.serialize_stats(inventory_result['stats'])
            if (serialized_stats):
                stats_result = serialized_stats['qty']
                qty_unit = serialized_stats['unit']
            else:
                raise Exception('Could not find a proper unit')

            update_order_items_result = update_stat_into_db(
                'order_items',
                'shipped_stats',
                args['order_item_id'],
                qty_unit,
                float(stats_result),
                organization_id=args["organization_id"]
            )

            activity_result = cls.insert_activity_into_db(args)

            DATABASE.dedicated_connection().commit()

            return {
                "activity_id": activity_result["id"],
                "affected_inventories_rows": update_inventories_result["affected_rows"],
                "affected_order_items_rows": update_order_items_result['affected_rows']
            }
        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError) as error:            
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "order_item_map_to_lot_item",
                "message": "There was an error mapping the order item to lot item: "+error.args[0]
            }, 500)

    def checkObject(obj, property):
        try:
            obj[property]
            return True
        except:        
            return False

