"""
received_inventory_return_items - return received inventory 
"""

from class_errors import ClientBadRequest

from activities.activity_handler_class import ActivityHandler
from db_functions import DATABASE, select_resource_from_db, update_into_db
import psycopg2


class ReceivedInventoryReturnItems(ActivityHandler):
    """
    return inventory items
    :param from_inventory_id : received inventory id
    :param from_qty: Used quantity
    :param from_qty_unit: The existing unit
    """

    required_args = {
        'name',
        'from_inventory_id',
        'from_qty',
        'from_qty_unit',
        'returned_by',
        'reason_for_return'
    }

    @classmethod
    def do_activity(cls, args, current_user):
        """
        Do the activity

        :param cls: this class
        :param args: arguments passed to the activity handler from the client
        :type args: dict
        :param current_user: current user object
        """

        cls.check_required_args(args)

        DATABASE.dedicated_connection().begin()
        try:
            received_inventory_object = select_resource_from_db('inventories', args['from_inventory_id'], args['organization_id'])

            if args['from_qty_unit'] == 'seeds':

                seed_weight = received_inventory_object['seed_weight']

                # store the weight of the seeds returned in the activity for HC report
                args['seeds_weight'] = float(args['from_qty'] * seed_weight)

            result = cls.insert_activity_into_db(args)

            return_obj = {
                "activity_id": result["id"],
            }

            if 'from_qty_packages' in args:

                current_qty_packages = received_inventory_object['qty_packages']

                current_qty_packages = current_qty_packages - args['from_qty_packages']

                update_db_result = update_into_db('inventories', args['from_inventory_id'], {'qty_packages': current_qty_packages})

                return_obj['affected_rows'] = update_db_result['affected_rows']

            DATABASE.dedicated_connection().commit()

            return return_obj

        except(psycopg2.Error, psycopg2.Warning, psycopg2.ProgrammingError) as error:              
            DATABASE.dedicated_connection().rollback()
            raise ClientBadRequest(
            {
                "code": "received_inventory_return_items_error",
                "message": "There was an error returning received inventory. "+error.args[0]
            }, 500)
