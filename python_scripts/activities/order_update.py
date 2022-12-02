""" order update status """
from db_functions import  DATABASE, update_multiple_columns, update_total_order, select_resource_from_db
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest
import psycopg2
from decimal import Decimal
from class_external_webhooks import firing_webhooks


class OrderUpdate(ActivityHandler):
    """
        Action to update order
        
        :returns: An object containing activity id and orders_affected_rows
    """

    required_args = {
        'order_id',
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """ 
            update any field of order 
            :param cls: this class
            :param args: arguments passed to the activity handler from the client
            :type args: dict
            :param current_user: current user object
        """
                
        cls.check_required_args(args)
        
        DATABASE.dedicated_connection().begin() 
        
        include_tax = None
        if ("include_tax" in args):
            include_tax = args["include_tax"]
                   
        try:
            order = select_resource_from_db('orders', args["order_id"], args["organization_id"])
            update_result = update_multiple_columns("orders", args, { "id": args["order_id"]})
            old_data = {}
            for prop in order.keys():     
                try:      
                    # Don't need to record this as old values because they don't change.
                    if (prop in ['id', "organization_id", "created_by"]):
                        continue
                    
                    # just to check if there is this property, if not exception will raise
                    args[prop]

                    if isinstance(order[prop], Decimal):
                        old_data[prop] = float(order[prop])    
                    else: 
                        old_data[prop] = order[prop] 
                except:
                    pass

            args["old_data"] = old_data

            provincial_old = old_data['provincial_tax'] if hasattr(old_data, 'provincial_tax') else None
            activity_result = cls.insert_activity_into_db(args)
            
            if ("discount_percent" in args or "shipping_value" in args or include_tax != None):                
                update_total_order(args["order_id"], args["organization_id"], include_tax, provincial_old)
            firing_webhooks(organization_id=args["organization_id"], event='orders.updated', event_data=args)
            DATABASE.dedicated_connection().commit()   


            object_return = { "activity_id": activity_result["id"]}
            if (update_result):
                object_return["order_affected_row"] = update_result["affected_rows"]
            return object_return

        except(psycopg2.Error, psycopg2.Warning,
        psycopg2.ProgrammingError) as error:            
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "order_update",
                "message": "There was an error updating status order. Error: "+error.args[0]
            }, 500)



    