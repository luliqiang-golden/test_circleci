"""Order Add Item"""
from db_functions import insert_into_db, update_stat_into_db, select_from_db, update_into_db, DATABASE, \
    update_total_order
from activities.activity_handler_class import ActivityHandler
from db_functions import update_resource_attribute_into_db, update_multiple_columns
from class_errors import ClientBadRequest
import psycopg2
from taxes.class_tax_factory import TaxFactory


class ExternalOrderAddItem(ActivityHandler):
    """
        Action to add a Item into an Order
        :param order_id: The existing order id
        :param sku_id: The existing sku id
        :param sku_name: The sku name
        :param sku_name: The sku name
        :param to_qty: the amount of the product added
        :param to_qty_unit: the unit of the product added
        :param variety: the variety of the product added
        :param quantity: how many item added at once
        
        :returns: An object containing the new activity's id and the new order_item_id's id, affected_order_rows and affected_order_item_rows

    """

    required_args = {
        'name',
        'order_id',
        'sku_id',
        'sku_name',
        'to_qty',
        'to_qty_unit',
        'variety',
        'quantity',
        'price'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """Adding new order item
           :param cls: this class
           :param args: arguments passed to the activity handler from the client
           :type args: dict
           :param current_user: current user object
        """

        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()
        try:
            order_item_result = {}
            order_item = cls.get_order_item(args["organization_id"], args["order_id"], args["sku_id"])
            price = 0

            if (order_item):
                order_item_result["id"] = order_item['id']
                new_quantity = order_item['quantity'] + args['quantity']
                price = round(float(args["price"]) * int(new_quantity), 2)
                update_into_db("order_items", order_item['id'], {"quantity": new_quantity, "price": price})
            else:
                price = round(float(args["price"]) * int(args["quantity"]), 2)
                order_items_object = {
                    "order_id": args["order_id"],
                    "sku_id": args["sku_id"],
                    "sku_name": args["sku_name"],
                    "status": "awaiting_approval",
                    "variety": args["variety"],
                    "organization_id": args["organization_id"],
                    "created_by": args["created_by"],
                    "quantity": args["quantity"],
                    "price": price,
                }

                if 'external_order_item_id' in args:
                    order_items_object['external_order_item_id'] = args['external_order_item_id']

                order_item_result = insert_into_db('order_items', order_items_object)

            reserved_quantity = cls.get_sku_reserved_quantity(args["organization_id"], args["sku_id"])
            update_resource_attribute_into_db('skus', args['sku_id'], 'reserved', reserved_quantity + args['quantity'])

            args["order_item_id"] = order_item_result["id"]

            update_stat_result_orders = update_stat_into_db(
                'orders', 'ordered_stats', args['order_id'], args['to_qty_unit'], args['to_qty'], organization_id=args["organization_id"])

            update_stat_result_order_items = update_stat_into_db(
                'order_items', 'ordered_stats', args["order_item_id"], args['to_qty_unit'], args['to_qty'], organization_id=args["organization_id"])

            taxObj = TaxFactory.get_instance(order_item_result["id"], price, args["organization_id"])
            if (taxObj):
                values = taxObj.do_calculation()
                update_result = update_multiple_columns("order_items", values, {"id": order_item_result["id"]})

            update_total_order(args["order_id"], args["organization_id"], args["include_tax"])

            activity_result = cls.insert_activity_into_db(args)

            DATABASE.dedicated_connection().commit()

            return {
                "activity_id": activity_result["id"],
                "order_item_id": order_item_result["id"],
                "affected_order_rows": update_stat_result_orders['affected_rows'],
                "affected_order_item_rows": update_stat_result_order_items['affected_rows']
            }

        except (psycopg2.Error, psycopg2.Warning,
                psycopg2.ProgrammingError, Exception) as error:
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
                {
                    "code": "external_add_order_item",
                    "message": "There was an error adding a new item into the order. " + error.args[0]
                }, 500)

    def get_order_item(org_id, order_id, sku_id):
        params = {'org_id': org_id, 'order_id': order_id, 'sku_id': sku_id}

        query = '''
            SELECT *, COALESCE(quantity,0) as quantity
            FROM order_items
            WHERE organization_id=%(org_id)s 
            AND order_id = %(order_id)s
            AND sku_id = %(sku_id)s  
            AND status != 'cancelled'          
        '''

        result = select_from_db(query, params)
        if (result):
            return result[0]

    def get_sku_reserved_quantity(org_id, sku_id):
        params = {'org_id': org_id, 'sku_id': sku_id}

        query = '''
            select cast(coalesce(attributes->>'reserved','0') as integer) as quantity
            from skus
            WHERE organization_id=%(org_id)s 
            AND id = %(sku_id)s  
        '''

        result = select_from_db(query, params)
        if (result):
            return result[0]['quantity']
