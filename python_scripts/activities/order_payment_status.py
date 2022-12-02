""" order payment status """
import psycopg2
from psycopg2 import sql
from db_functions import update_into_db, DATABASE, select_from_db
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest, DatabaseError
from decimal import Decimal
from class_external_webhooks import firing_webhooks


class OrderPaymentStatus(ActivityHandler):
    """
        Action to update the payment status of the order
        :param order_id: The existing order id
        :param to_status: new status
        
        :returns: An object containing the activity_id, orders_affected_rows and order_items_affected_rows
    """

    required_args = {
        'name',
        'order_id',
        'payment_status',
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

            params = {}
            params['payment_status'] = args['payment_status']

            if args['payment_date']:
                params['payment_date'] = args['payment_date']

            update_result = update_into_db('orders', args['order_id'], params)

            activity_result = cls.insert_activity_into_db(args)


            # once it receives the payment, we need to do the prorate of the shipping and discount values
            order = cls.get_order(cls, args['organization_id'], args['order_id'])
            order_items = cls.get_order_items(cls, args['organization_id'], args['order_id'])
           
            order_items_result = cls.update_order_items_values(cls, order_items, order["discount_percent"], order["shipping_value"])
            
            # check if there are values to adjust and update the last order item
            values_to_adjust = cls.get_values_to_adjust(cls, args['organization_id'], args['order_id'], order["discount"], order["shipping_value"])
            if (values_to_adjust):
                cls.update_order_item_values_by_id(cls, values_to_adjust["id"], values_to_adjust)

            firing_webhooks(organization_id=args["organization_id"], event='orders.updated', event_data=params)
            DATABASE.dedicated_connection().commit()

            return {
                "activity_id": activity_result["id"],
                "affected_rows": update_result['affected_rows'],
                "order_items_affected_rows": order_items_result["affected_rows"]
            }
        
        except (psycopg2.Error, psycopg2.Warning,
            psycopg2.ProgrammingError, Exception) as error:
                DATABASE.dedicated_connection().rollback()
                raise ClientBadRequest(
                {
                    "code": "order_payment_status",
                    "message": "There was an error receving an order payment. "+error.args[0]
                }, 500)


    def get_order(self, org_id, order_id):
        """ get the order object"""

        try:
            params = {'org_id': org_id, 'order_id': order_id}
            
            query = '''
                SELECT *
                FROM orders
                WHERE organization_id=%(org_id)s 
                AND id = %(order_id)s          
            '''

            result = select_from_db(query, params)
            if (result):      
                return result[0]
            else:
                return None
        except Exception as error:
            raise Exception("Error getting order items - {}".format(error))


    def get_order_items(self, org_id, order_id):
        """ Get order items """
        
        try:
            params = {'org_id': org_id, 'order_id': order_id}
            
            query = '''
                SELECT *
                FROM order_items
                WHERE organization_id=%(org_id)s 
                AND order_id = %(order_id)s
                AND status != 'cancelled'          
            '''

            result = select_from_db(query, params)
            if (result):            
                return result
            else:
                return None
        except Exception as error:
            raise Exception("Error getting order items - {}".format(error))

 
    

    def get_prorated_shipping_value(self, order_items, order_shipping_value):
        """ Get the prorated shipping value """
        try:
            qty_order_items = len(order_items)
            prorated_shipping_value = round(float(order_shipping_value)/qty_order_items, 2)

            return prorated_shipping_value
        except Exception as error:
            raise Exception("Error getting prorated shipping value - {}".format(error))


    def get_prorated_discount_value(self, order_item, order_discount_percent, shipping_value):
        """ Get the prorated discount value by order item """
        try:
            prorated_discount_value = round((order_item["price"] + order_item["provincial_tax"] + Decimal(shipping_value)) * Decimal(order_discount_percent) / 100, 2)
            return float(prorated_discount_value)
        except Exception as error:
            raise Exception("Error getting prorated discount value - {}".format(error))

    
    def update_order_item_values_by_id(self, order_item_id, values):
        """Update the discount and shipping_value of an specific order item"""
        try:
            return update_into_db("order_items", order_item_id, values)
        except Exception as error:
            raise Exception("Error updating order item value by id - {}".format(error))



    def update_order_items_values(self, order_items, order_discount_percent, order_shipping_value):
        """Update all the discount and shipment values of all order items"""
        try:
            shipping_value = self.get_prorated_shipping_value(self, order_items, float(order_shipping_value))
            for order_item in order_items:
                discount_value = self.get_prorated_discount_value(self, order_item, float(order_discount_percent), float(shipping_value))                
                values = {"discount": discount_value, "shipping_value": shipping_value}
                self.update_order_item_values_by_id(self, order_item["id"], values)

            return {"affected_rows": len(order_items)}


        except Exception as error:
            raise Exception("Error updatting prorated values in order_item table - {}".format(error))
 


    def get_values_to_adjust(self, org_id, order_id, order_discount_value, order_shipping_value):
        """check if there is some discount or shipping_value to adjust, if so, the method will return the the values as well as the last order item id"""
        try:
            order_items = self.get_order_items(self, org_id, order_id)
            total_discount = sum(oi["discount"] for oi in order_items)
            total_shipping = sum(oi["shipping_value"] for oi in order_items)
            last_order_item = order_items[len(order_items)-1]
    
            values = {}
            dif_discount = order_discount_value - total_discount
            if (dif_discount != 0):
                values["discount"] = last_order_item["discount"] + dif_discount
    
            dif_shipping = order_shipping_value - total_shipping
            if (dif_shipping != 0):
                values["shipping_value"] = last_order_item["shipping_value"] + dif_shipping
    
    
            if (dif_discount != 0 or dif_shipping != 0):
                values["id"] = last_order_item["id"]
                return values
            else:
                return None
        except Exception as error:
            raise Exception("Error getting shipping and discount values to adjust - {}".format(error))
 
 

    





