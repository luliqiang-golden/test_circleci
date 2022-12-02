"""Record order_cancel_item"""
from activities.activity_handler_class import ActivityHandler
from db_functions import select_resource_from_db, update_into_db, update_stat_into_db, update_resource_attribute_into_db, select_from_db, DATABASE, update_total_order
from class_errors import ClientBadRequest
import json
import psycopg2
from class_external_webhooks import firing_webhooks
from stats.class_stats import Stats


class OrderCancelItem(ActivityHandler):
    """
        Action to cancel an order item
        :param order_item_id: The existing order item id
        :param cancelled_by: Who wants to cancel the item from the client side
        
        :returns: An object containing the new activity's id and the new shipment's id
    """

    required_args = {
        'name',
        'order_item_id',
        'cancelled_by'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Create a new shipment        
            :param cls: this class
            :param args: arguments passed to the activity handler from the client
            :type args: dict
            :param current_user: current user object
        """

        cls.check_required_args(args)
        DATABASE.dedicated_connection().begin()        
        try:
            args['to_status'] = "cancelled"

            order_item_result = select_resource_from_db(
                'order_items', args['order_item_id'], args['organization_id'])

            args['order_id'] = order_item_result['order_id']


            serialized_stats = Stats.serialize_stats(order_item_result['ordered_stats'])
            if (serialized_stats):
                stats_result = serialized_stats['qty']
                qty_unit = serialized_stats['unit']
            else:
                raise Exception('Could not find a proper unit')
           
                
            update_stat_result = update_stat_into_db(
                'orders', 'ordered_stats', args['order_id'], qty_unit, float(stats_result), organization_id=args["organization_id"],subtract=True)
            
            sku = cls.get_sku_by_order_item(args['organization_id'], args['order_item_id']) 
            update_skus_attribute = update_resource_attribute_into_db('skus', sku['sku_id'], 'reserved', sku['reserved_quantity'] - order_item_result['quantity'])

            update_db_result = update_into_db("order_items", args['order_item_id'], {'status': args['to_status']})

            update_total_order(args["order_id"], args["organization_id"], args["include_tax"])

            activity_result = cls.insert_activity_into_db(args)

            DATABASE.dedicated_connection().commit()
            firing_webhooks(organization_id=args["organization_id"], event='orders.cancel', event_data=args)
            return {
                'activity_id': activity_result['id'],
                'affected_order_rows': update_stat_result['affected_rows'],
                'affected_sku_rows': update_skus_attribute['affected_rows'],
                'affected_order_item_rows': update_db_result['affected_rows'],
            }
        except(psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError, Exception) as error:
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest(
                {
                    "code": "cancel_order_item",
                    "message": "There was an error canceling an order item. Error: "+error.args[0]
                }, 500)



    def get_sku_by_order_item(org_id, order_item_id):
        """
            Get the sku id and reserverd quantity by order item id        
            :org_id: organization id
            :param order_item_id: order item it
        """
        params = { 'org_id': org_id, 'order_item_id': order_item_id }
        
        query = '''
            select  s.id as sku_id,
                    cast(coalesce(s.attributes->>'reserved','0') as integer) as reserved_quantity
            from skus as s 
            inner join order_items as o on o.sku_id = s.id
            where s.organization_id=%(org_id)s 
            and o.id = %(order_item_id)s  
        '''

        result = select_from_db(query, params)
        if (result):            
            return result[0]
    
    def checkObject(obj, property):
        try:
            obj[property]
            return True
        except:        
            return False



    