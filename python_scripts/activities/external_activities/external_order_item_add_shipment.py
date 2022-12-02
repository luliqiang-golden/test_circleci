""" External Order Item Add Shipment"""
from db_functions import update_into_db, execute_query_into_db, select_from_db
from activities.activity_handler_class import ActivityHandler
from class_external_webhooks import firing_webhooks


class ExternalOrderItemAddShipment(ActivityHandler):
    """
        Action to sign a shipment to an external order item
        :param shipment_id: The existing shipment id
        :param order_item_id: The existing order id
        :param quantity_filled: Quantity filled
        
        :returns: An object containing the activity_id and the affected_order_item_rows
    """

    required_args = {
        'name',
        'shipment_id', 
        'order_item_id',
        'quantity_filled'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
            Order Item Add Shipment
            :param cls: this class
            :param args: arguments passed to the activity handler from the client
            :type args: dict
            :param current_user: current user object
        """

        cls.check_required_args(args)

        update_db_result = update_into_db(
            'order_items', args['order_item_id'], {'shipment_id': args["shipment_id"], 'filled': args["quantity_filled"]})
     
        activity_result = cls.insert_activity_into_db(args)
        cls.update_skus_current_inventory(args.get("organization_id"),args.get('order_item_id'))
        sku_detail = cls.get_sku_by_order_item(args.get("organization_id"), args.get('order_item_id'))
        firing_webhooks(organization_id=args.get("organization_id"), event='skus.updated', event_data=sku_detail)
        return {
            "activity_id": activity_result["id"],
            "affected_order_item_rows":update_db_result["affected_rows"]
        }

    def update_skus_current_inventory(organization_id, order_item_id):
        '''Substracts filled quantity from skus current_inventory in order to update the column'''
        params = {'organization_id': organization_id, 'order_item_id': order_item_id}
        query = '''
            UPDATE skus
            SET current_inventory = skus.current_inventory-order_items.filled
            FROM order_items
            WHERE skus.id = order_items.sku_id 
            AND order_items.id = %(order_item_id)s
            AND order_items.organization_id = %(organization_id)s
        '''
        return execute_query_into_db(query, params)

    def get_sku_by_order_item(organization_id, order_item_id):
        '''Returns sku detail by order_item_id'''
        params = {'organization_id': organization_id, 'order_item_id': order_item_id}
        query = '''
            select  s.id as sku_id, s.name, s.current_inventory, s.price, s.variety,
            s.data->>'external_sku_id' as external_sku_id,
            s.data->>'external_sku_variant_id' as external_sku_variant_id
            from skus as s 
            inner join order_items as oi on oi.sku_id = s.id
            where s.organization_id=%(organization_id)s
            and oi.id = %(order_item_id)s 
        '''
        result = select_from_db(query, params)
        if (result):            
            return result[0]
            