""" order update status """
from db_functions import  DATABASE, update_multiple_columns, update_total_order, select_resource_from_db
from activities.activity_handler_class import ActivityHandler
from class_errors import ClientBadRequest
import psycopg2
from copy import deepcopy
from decimal import Decimal
from taxes.class_tax_factory import TaxFactory
from class_external_webhooks import firing_webhooks


class OrderItemUpdate(ActivityHandler):
    """
        Action to update order item
       
        :returns: An object containing the activity id and order_items_affected_rows
    """

    required_args = {
        'order_item_id',
        'order_id'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """ 
            update any field of order item
            :param cls: this class
            :param args: arguments passed to the activity handler from the client
            :type args: dict
            :param current_user: current user object
        """

        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()       
        try:              
            order_item = select_resource_from_db('order_items', args["order_item_id"], args["organization_id"])

            old_data = {}
            for prop in order_item.keys():     
                try:  
                    # Don't need to record this as old values because they don't change.
                    if (prop in ['id', "organization_id", "created_by, order_id"]):
                        continue

                    # just to check if there is this property, if not exception will raise
                    args[prop]

                    if isinstance(order_item[prop], Decimal):
                        old_data[prop] = float(order_item[prop])    
                    else: 
                        old_data[prop] = order_item[prop]         
                except:
                    pass

            args["old_data"] = old_data
            
            activity_result = cls.insert_activity_into_db(args)
            
            taxObj = TaxFactory.get_instance(args["order_item_id"], args["price"], args["organization_id"])
            if (taxObj) :
                values = taxObj.do_calculation()
                args.update(values)
            
            update_result = update_multiple_columns("order_items", args, {"id": args["order_item_id"]})
            
            if ("price" in args):
                update_total_order(args["order_id"], args["organization_id"], args["include_tax"])

            firing_webhooks(organization_id=args["organization_id"], event='order_items.updated', event_data=args)
            DATABASE.dedicated_connection().commit()

            return {
                "activity_id": activity_result["id"],
                "order_item_affected_row": update_result["affected_rows"],
            }
       
        except(psycopg2.Error, psycopg2.Warning,
        psycopg2.ProgrammingError, Exception) as error:            
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "order_item_update",
                "message": "There was an error updating an order item. Error: "+error.args[0]
            }, 500)



