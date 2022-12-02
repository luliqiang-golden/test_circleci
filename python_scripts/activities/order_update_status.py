""" order update status """
from db_functions import update_into_db
from db_functions import bulk_update_column_into_db
from db_functions import update_resource_attribute_into_db, select_from_db, delete_from_db, DATABASE
from activities.activity_handler_class import ActivityHandler
from activities.create_invoice import CreateInvoice
from class_errors import ClientBadRequest
import psycopg2

from class_external_webhooks import firing_webhooks


class OrderUpdateStatus(ActivityHandler):
    """
        Action to update the status of the order
        :param order_id: The existing order id
        :param to_status: new status
        :returns: An object containing the activity_id, orders_affected_rows and order_items_affected_rows
    """

    required_args = {
        'name',
        'order_id',
        'to_status',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """ 
            order update status
            :param cls: this class
            :param args: arguments passed to the activity handler from the client
            :type args: dict
            :param current_user: current user object
        """

        cls.check_required_args(args)
        DATABASE.dedicated_connection().begin()
        try:
            update_result = update_into_db("orders", args['order_id'], {'status': args['to_status']})

            if (args['to_status'] == 'approved'):
                CreateInvoice.do_activity(args, {})

            if (args['to_status'] == 'cancelled'):
                update_into_db("orders", args['order_id'], {'shipping_status': 'cancelled'})

                order_items = cls.get_order_items_quantity_reserved(args['order_id'])
                if (order_items):
                    for order_item in order_items:
                        update_resource_attribute_into_db('skus', order_item['sku_id'], 'reserved',
                                                          order_item['reserved_quantity'] - order_item['quantity'])
                        activities_list = cls.get_order_item_map_to_lot_item_activity_id(args['organization_id'],
                                                                                         order_item['id'])
                        if (activities_list):
                            for activity in activities_list:
                                delete_from_db("activities", activity['id'], args['organization_id'])

            bulk_update_result = bulk_update_column_into_db("order_items", args["organization_id"], 'status',
                                                            args["to_status"], [('order_id', '=', args['order_id']),
                                                                                ('status', '!=', 'cancelled')])

            activity_result = cls.insert_activity_into_db(args)
            firing_webhooks(organization_id=args["organization_id"], event='orders.updated', event_data=args)
            DATABASE.dedicated_connection().commit()
            return {
                "activity_id": activity_result["id"],
                "orders_affected_rows": update_result["affected_rows"],
                "order_items_affected_rows": bulk_update_result["affected_rows"]
            }

        except(psycopg2.Error, psycopg2.Warning,
               psycopg2.ProgrammingError) as error:
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
                {
                    "code": "update__status_order",
                    "message": "There was an error updating status of an order. Error: " + error.args[0]
                }, 500)

    def get_order_items_quantity_reserved(order_id):
        """
            Get order items with its reserved quantity
            :param order_id: The existing order id
        """
        params = {'order_id': order_id}

        query = '''
            select  o.id, sku_id, coalesce(quantity,0) as quantity, cast(coalesce(s.attributes->>'reserved','0') as integer) as reserved_quantity  				
            from order_items as o
                inner join skus as s on s.id = o.sku_id
            where o.order_id = %(order_id)s and
                    o.status != 'cancelled'
        '''

        result = select_from_db(query, params)
        if (result):
            return result

    def get_order_item_map_to_lot_item_activity_id(org_id, order_item_id):
        """
                Get all the activities order_item_map_to_lot_item related with the order item
                :param org_id: organization id
                :param order_item_id: The existing order item id
            """
        params = {'org_id': org_id, 'order_item_id': order_item_id}

        query = '''
                select *
                from activities
                where
                    name = 'order_item_map_to_lot_item' and
                    cast(data->>'order_item_id' as integer) = %(order_item_id)s and
                    organization_id = %(org_id)s 
            '''

        result = select_from_db(query, params)
        if (result):
            return result
